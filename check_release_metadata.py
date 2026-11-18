#!/usr/bin/env python3
# (c) 2026 William J. Dwyer. MIT License.
"""One release, one version string, one citation — checked, not remembered.

This repository ships the same object twice, in two languages, with the version
written in seven places and the citation in three. Nothing but habit keeps them
in step, and habit has already failed once here: the README advertised
`install.packages("tracegamma")` for a package that is not on CRAN, and it took
a human reading it to notice.

Checks, each of which has a declared failure mode:

  V1  the version string is identical in all seven files that carry it. A
      Python package claiming 0.1.1 beside an R package claiming 0.1.0 is two
      different releases wearing one name, and the shared parity fixture then
      certifies nothing.
  V2  the three CITATION.cff are byte-identical. They are one file maintained
      in three places so that each half of the repository is independently
      citable; if they drift, one of them is wrong and no reader can tell which.
  V3  every CITATION.cff carries the software concept DOI and the paper DOI.
      The concept DOI is the only one that keeps resolving as versions are
      added, so losing it silently breaks every citation of this software.

A fourth check was written and then removed: "the changelog's newest entry
matches the declared version". Its mutation fired, but through V1, not through
itself — the changelog's top heading is one of V1's seven version sources, so a
release whose notes lag is a version disagreement by construction. A check that
can only ever echo another one inflates the count without adding evidence.

Usage:  python3 check_release_metadata.py [repo_root]
Exit:   0 all checks pass, 1 any failure.
"""
import hashlib
import pathlib
import re
import sys

CONCEPT_DOI = "10.5281/zenodo.24354607"   # this software, resolves to latest
PAPER_DOI = "10.5281/zenodo.22060095"     # the paper and its deposit

CFFS = ["CITATION.cff", "python/CITATION.cff", "r/tracegamma/inst/CITATION.cff"]

# file -> regex whose single capture group is the version.
#
# This list was wrong on its first outing. I built it from a grep restricted to
# *.toml, *.cff, DESCRIPTION and *.md, which never looked at a .py file, so
# `__init__.py`'s hardcoded `__version__` was missed and the 0.1.1 wheel shipped
# metadata saying 0.1.1 around a module that reported 0.1.0. It was caught by
# installing the built wheel and asking it, not by reading anything.
#
# DELIBERATELY NOT LISTED: the "generator" stamp in both parity.json files. It
# records which version PRODUCED the fixture — currently 0.1.0, truthfully —
# and is provenance, not a declaration. Bumping it with the release would make
# the fixture claim an ancestry it does not have. It changes only when the
# fixture is regenerated.
VERSION_SOURCES = {
    "python/pyproject.toml": r'^version = "([^"]+)"',
    "python/src/tracegamma/__init__.py": r'^__version__ = "([^"]+)"',
    "r/tracegamma/DESCRIPTION": r"^Version:\s*(\S+)",
    "CITATION.cff": r"^version:\s*(\S+)",
    "python/CITATION.cff": r"^version:\s*(\S+)",
    "r/tracegamma/inst/CITATION.cff": r"^version:\s*(\S+)",
    "python/CHANGELOG.md": r"^## (\S+) —",
    "r/tracegamma/NEWS.md": r"^## (\S+) —",
}


def main(root):
    root = pathlib.Path(root)
    problems = []

    # ---- V1: one version string --------------------------------------------
    found = {}
    for rel, pattern in VERSION_SOURCES.items():
        p = root / rel
        if not p.is_file():
            problems.append("V1: %s does not exist" % rel)
            continue
        m = re.search(pattern, p.read_text(encoding="utf-8"), re.M)
        if not m:
            problems.append(
                "V1: no version found in %s with %r — the file's format changed "
                "and this check is now reading nothing, which would otherwise "
                "pass silently" % (rel, pattern))
            continue
        found[rel] = m.group(1)

    if found and len(set(found.values())) != 1:
        byver = {}
        for rel, v in found.items():
            byver.setdefault(v, []).append(rel)
        problems.append(
            "V1: the version string disagrees across files:\n      " +
            "\n      ".join("%-34s %s" % (v, ", ".join(sorted(f)))
                            for v, f in sorted(byver.items())))
    if len(found) != len(VERSION_SOURCES):
        problems.append("V1: only %d of %d version sources were read; a missing "
                        "source cannot be compared" % (len(found), len(VERSION_SOURCES)))

    version = sorted(found.values())[0] if found else None

    # ---- V2: the three CITATION.cff are one file ---------------------------
    digests = {}
    for rel in CFFS:
        p = root / rel
        if not p.is_file():
            problems.append("V2: %s does not exist" % rel)
            continue
        digests[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    if len(digests) == len(CFFS) and len(set(digests.values())) != 1:
        problems.append(
            "V2: the three CITATION.cff differ:\n      " +
            "\n      ".join("%s  %s" % (d[:16], f) for f, d in sorted(digests.items())))

    # ---- V3: both DOIs present in every citation file ----------------------
    for rel in CFFS:
        p = root / rel
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8")
        if CONCEPT_DOI not in t:
            problems.append("V3: %s has lost the software concept DOI %s — every "
                            "citation of this software depends on it"
                            % (rel, CONCEPT_DOI))
        if PAPER_DOI not in t:
            problems.append("V3: %s no longer cites the paper %s" % (rel, PAPER_DOI))

    if problems:
        print("FAIL: release metadata is inconsistent.")
        for p in problems:
            print("  - %s" % p)
        return 1

    print("PASS: version %s in all %d files; the three CITATION.cff are "
          "identical and carry both DOIs; both changelogs lead with %s."
          % (version, len(VERSION_SOURCES), version))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else
                  pathlib.Path(__file__).resolve().parent))
