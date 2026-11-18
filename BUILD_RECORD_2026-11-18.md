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
