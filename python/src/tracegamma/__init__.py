# (c) 2026 William J. Dwyer. MIT License.
r"""tracegamma -- the three-cumulant calibrated reference for quadratic-form tests.

The trace-gamma is the closed-form shifted, scaled chi-square matched to the
first three cumulants of a quadratic form in near-normal variables. Welch's F is
its two-cumulant member and Pearson's chi-square its equal-eigenvalue member, so
the family *contains* the classical references rather than competing with them.

Quick start
-----------
>>> from tracegamma import TraceGamma
>>> tg = TraceGamma.from_eigs([4.0, 2.0, 1.0, 1.0])
>>> round(tg.cutoff(0.05), 6)
21.249374
>>> tg.branch
'three-cumulant'

Checking the closed form against the exact law:

>>> from tracegamma import imhof_ppf
>>> lam = [4.0, 2.0, 1.0, 1.0]
>>> round(TraceGamma.from_eigs(lam).ppf(0.95) - imhof_ppf(0.95, lam), 4)
0.33

Citation
--------
Dwyer, W. J. (2026). *The trace-gamma distribution: a three-cumulant calibrated
reference for quadratic-form tests, with Welch's F and Pearson's chi-square as
special cases.* Zenodo concept DOI 10.5281/zenodo.22060095.
"""
from .core import (
    SKEW_FLOOR,
    VAR_FLOOR,
    TraceGamma,
    cumulants_from_eigs,
    cumulants_from_traces,
    params_from_power_sums,
    traces_from_quadform,
)
from .exact import imhof_cdf, imhof_ppf, imhof_sf
from .defects import (
    cf_modulus,
    kurtosis_defect,
    rho_ratio,
    standardized_cumulant,
    tail_rate_defect,
)
from .correction import (
    estimate_moments,
    kurtosis_widening,
    marginal_cumulants,
    tracegamma_from_marginal,
)
from .bb import bb_scale_mixture

__version__ = "0.1.1"

__all__ = [
    "TraceGamma",
    "cumulants_from_traces",
    "traces_from_quadform",
    "cumulants_from_eigs",
    "params_from_power_sums",
    "SKEW_FLOOR",
    "VAR_FLOOR",
    "imhof_sf",
    "imhof_cdf",
    "imhof_ppf",
    "kurtosis_defect",
    "tail_rate_defect",
    "standardized_cumulant",
    "rho_ratio",
    "cf_modulus",
    "marginal_cumulants",
    "tracegamma_from_marginal",
    "estimate_moments",
    "kurtosis_widening",
    "bb_scale_mixture",
    "__version__",
]
