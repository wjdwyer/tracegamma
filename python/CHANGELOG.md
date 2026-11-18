# Changelog

## 0.1.1 — 2026-11-18

Metadata only. **No formula, constant or returned value changes**; 0.1.0 and
0.1.1 compute identically.

- **Archived and citable.** Zenodo concept DOI `10.5281/zenodo.24354607`, which always
  resolves to the latest version and is the one to cite. Version 0.1.0 is
  `10.5281/zenodo.24354608`. Both are recorded in `CITATION.cff`.
- **Correction to the 0.1.0 notes.** Those notes said the R package had not
  been executed and that `R CMD check` should be run before relying on it.
  That was true when written and is no longer: `R CMD check --as-cran` passed
  on ubuntu release, ubuntu oldrel-1, macOS and Windows on 2026-11-18, at the
  first attempt. The 0.1.0 text is left as published; this entry supersedes it.
- **A false claim removed from the README.** It advertised
  `install.packages("tracegamma")`. The package is not on CRAN and that line
  should never have shipped. Corrected to install-from-GitHub, with the CRAN
  status stated plainly.
- Supported Python versions are 3.10 through 3.14, tested on Linux, macOS and
  Windows. Unchanged from the published 0.1.0, whose notes did not state it.
- GitHub Actions moved off Node 20 (`checkout@v7`, `setup-python@v7`,
  `upload-artifact@v7`).

## 0.1.0 — 2026-11-18

First release. Ported from the research code deposited with the trace-gamma
paper (Zenodo concept DOI 10.5281/zenodo.22060095).

### Behaviour preserved
- `TraceGamma` / `trace_gamma` fits the three cumulants by the deposited
  formulas, with the deposited skewness floor (1e-6) and variance clamp (1e-12).
- `bb_scale_mixture`, the trace and cumulant helpers, the kurtosis and
  tail-rate defects, and the non-normal correction are unchanged.

### Deliberate departures from the deposited code, each measured
- **The fitted branch is recorded** (`branch`) and a negative third cumulant
  now warns. The deposited module silently took the two-cumulant branch for any
  `k3 <= 0`; the arithmetic is unchanged, the user is told.
- **The exact inversion defaults to a repaired method.** The deposited single
  adaptive quadrature over the half-line is accurate for ten or more
  eigenvalues and unusable below three: measured against the exact oracle, its
  worst relative error is 6.9e-01 at m=1, 1.0e-02 at m=2, 1.1e-03 at m=3,
  falling to 2.3e-10 by m=10. The new panel method stays below 5e-9 throughout.
  The old behaviour remains available as `method="quad"` so the published
  cross-check numbers reproduce exactly.
- `cdf` uses a plain branch where the deposited code used `numpy.where`. Both
  arms of that `where` were algebraically identical, so this changes no value.
- Scalar arguments return plain floats rather than 0-d numpy scalars.

### Known limits
- The panel method costs roughly 0.1 s per evaluation.
- The R package was not executed in the environment where it was written; no R
  interpreter was available there. Run `R CMD check` before relying on it.
