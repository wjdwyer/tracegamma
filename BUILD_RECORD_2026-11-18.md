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
after the matrix is green. *(Done in §9.4. The tooltip named a third action the
annotation text had not: `actions/upload-artifact@v4`.)*

---

## 9. Released, 2026-11-18 — v0.1.0 and v0.1.1 both out

### 9.1 What shipped, and how it was confirmed

| | result | how it was checked |
|---|---|---|
| PyPI | `tracegamma` 0.1.0 live | downloaded from the index on a machine with no access to this tree, installed into a clean venv, and run |
| Zenodo | concept `10.5281/zenodo.24354607`, version `10.5281/zenodo.24354608` | **DataCite** API, not the Zenodo page — both `findable`, concept `HasVersion` → version, version `IsVersionOf` → concept |
| relation | `IsSupplementTo 10.5281/zenodo.22060095`, typed JournalArticle | same DataCite records; the GitHub URL and the ORCID are carried too |
| CI | 15 matrix jobs + build, all green | `python` run #2 |

The installed 0.1.0 returns `cutoff(0.05) = 21.24937381477673` for the spectrum
`(4, 2, 1, 1)` — the value §3 records me inventing twice from memory, now
coming out of a published artifact on someone else's machine.

Trusted publishing worked as designed: no API token exists in this repository
or in its secrets. The pending publisher converted to an ordinary one on first
upload, which is what claims the name.

**One failure worth recording as not-ours.** The first attempt at `python` run
#2 lost one cell with *"The job was not acquired by Runner of type hosted"* and
a run-level internal server error. No checkout, no install, no pytest — the job
never reached a machine. Re-running it was the whole fix. It is recorded so the
history does not later read as flakiness in this package.

### 9.2 Two defects of mine in the v0.1.1 pass

1. **A false claim had been sitting in the public README**: an install line
   reading `install.packages("tracegamma")`. The package is not on CRAN. It was
   not caught by any check — it was caught by reading the file while editing it
   for something else. Corrected to install-from-GitHub with the CRAN status
   stated. Nothing in CI would have found it, which is the point: it is a true
   sentence about a world that does not exist yet.
2. **I shipped a wheel whose metadata and module disagreed.** `pyproject.toml`
   said 0.1.1; `src/tracegamma/__init__.py` still said 0.1.0. My version-source
   list was built from a grep restricted to `*.toml`, `*.cff`, `DESCRIPTION`
   and `*.md` — it never looked at a `.py` file. Caught by installing the built
   wheel and asking the module, rather than reading the metadata I had just
   written. `__init__.py` is now the eighth checked source.

Both are the same shape as §3 and §8.2: a claim written from an incomplete
survey, found only by executing something.

### 9.3 `check_release_metadata.py`, and the check I deleted

Three checks, each with a named failure mode: one version string across all
eight files; the three `CITATION.cff` byte-identical; both DOIs present in each.
Run in the parity workflow. Mutation-tested — it fires on a stale R version, a
diverged citation file, a changed concept DOI, a dropped paper DOI, a lagging
changelog, a renamed version key, and on the `__init__.py` defect above.

A fourth check was written and **removed**: "the changelog's newest entry
matches the declared version". Its mutation fired, but through check V1, not
through itself — the changelog heading is one of V1's own version sources, so a
lagging changelog is a version disagreement by construction. A check that can
only echo another inflates the count without adding evidence.

The patch script that applied this pass (`tg_v011_metadata_patch.py`) refused
twice before writing anything, both times correctly: once because
`setup-python@v5` occurs twice in `python.yml` and I had declared one, and once
because my "no superseded claim survives" scan was reading the changelog's
*description* of the removed CRAN line as the line itself. The second was the
check being too crude — a claim is superseded where a reader would act on it,
not where it is quoted in a correction — and it is now scoped per file.

### 9.4 Node 20

`checkout@v4 → v7`, `setup-python@v5 → v7`, `upload-artifact@v4 → v7`; latest
majors read from each action's release feed, not assumed.
`download-artifact@v4` is **left alone**: it was not named in the deprecation
annotation and I did not verify its current major, so bumping it would be a
guess wearing the same commit message as three measurements.

### 9.5 v0.1.1 released, and what that confirmed

Tagged and released after all three workflows passed on `326c5a2`. Zenodo
version DOI `10.5281/zenodo.24355601`; the concept DOI `10.5281/zenodo.24354607`
now spans both versions and resolves to the newer. Nothing in `CITATION.cff`
needed editing — carrying only the concept DOI is what makes that true, and it
will stay true for every later release.

The wheel PyPI serves was pulled down and run in a clean environment:

| | |
|---|---|
| module `__version__` | 0.1.1 |
| metadata `Version` | 0.1.1 |
| `Requires-Python` | `>=3.10` |
| Deposit URL | `https://doi.org/10.5281/zenodo.24354607` |
| `cutoff(0.05)` on (4,2,1,1) | 21.24937381477673 — **identical to 0.1.0** |

The first two lines agreeing is the §9.2 defect confirmed fixed in the published
artifact, not just locally. The last line tests "metadata only, no behaviour
change" against what users actually download.

**A wrong reading I nearly reported.** The first clean-venv install returned
0.1.0, which looked like PyPI serving stale metadata. It was this machine's pip
cache from installing 0.1.0 an hour earlier. `pip download` had already fetched
the 0.1.1 wheel from the index, which is what settled it. The same caution
applies to anyone checking from a machine that has installed 0.1.0:
`pip install --no-cache-dir --upgrade tracegamma`.

**One `python` cell failed again on macOS**, the third run in a row to lose a
macOS job to the scheduler: queued 15m 36s, never assigned a runner,
`conclusion: cancelled`, zero steps. Re-running it alone took 38 seconds. Across
three runs that is 2 of 15 macOS job attempts lost to infrastructure and none to
a defect in this package. Whether to prune the macOS matrix is an open decision,
not a repair.

### 9.6 Still open

1. ~~`cran-comments.md` is a template.~~ **Closed.** The NOTEs were read: four
   of them, plus one INFO. All five are fixed rather than explained, and
   `R CMD check --as-cran` now reports **`Status: OK`** — run #4 on commit
   `7a6014c`, success on all four configs, the Ubuntu release log read line by
   line. `cran-comments.md` is written against that run and says explicitly
   which log was read, because a NOTE does not fail the job and the other three
   logs were not read.

   Fixing two of the NOTEs required repairing `check_r_package.py` first: its
   `\usage` parser required `)}` adjacent and a bare function name, so a wrapped
   usage and `\method` markup — the two fixes — would have made it skip those
   pages silently. The repair then found three pages (`imhof_cdf`, `imhof_ppf`,
   `imhof_sf`) whose usage had never been checked at all, because the default
   `method = c("panel", "quad")` contains a parenthesis the old pattern could
   not see past. Nine mutations now fire with the right cause; two of my own
   mutations had to be rebuilt, one a `sed` that silently matched nothing and
   one that hit an `\alias` as well as the `\usage`.
2. Dependency floors (`numpy>=1.21`, `scipy>=1.7`) are declared and untested,
   and vacuous at the bottom now that the floor is Python 3.10.
3. §7 item 2 — whether the Imhof defect touches the paper's published
   cross-check — is unchanged and unanswered.
