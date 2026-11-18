# tracegamma (Python)

The **trace-gamma** is the closed-form shifted, scaled chi-square matched to the
first three cumulants of a quadratic form in near-normal variables. Those
cumulants are exact traces of one matrix product (Lancaster's identity), and the
three-moment fit is Solomon and Stephens's. Welch's F is the **two-cumulant
member** of the family and Pearson's chi-square the **equal-eigenvalue member**,
so the family contains the classical references rather than competing with them.

The package also provides the exact generalized chi-square by Imhof inversion,
so the closed form can be checked against the truth rather than against
simulation; the kurtosis and tail-rate defects that govern the error; and an
estimable correction for non-normal inputs.

## Two things worth knowing before you use it

**The two-cumulant branch is requested, not discovered.** The fit falls back to
Satterthwaite's two-moment form when the standardized skewness does not exceed
`1e-6`. No spectrum of positive eigenvalues reaches that in practice: the
skewness is `2*sqrt(2)*p3/p2^1.5`, minimised at equal eigenvalues where it is
`2*sqrt(2)/sqrt(m)`, so `1e-6` would need about 8e12 eigenvalues. You reach the
branch by supplying `k3 = 0` — which is exactly how the paper states the Welch
special case — or a negative `k3`, which is discarded with a warning. Inspect
the fitted object's `branch` to see which fit you have.

**The exact-inversion method matters for small spectra.** `method = "quad"`, the
single adaptive call used in the deposited research code, is accurate for ten or
more eigenvalues and **unusable below three**: measured against the exact oracle
`sum of m unit chi-squares = chi-square on m`, its worst relative error is about
0.69 at m = 1 and 1.0e-2 at m = 2. `method = "panel"`, the default, integrates
between successive zeros and stays below 5e-9 throughout. It is slower. Both are
kept: `"quad"` reproduces the published cross-check numbers exactly.

## Provenance and honest limits

Ported from the research code deposited with the paper (Zenodo concept DOI
`10.5281/zenodo.22060095`). The port changes no formula and no constant; the
Python test suite pins it to the deposited module value for value. Two
departures are deliberate and documented in the source: the fitted branch is
recorded and a negative third cumulant warns, and the exact-inversion default is
the repaired panel method rather than the single quad call.

MIT licensed.

## Install

```
pip install tracegamma
```

## Use

```python
from tracegamma import TraceGamma, imhof_ppf, kurtosis_defect

lam = [4.0, 2.0, 1.0, 1.0]            # eigenvalues of M^{1/2} D M^{1/2}
tg  = TraceGamma.from_eigs(lam)
tg.cutoff(0.05)                        # 21.249374...
tg.branch                              # 'three-cumulant'

imhof_ppf(0.95, lam)                   # 20.919385... the exact quantile
kurtosis_defect(lam)                   # what drives the shoulder error
```

Also `TraceGamma.from_quadform(M, D)` and `TraceGamma(k1, k2, k3)`.

## Test

```
pytest --doctest-modules src/tracegamma tests
```
