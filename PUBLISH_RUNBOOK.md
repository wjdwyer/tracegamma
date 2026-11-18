# Publishing runbook — tracegamma

Everything here is **account-gated**: it needs your GitHub, PyPI, Zenodo and
CRAN credentials. The repository is staged up to the first `git push`; nothing
below has been done for you.

Working directory throughout: the `tracegamma_pkg` folder. A git repository is
already initialised on branch `main` with one commit.

---

## Step 1 — this week

### 1a. Public GitHub repository

Create an empty public repo named **`tracegamma`** (no README, no .gitignore —
this repo already has them), then:

```bash
cd tracegamma_pkg
git remote add origin https://github.com/<you>/tracegamma.git
git push -u origin main
```

**Why today and not later:** JOSS requires the repository to have been public
for **more than six months**, with development spread across that period, before
it will even enter review. The clock starts the day you push. Nothing else on
this page has a deadline; this one does.

### 1b. Confirm CI, and get the R check you could not run locally

Pushing triggers three workflows. Watch the Actions tab:

| workflow | what it proves |
|---|---|
| `python` | tests on 3.9–3.12 across Linux, macOS, Windows; builds and `twine check`s the distributions |
| `R-CMD-check` | **`R CMD check --as-cran` on four platform/version combinations** |
| `cross-language parity` | the two `parity.json` files are byte-identical, and the structural R check passes |

`R-CMD-check` is the one that matters. It is the verification I could not
perform — no R interpreter was available — and it runs for free on push. **Do
not proceed to CRAN until it is green on all four.** Expect to fix something:
the R code has never been executed anywhere.

### 1c. PyPI

Register the name on **TestPyPI first** and install from it before touching the
real index. A bad first release cannot be replaced, only yanked.

```bash
cd python
python -m pip install --upgrade build twine
rm -rf dist && python -m build
twine check dist/*

twine upload --repository testpypi dist/*
python -m pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple tracegamma
python -c "from tracegamma import TraceGamma; print(TraceGamma.from_eigs([4,2,1,1]).cutoff(0.05))"
# expect 21.249373814778...
```

If that prints the right number, upload for real:

```bash
twine upload dist/*
```

Use an API token, not your password. For later releases, switch to PyPI
**trusted publishing** (OIDC from GitHub Actions) so there is no token to store.

### 1d. Zenodo

**Order matters.** Zenodo only captures releases created *after* you enable the
repository.

1. Sign in to Zenodo with GitHub, open **GitHub** in your account settings, and
   flip the switch on `<you>/tracegamma`.
2. Only then create the release:

```bash
git tag -a v0.1.0 -m "tracegamma 0.1.0"
git push origin v0.1.0
```
   Then publish a GitHub Release from that tag.

3. Zenodo mints a **concept DOI** (all versions) and a **version DOI** (v0.1.0).
   `.zenodo.json` in the repo root supplies the metadata, including
   `isSupplementTo` the paper's deposit `10.5281/zenodo.22060095`.
4. Put the concept DOI badge in `README.md` and the DOI in `CITATION.cff` and
   `python/CITATION.cff`, then commit. That change ships in v0.1.1.

After this the software is citable with no journal involved, which was the
point.

---

## Step 2 — CRAN, after the R check is green

CRAN is the one that drives adoption in statistics. It is also a standing
commitment: when a dependency or R itself breaks the package you get a notice
with a deadline, and missing it means archival.

```bash
# locally, in addition to CI
R CMD build r/tracegamma
R CMD check --as-cran tracegamma_0.1.0.tar.gz
```

Then:

1. Fix every ERROR and WARNING. Explain any NOTE in `cran-comments.md`.
2. **Edit `r/tracegamma/cran-comments.md`** — it is a template with placeholders.
   Submitting it unedited is worse than omitting it.
3. Run `devtools::check_win_devel()` and `check_win_release()`.
4. Submit the tarball at <https://cran.r-project.org/submit.html>.
5. Confirm from the maintainer email address in `DESCRIPTION`
   (`wjdwyer@trialdesign.com`) — CRAN sends a confirmation link.

Expect at least one round of comments. Common first-submission requests: single
quotes around software names in `Description`, no `print()` to console in
functions, examples under 5 seconds.

---

## Step 3 — the methods paper (separate track)

Computational Statistics, per the venue analysis in
`mdist_work/TraceGamma_ISR_Rejection_DeepDive_2026-11-18.md` §7.4. Cite the
packages by their Zenodo concept DOI once step 1d has minted it.

Do **not** let a software paper stand in for the methods paper: Proposition 2 is
the one new theorem, and JOSS explicitly will not publish a paper focused on
new research results.

---

## Step 4 — the software paper, mid-2027 at the earliest

JOSS pre-review gates, all of which fail today and none of which can be
shortcut:

- repository public **more than six months**, with commits spread across that
  period — "a repo dump is not a history", and they run automated checks on the
  commit distribution;
- **demonstrated research use**, not aspiration;
- open-source practice indicators: history, tagged releases, changelog, tests,
  CI, `CONTRIBUTING`, stated support expectations — all present in this repo
  from the first commit;
- **iterative development**, refined through use and feedback.

You will also file an **AI usage disclosure**. `AI_DISCLOSURE.md` is drafted and
has a confirmation block that **only you can sign** — read it before you do.
JOSS treats incomplete disclosure as an ethical breach.

If you would rather not wait: **JSS** has no six-month rule, is free, and
carries more weight in statistics, at the cost of a long review.

---

## Order of operations, one line

Push today → CI green → TestPyPI → PyPI → Zenodo switch on → tag → DOI → badge →
`R CMD check` clean → CRAN → methods paper → (mid-2027) JOSS or JSS.
