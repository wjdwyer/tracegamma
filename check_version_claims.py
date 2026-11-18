#!/usr/bin/env python3
# (c) 2026 William J. Dwyer. MIT License.
"""The Python versions this package CLAIMS must be the ones CI actually runs.

Two files make the claim independently:

  python/pyproject.toml        "Programming Language :: Python :: X.Y" classifiers,
                               which is what PyPI displays to a prospective user
  .github/workflows/python.yml the test matrix, which is what is actually executed

Nothing keeps them in step except a comment, and a comment is not a check. This
script fails if they disagree, and fails if either set is empty -- an empty set
would otherwise make the comparison trivially true, which is the failure shape
this project has hit before (a PASS reported over zero checks).

It deliberately does not import a YAML parser: PyYAML reads a bare `on:` key as
the boolean True (YAML 1.1), so a YAML-aware check of these files has already
produced one false failure here. The matrix line is matched literally instead,
and the script fails if that line is not found exactly once.

Usage:  python3 check_version_claims.py [repo_root]
Exit:   0 agreement, 1 disagreement or a malformed input.
"""
import pathlib
import re
import sys

VERSION = re.compile(r'"(\d+\.\d+)"')


def claimed_by_pyproject(path):
    """The X.Y of every per-version classifier, in file order."""
    found = re.findall(r'"Programming Language :: Python :: (\d+\.\d+)"',
                       path.read_text(encoding="utf-8"))
    return found


def run_by_workflow(path):
    """The X.Y of every entry on the matrix's `python:` list."""
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines()
             if re.match(r"\s*python:\s*\[", ln)]
    if len(lines) != 1:
        raise ValueError(
            "expected exactly one matrix line matching `python: [...]` in %s, "
            "found %d -- the workflow was restructured and this check is now "
            "reading the wrong thing" % (path.name, len(lines)))
    inside = lines[0].split("[", 1)[1].rsplit("]", 1)[0]
    return VERSION.findall(inside)


def main(root):
    root = pathlib.Path(root)
    pyproject = root / "python" / "pyproject.toml"
    workflow = root / ".github" / "workflows" / "python.yml"
    for p in (pyproject, workflow):
        if not p.is_file():
            print("FAIL: %s does not exist" % p)
            return 1

    try:
        claimed = claimed_by_pyproject(pyproject)
        tested = run_by_workflow(workflow)
    except ValueError as exc:
        print("FAIL: %s" % exc)
        return 1

    problems = []
    if not claimed:
        problems.append(
            "pyproject.toml declares no per-version Python classifier, so this "
            "check would pass over nothing. Add one classifier per tested version.")
    if not tested:
        problems.append(
            "the python.yml matrix lists no Python version, so nothing is tested.")

    missing_claim = sorted(set(tested) - set(claimed), key=float)
    missing_test = sorted(set(claimed) - set(tested), key=float)
    if missing_claim:
        problems.append(
            "tested but not claimed: %s -- CI runs these, so pyproject.toml "
            "should say so (add the classifier)." % ", ".join(missing_claim))
    if missing_test:
        problems.append(
            "claimed but not tested: %s -- pyproject.toml tells PyPI the package "
            "supports these and nothing verifies it (add the matrix cell, or "
            "drop the classifier)." % ", ".join(missing_test))

    if problems:
        print("FAIL: the version claims and the test matrix disagree.")
        for p in problems:
            print("  - %s" % p)
        print("\n  classifiers: %s\n  matrix:      %s"
              % (", ".join(claimed) or "(none)", ", ".join(tested) or "(none)"))
        return 1

    print("PASS: %d versions, claimed and tested: %s"
          % (len(tested), ", ".join(sorted(tested, key=float))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else
                  pathlib.Path(__file__).resolve().parent))
