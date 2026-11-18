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
    for p in sorted((R / "man").glob("*.Rd")):
        t = p.read_text()
        m = re.search(r"\\usage\{([A-Za-z._][A-Za-z0-9._]*)\(([^)]*)\)\}", t, re.S)
        if not m:
            continue
        fn, usage_args = m.group(1), m.group(2)
        d = re.search(r"^%s\s*<-\s*function\s*\(" % re.escape(fn), src, re.M)
        if not d:
            continue
        depth, j, buf = 0, d.end() - 1, ""
        while j < len(src):
            buf += src[j]
            depth += (src[j] == "(") - (src[j] == ")")
            if depth == 0:
                break
            j += 1
        real = [a.split("=")[0].strip() for a in re.sub(r"\s+", " ", buf[1:-1]).split(",") if a.strip()]
        used = [a.split("=")[0].strip() for a in re.sub(r"\s+", " ", usage_args).split(",") if a.strip()]
        if real != used:
            fail.append("%s.Rd usage %s does not match the signature %s" % (fn, used, real))
        documented = set(re.findall(r"\\item\{([^}]+)\}", t))
        for a in real:
            if a not in documented and a != "...":
                fail.append("%s.Rd does not document argument '%s'" % (fn, a))

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
