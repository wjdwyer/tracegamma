# tracegamma packages — build record, 2026-11-18

Two installable, documented packages built from the author's research tree,
under the scope elected by the project owner: **everything in that tree**, package name **`tracegamma`** in both ecosystems.

Until now the implementation was a research module and an HTML demonstrator,
not a package anyone could install, which ruled out the software-journal route.
The library half of that is now done; §7 below lists what is still missing
before a software submission.

---

## 1. What was built

| | Python | R |
|---|---|---|
| name | `tracegamma` 0.1.0 | `tracegamma` 0.1.0 |
| layout | `src/` layout, `pyproject.toml` | CRAN layout, `DESCRIPTION`/`NAMESPACE` |
| public symbols | 21 | 29 exports |
| docs | numpydoc docstrings + doctests | 29 `man/*.Rd` |
| tests | 99 passing (pytest + doctests) | 2 testthat files, **not executed** (§6) |
| artifacts | wheel + sdist built, installs, imports | source tree, structurally checked |

**Scope honoured without misrepresentation.** The owner chose "everything in the research tree". The library-grade code is the public API: the distribution and
its three constructors, the trace/cumulant helpers, the closed forms, the exact
Imhof inversion, the two defects, the standardized cumulants, the non-normal
correction, and the Berger-Boos dilation. The simulation drivers
(`qgamma_grid.py`, `qgamma_stress_grid.py`, `qgamma_experiments.py`) and the
validation suites are research scripts; they were **not** promoted to a stable
interface, because they were never written to be one. `bb.py` carries an
explicit scope warning that the statistic belongs to a different paper.

---

## 2. Three findings in the deposited code, each measured before it was claimed

### F1 — the Welch fallback is unreachable from eigenvalues, and silent

`TraceGamma.__init__` takes the two-cumulant branch when
`gamma1 = k3/k2^1.5 <= 1e-6`. For a spectrum of **positive** eigenvalues that
cannot happen: `gamma1 = 2*sqrt(2)*p3/p2^1.5`, minimised at equal eigenvalues at
`2*sqrt(2)/sqrt(m)`, so reaching `1e-6` would take about **8e12** eigenvalues.
The branch is reached only by supplying `k3 = 0` — which is exactly how the
paper states Proposition 1 — or a **negative** `k3`, which an indefinite `M` can
produce. In that case the deposited module **silently discards the third
cumulant** and returns the two-cumulant answer with no indication.

Not a numerical error: the arithmetic is right. It is an interface defect. Both
packages now record `branch` and warn on negative `k3`; no value changed.

### F2 — the `numpy.where` in the deposited `cdf` was a no-op

Verified algebraically and numerically: `(b - x)/(-a)` equals `(x - b)/a` for
every `a != 0`, so both arms of the `where` computed the same number, and `a` is
a scalar so it was never selecting elementwise either. Replaced by a plain
branch; `tests/test_deposited.py` asserts the two arms are identical.

**A hypothesis I had to withdraw.** I first expected `a < 0` to produce a wrong
CDF. Measurement refuted it: `a < 0` is unreachable, because negative skew sends
the fit to the Welch branch where `a = k2/(2*k1) > 0`. The round-trip
`cdf(ppf(q)) = q` holds to 3e-16 and the CDF is monotone in every case tested.
The deposited module is correct on everything it actually computes.

### F3 — the exact-inversion routine is unusable for small spectra

This is the substantive one, because **Imhof is the paper's ground truth** for
its accuracy claims. Measured against an exact oracle — `m` unit eigenvalues
give exactly `chi^2_m`, so the answer is known in closed form — the deposited
single `quad` call over `[0, inf)` has worst relative error:

| m | deposited `quad` | repaired `panel` |
|---|---|---|
| 1 | **6.9e-01** | < 5e-09 |
| 2 | **1.0e-02** | < 5e-09 |
| 3 | 1.1e-03 | < 5e-09 |
| 5 | 2.3e-06 | < 5e-09 |
| 10 | 2.3e-10 | < 5e-09 |
| 20 | 7.1e-12 | < 5e-09 |

Cause: the integrand decays like `u^-(1+m/2)` and oscillates with period
`4*pi/x`, so for few eigenvalues the adaptive rule cannot resolve the tail. It
returns a poor answer while reporting only a subdivision warning, which the
deposited code never surfaced.

**Tolerance was not the problem.** Tightening from 1e-9 to 1e-12 moved the m=1
error from 1.4e-03 to 6.9e-04. The paper's own spectra have m >= 4, where the
error is 1e-6 or better, so **the published cross-check is probably
unaffected** — but that should be checked against the actual figures rather
than assumed, and it is listed as open in §7.

Both methods ship. `method="quad"` reproduces the published numbers exactly;
`method="panel"` is the default because a package is called with inputs its
author did not choose.

---

## 3. Two defects of my own, in the repair

Recorded because they are the reason the measurement discipline exists.

1. **I invented a doctest value.** I wrote `cutoff(0.05) == 19.552637` from
   intuition rather than computing it. The real value is **21.249374**. Caught
   by running the doctests. Every numeric literal in the documentation is now
   computed output, not recollection.
2. **I fixed the panel method twice, wrongly, before measuring.** My first
   diagnosis of the small-`x` failure was slow decay; I added a *linear*
   subdivision, which was far too slow and did not fix it. Instrumenting showed
   the real cause: the integrand's mass sits near `u ~ 1/max(lam)` while the
   first panel spans `2*pi/x`, so for small `x` the adaptive rule samples only
   the empty part and returns ~0 — giving `sf = 0.5` for every small `x`.
   **Geometric** subdivision fixed it. The comment in both `exact.py` and
   `exact.R` records that linear subdivision was tried and failed, so nobody
   repeats it.

---

## 4. Identities that hold, and are tested as identities

- `a = p3/p2`, `nu = p2^3/p3^2`, `b = p1 - p2^2/p3` equals the cumulant fit to
  **1.5e-15** across eight designed spectra. Two routes, each the other's oracle.
- Lancaster: `kappa_r = 2^(r-1)(r-1)! t_r` at r = 1, 2, 3.
- Traces of a diagonal form are the eigenvalue power sums.
- Pearson exactly: `m` unit eigenvalues reproduce `chi^2_m` to 1e-14 in the CDF,
  not approximately.
- The non-normal correction at the normal values `mu4=3, mu6=15` returns exactly
  the Gaussian cumulants `(m, 2m, 8m)`.
- `tests/test_deposited.py` pins the Python port to the deposited module
  **bit for bit** on parameters, and by exact array equality on ppf/cdf/pdf.

---

## 5. Cross-language parity

`parity.json` — 8 spectra x 9 quantiles plus parameters, branch, closed forms,
cumulants, cutoffs, both defects, two standardized cumulants, the exact Imhof
survival at each 5% cutoff, the Welch branch, the marginal cumulants and three
Berger-Boos dilations — is generated by the Python package and shipped in both.
`tests/testthat/test-parity.R` checks the R port against it. The two
implementations therefore cannot drift apart silently.

---

## 6. What was verified, and what was not

**Verified by execution here:**
- Python: 99 tests pass (unit, identity, exact-method envelope, deposited-module
  pin, doctests). Wheel and sdist build; the wheel installs; the installed
  package imports and runs from outside the source tree.
- The exact-method accuracy table is pinned by a test that also asserts `quad`
  is *still inaccurate* at m <= 3 — if that stops being true the table is stale
  and the test says so.

**Not verified here: the R package was never executed.** No R interpreter was
available and none could be installed (no root, no conda). `check_r_package.py`
checks file layout, NAMESPACE/definition/help-page agreement, usage lines
against real signatures, documented arguments, bracket and quote balance, and
fixture validity — **PASS, 0 failures**, and the checker itself is
mutation-tested **8/8**: it fires on an export with no definition, a usage line
disagreeing with its signature, an undocumented argument, unbalanced braces, a
missing fixture and a missing DESCRIPTION, and stays quiet on the restored
package.

That is structure, not behaviour. It cannot run the code, the examples or the
testthat suite. **`R CMD check` must be run before the R package is relied on**,
and the README says so in those words.

---

## 7. Open, before this becomes a software submission

1. **Run `R CMD check`** on a machine with R, plus the testthat suite against
   the parity fixture. Nothing here substitutes for it.
2. **Check whether F3 touches the published cross-check.** The paper's spectra
   look large enough to be unaffected, but that is an inference, not a
   measurement; re-run the figure against `method="panel"` and compare.
3. Decide whether the manuscript should cite the packages, and whether the
   exact-inversion repair belongs in the paper as a correction.
4. Research scripts ship as scripts. If a JSS submission is the target, they
   need either promotion to a documented interface or explicit exclusion.
5. Neither package is published to PyPI or CRAN. The names are unclaimed.

---

## 8. First CI run, 2026-11-18 (commit `67497b3`)

The repository was made public and three workflows ran. This section records
what that execution actually established, because §6 above was written when
nothing had been executed outside one sandbox.

### 8.1 `R CMD check` passed on all four platforms — item 1 of §7 is closed

`R-CMD-check` run #1, conclusion **success**, 15m 13s: `R CMD check --as-cran
--no-manual` plus the testthat suite against `parity.json`, on ubuntu release,
ubuntu oldrel-1, macOS release and Windows release, with `fail-fast: false` so
each is an independent result.

**This is the first time the R code has been executed anywhere.** §6 said the
structural checker proves layout and agreement, not behaviour, and that
`R CMD check` had to be run before the package was relied on. It has been, and
it is clean on four platforms at the first attempt. The structural checker is
corroborated rather than superseded: it still catches the classes it was built
for before a push costs fifteen minutes.

`cross-language parity` also passed (1m 32s), confirming on a clean runner that
the two `parity.json` files are byte-identical and that `check_r_package.py`
reports PASS away from the machine that wrote it.

### 8.2 The `python` workflow failed in one cell of thirteen, and not for a
reason in this package

Twelve of thirteen jobs passed: every macOS and Windows cell including 3.9,
three of four Linux cells, and `build and check distributions`. The single
failure was **`pytest 3.9 on ubuntu-latest`**, at the `actions/setup-python`
step — *before* installation, so no line of `tracegamma` ran. The run's failure
annotation, quoted exactly:

> The version '3.9' with architecture 'x64' was not found for Ubuntu 26.04.

`ubuntu-latest` migrated to Ubuntu 26.04 on 19 October 2026, and
`actions/python-versions` publishes no 3.9 build for that image. Python 3.9 has
been end-of-life since October 2025.

**This was my defect, not GitHub's.** I wrote a matrix cell for an interpreter
I never checked could be provisioned, and `requires-python = ">=3.9"` asserted a
support surface on that basis. The same shape as the other errors in §3: a claim
made from recollection and shipped without the one measurement that would have
settled it.

### 8.3 What was measured before deciding, and what it showed

Dependency resolution under each interpreter, by `pip install --dry-run` against
the real index, not from memory:

| interpreter | resolves to |
|---|---|
| cp39 | numpy 2.0.2, scipy 1.13.1 |
| cp313 | numpy 2.2.6, scipy 1.16.3 |
| cp314 | numpy 2.5.5, scipy 1.18.1 |

So the 3.9 cell was not testing a stack any new user installs: numpy requires
3.10+ from 2.1 onward, and the cell silently pinned dependencies more than two
years old. Dropping 3.9 removes a cell that could not run and was testing the
wrong thing when it could.

**A probe artifact I had to correct.** My first cp314 probe reported *no numpy
wheel at all*, and the obvious reading was that 3.14 is not yet supported. It
was my probe: I had offered only `manylinux2014`/`manylinux_2_17` platform tags,
and the cp314 wheels are tagged `manylinux_2_27`/`manylinux_2_28`. Re-running
with those tags returned the wheels above. The absence was in my predicate, not
on the index — the fourth time in this project that a measurement failure has
looked like a finding.

### 8.4 The change

- matrix `["3.9","3.10","3.11","3.12"]` → `["3.10","3.11","3.12","3.13","3.14"]`;
  12 test cells become 15, each one provisionable and each one on a current
  dependency stack
- `requires-python = ">=3.9"` → `">=3.10"`
- one `Programming Language :: Python :: X.Y` classifier per tested version, so
  what PyPI advertises is exactly what CI runs
- `check_version_claims.py`, new, run in the `build` job: it fails if the
  classifiers and the matrix disagree, **and fails if either list is empty**, so
  it cannot report a pass over nothing. Mutation-tested 9/9 — it fires on a
  deleted classifier, a deleted matrix entry, all classifiers removed, an
  emptied matrix, a duplicated or renamed matrix line, a missing
  `pyproject.toml`, and on 3.9 being reintroduced into the matrix alone; it
  stays quiet on the unmodified repository. It does not import a YAML parser,
  because PyYAML reads the workflow's bare `on:` key as the boolean `True`
  (YAML 1.1) and that has already produced one false failure here.

Dependency floors (`numpy>=1.21`, `scipy>=1.7`) were left alone. They are now
vacuous at the bottom — scipy 1.7 does not support 3.10 — but they are not
false, and nothing in CI tests the floor on any interpreter. **Open:** either
raise them to the oldest versions that actually install under 3.10 and test that
cell, or state that only current dependencies are supported.

**Also open, non-blocking:** every run carries a warning that
`actions/checkout@v4` and `actions/setup-python@v5` target Node.js 20 and are
being forced onto Node.js 24. They work today. The bump is deliberately held
back so that this commit changes one variable; it should be a separate commit
after the matrix is green.
