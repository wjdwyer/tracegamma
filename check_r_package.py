#!/usr/bin/env python3
# (c) 2026 William J. Dwyer. MIT License.
"""Structural check of the R package, for environments with no R.

R is not installed in the build sandbox, so `R CMD check` could not be run
there. This checks what can be checked without an R interpreter: that the
package has the files CRAN requires, that every NAMESPACE export has both a
definition and a help page, that every help page documents something exported,
that the usage line matches the real signature, and that braces, parentheses
and quotes balance in every source file.

It is NOT a substitute for `R CMD check`. It cannot run the code, evaluate the
examples, or execute the testthat suite. Run `R CMD check` before any release.
"""
import re, sys, pathlib, json


def _braced(text, macro):
    r"""The contents of \macro{...}, balancing nested braces.

    Needed because \usage{\method{print}{trace_gamma}(x, ...)} contains braces
    inside the body; a non-greedy regex stops at the first closing one and
    hands back `\method{print`.
    """
    i = text.find("\\" + macro + "{")
    if i < 0:
        return None
    j, depth, out = i + len(macro) + 2, 1, []
    while j < len(text) and depth:
        depth += (text[j] == "{") - (text[j] == "}")
        if depth:
            out.append(text[j])
        j += 1
    return "".join(out) if depth == 0 else None


def _parens(text, i):
    """The text inside the parentheses that open at or after index i."""
    i = text.find("(", i)
    if i < 0:
        return None
    j, depth, out = i, 0, []
    while j < len(text):
        depth += (text[j] == "(") - (text[j] == ")")
        if depth == 0:
            return "".join(out[1:])
        out.append(text[j])
        j += 1
    return None


def _argsplit(argstr):
    """Whole arguments, split on top-level commas only."""
    out, depth, buf = [], 0, ""
    for c in argstr:
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        if c == "," and depth == 0:
            out.append(buf)
            buf = ""
        else:
            buf += c
    out.append(buf)
    return [a for a in out if a.strip()]


def _argnames(argstr):
    """Argument NAMES, splitting on top-level commas only.

    A default value can contain both commas and parentheses --
    `method = c("panel", "quad")` is the live example, on three help pages.
    Splitting on every comma invents an argument called '"quad"'; the earlier
    version of this checker instead used a regex that stopped at the first
    ')', which made the whole \\usage unmatchable and silently skipped those
    three pages. Neither failure was visible in the output.
    """
    return [a.split("=")[0].strip() for a in _argsplit(argstr)]


def main(root):
    R = pathlib.Path(root)
    fail, info = [], []

    # --- required files ---
    for rel in ("DESCRIPTION", "NAMESPACE", "LICENSE", "R", "man", "tests/testthat.R"):
        if not (R / rel).exists():
            fail.append("missing required path: %s" % rel)

    desc = (R / "DESCRIPTION").read_text() if (R / "DESCRIPTION").exists() else ""
    for field in ("Package:", "Version:", "Title:", "Description:", "License:", "Authors@R:"):
        if field not in desc:
            fail.append("DESCRIPTION lacks %s" % field)

    # --- exports vs definitions vs help pages ---
    ns = (R / "NAMESPACE").read_text() if (R / "NAMESPACE").exists() else ""
    exports = set(re.findall(r"^export\(([^)]+)\)", ns, re.M))
    s3 = set(re.findall(r"^S3method\(([^,]+),\s*([^)]+)\)", ns, re.M))
    src = "\n".join(p.read_text() for p in sorted((R / "R").glob("*.R")))
    defined = set(re.findall(r"^([A-Za-z._][A-Za-z0-9._]*)\s*<-", src, re.M))
    rd = {p.stem for p in (R / "man").glob("*.Rd")}
    rd_aliases = set()
    for p in (R / "man").glob("*.Rd"):
        rd_aliases |= set(re.findall(r"\\alias\{([^}]+)\}", p.read_text()))

    for e in sorted(exports - defined):
        fail.append("NAMESPACE exports %s but no R/ file defines it" % e)
    for e in sorted(exports - rd_aliases):
        fail.append("exported %s has no help page (\\alias) in man/" % e)
    roxy_exported = set()
    for blk in re.finditer(r"((?:^#'.*\n)+)\s*([A-Za-z._][A-Za-z0-9._]*)\s*<-", src, re.M):
        if "@export" in blk.group(1) and not blk.group(2).startswith("."):
            roxy_exported.add(blk.group(2))
    for e in sorted(roxy_exported - exports - {"%s.%s" % (g, c) for g, c in s3}):
        if e not in {m for _, m in s3} and not any(e.startswith(g + ".") for g, _ in s3):
            fail.append("R/ marks %s @export but NAMESPACE does not export it" % e)
    for a in sorted(rd_aliases - exports - defined):
        info.append("help page documents %s, which is neither exported nor defined" % a)

    # --- usage lines must match the real signature ---
    #
    # The usage body is extracted by balancing braces, not by regex. The old
    # pattern required `)}` adjacent and a bare function name, so it could not
    # read either of the two forms `R CMD check --as-cran` actually asks for:
    # a \usage wrapped across lines (to stay under 90 characters) or the
    # \method{generic}{class} markup required for S3 methods. It did not fail
    # on them -- it SKIPPED the file, silently, which would have switched this
    # check off for exactly the pages being edited.
    rd_usage_checked, rd_usage_novalue = 0, 0
    for p in sorted((R / "man").glob("*.Rd")):
        t = p.read_text()
        body = _braced(t, "usage")
        if body is None:
            continue                       # no \usage section at all
        body = body.strip()
        if "(" not in body:
            # A data page's \usage lists the object names it documents, one per
            # line -- NORMAL_MU4.Rd legitimately lists two. So the test is not
            # "exactly one identifier" (that was too strict and fired on a
            # correct page); it is that every name listed is one this page
            # actually documents. A mangled \usage fails that, instead of being
            # waved through as "just a constant", which is how it would escape
            # both this check and notice.
            page_aliases = set(re.findall(r"\\alias\{([^}]+)\}", t))
            stray = [w for w in body.split() if w not in page_aliases]
            if stray:
                fail.append("%s: \\usage{%s} has no call, and %s %s not among the "
                            "names this page documents (%s)"
                            % (p.name, " ".join(body.split())[:60],
                               ", ".join(stray[:4]), "is" if len(stray) == 1 else "are",
                               ", ".join(sorted(page_aliases)) or "none"))
            else:
                rd_usage_novalue += 1
            continue
        m = re.match(r"\\method\{([A-Za-z._][A-Za-z0-9._]*)\}"
                     r"\{([A-Za-z._][A-Za-z0-9._]*)\}\s*\(", body)
        if m:
            fn = "%s.%s" % (m.group(1), m.group(2))
        else:
            m = re.match(r"([A-Za-z._][A-Za-z0-9._]*)\s*\(", body)
            fn = m.group(1) if m else None
        usage_args = _parens(body, m.end() - 1) if m else None
        if fn is None or usage_args is None:
            fail.append(
                "%s: this checker cannot parse the \\usage section %r. It is "
                "reported rather than skipped: skipping would turn the "
                "signature and argument checks off for this page without "
                "saying so." % (p.name, " ".join(body.split())[:120]))
            continue
        d = re.search(r"^%s\s*<-\s*function\s*\(" % re.escape(fn), src, re.M)
        if not d:
            fail.append("%s documents \\usage for %s(), which is defined nowhere "
                        "in R/" % (p.name, fn))
            continue
        rd_usage_checked += 1
        real_src = _parens(src, d.end() - 1) or ""
        real, used = _argnames(real_src), _argnames(usage_args)
        if real != used:
            fail.append("%s.Rd usage %s does not match the signature %s" % (fn, used, real))
        else:
            # Names agreeing is not enough: a documented DEFAULT that the code
            # does not use sends the reader to the wrong behaviour, and the
            # names-only comparison cannot see it. Compared on normalised
            # whitespace, because a \usage wrapped to stay under 90 characters
            # carries newlines and indentation the source does not.
            norm = lambda s: [" ".join(a.split()) for a in _argsplit(s)]
            if norm(real_src) != norm(usage_args):
                fail.append("%s.Rd documents defaults the signature does not "
                            "have:\n        documented %s\n        actual     %s"
                            % (fn, norm(usage_args), norm(real_src)))
        documented = set(re.findall(r"\\item\{([^}]+)\}", t))
        for a in real:
            if a not in documented and a != "...":
                fail.append("%s.Rd does not document argument '%s'" % (fn, a))

    if rd_usage_checked == 0:
        fail.append("no help page had its \\usage compared against a real "
                    "signature. The usage check would report PASS having "
                    "examined nothing, which is the failure shape this project "
                    "has hit before.")
    else:
        info.append("usage checked against the real signature on %d help pages "
                    "(%d more document a constant and have no arguments)"
                    % (rd_usage_checked, rd_usage_novalue))

    # --- balance of braces/parens/quotes per file ---
    for p in sorted(list((R / "R").glob("*.R")) + list((R / "tests").rglob("*.R"))):
        t = p.read_text()
        stripped = re.sub(r'"(?:[^"\\]|\\.)*"', '""', re.sub(r"'(?:[^'\\]|\\.)*'", "''", t))
        stripped = re.sub(r"#.*", "", stripped)
        for open_c, close_c in (("{", "}"), ("(", ")"), ("[", "]")):
            if stripped.count(open_c) != stripped.count(close_c):
                fail.append("%s: unbalanced %s%s (%d vs %d)" % (
                    p.name, open_c, close_c, stripped.count(open_c), stripped.count(close_c)))
        if t.count('"') % 2:
            fail.append("%s: odd number of double quotes" % p.name)

    # --- the parity fixture must be present and parseable ---
    fx = R / "inst" / "parity" / "parity.json"
    if not fx.exists():
        fail.append("parity fixture missing at inst/parity/parity.json")
    else:
        try:
            j = json.loads(fx.read_text())
            info.append("parity fixture: %d cases, generator %r" % (len(j["cases"]), j["generator"]))
        except Exception as e:
            fail.append("parity fixture is not valid JSON: %s" % e)

    print("R PACKAGE STRUCTURAL CHECK -- %s" % R)
    print("  exports: %d | definitions: %d | help pages: %d | aliases: %d"
          % (len(exports), len(defined), len(rd), len(rd_aliases)))
    for i in info:
        print("  info  %s" % i)
    for f in fail:
        print("  FAIL  %s" % f)
    print("\n%s: %d failure(s)" % ("FAIL" if fail else "PASS", len(fail)))
    print("NOT CHECKED HERE (no R interpreter): code execution, examples, testthat suite,")
    print("R CMD check. Run `R CMD check` on a machine with R before release.")
    return 1 if fail else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
