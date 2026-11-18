# AI usage disclosure

Written at build time rather than reconstructed later, because a disclosure
assembled from memory months afterwards is not a disclosure.

The Journal of Open Source Software requires this statement at submission and
treats incomplete disclosure as an ethical breach. Other venues are moving the
same way. The form below follows the JOSS policy headings.

## Tools used

- **Claude (Anthropic), Opus 5**, via the Claude desktop application, on
  **2026-11-18**.

## Nature and scope of assistance

Used for:

- **Code generation.** First drafts of both packages, ported from the author's
  existing research modules in the `m_series` tree (`mseries_qgamma.py`,
  `qgamma_imhof.py`, `qgamma_cumulant_correction.py`,
  `tracegamma_tailbound_minimal.py`, `verify_m1_m2.py`).
- **Test authoring.** The pytest and testthat suites, the cross-language parity
  fixture generator, and the R structural checker `check_r_package.py`.
- **Documentation.** Docstrings, `man/*.Rd` (generated from roxygen comments by
  script, since roxygen2 was unavailable), READMEs, CHANGELOG.
- **Numerical investigation.** Measuring the deposited code against exact
  oracles, which is how the three findings in `BUILD_RECORD_2026-11-18.md`
  were located, and designing the repaired panel quadrature.

Not used for: the underlying mathematics. The trace-gamma object, the
cumulant-trace construction, the closed forms, the two defects, the deflation
invariant and the Berger-Boos scale mixture are the author's prior work,
published in the manuscript and deposited at Zenodo concept DOI
10.5281/zenodo.22060095, and predate any of this assistance.

## Confirmation of review

> **To be completed and signed by the author before any submission that
> requires this statement. Do not submit it unread — it asserts something only
> you can assert.**

The human author confirms that he has reviewed, edited and validated all
AI-assisted output, and made the core design decisions, including:

- [ ] the public API surface and what was deliberately excluded from it
- [ ] the decision to preserve the deposited numerics exactly, and each
      documented departure from them
- [ ] the three findings in `BUILD_RECORD_2026-11-18.md` and their dispositions
- [ ] the test suites, including that each check can fail
- [ ] the accuracy claims, each traced to a measurement against a known-exact
      reference

Signed: ______________________  Date: ____________

## Known limits of the assistance

- The R package was **never executed**: no R interpreter was available in the
  build environment. It was checked structurally only.
- Two defects introduced by the assistant during the build were caught and are
  recorded in `BUILD_RECORD_2026-11-18.md` §3: an invented documentation value,
  and two wrong diagnoses of a quadrature failure before it was measured
  properly. They are recorded rather than quietly removed because they bear on
  how much unreviewed output should be trusted.
