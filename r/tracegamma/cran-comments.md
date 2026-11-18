## Test environments

<!-- Fill in from the actual runs before submitting. Do not submit this
     unedited: CRAN reads it, and a template is worse than nothing. -->

* local macOS, R <version>
* GitHub Actions: ubuntu-latest (release, oldrel-1), macos-latest, windows-latest
* win-builder (devel and release)

## R CMD check results

0 errors | 0 warnings | 0 notes

<!-- If there is a NOTE, state it and why it is acceptable. The usual one for a
     first submission is:

     * This is a new release.
-->

## Notes for the reviewer

This is a new submission.

The package implements the trace-gamma reference distribution for quadratic-form
test statistics, with Welch's F and Pearson's chi-square as special cases, and
the exact generalized chi-square by Imhof (1961) inversion for comparison. A
companion Python implementation exists; a shared fixture
(`inst/parity/parity.json`) is used by the test suite to check the two against
each other.

Examples and tests run in a few seconds. `imhof_sf(method = "panel")` is the
accurate but slower exact inversion; it is not used in any example in a way that
would make checks slow.
