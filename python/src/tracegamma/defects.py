# (c) 2026 William J. Dwyer. MIT License.
r"""The two governing defects, and the standardized cumulants behind them.

The trace-gamma matches three cumulants exactly, so its error is governed by
what happens at the fourth and in the far tail. Two scalars summarise that:

* the **kurtosis defect** ``Dgamma2 = 12 (p2 p4 - p3^2) / p2^3``, non-negative
  by Cauchy-Schwarz and zero exactly at equal eigenvalues, which drives the
  shoulder error through the leading Cornish-Fisher term;
* the **tail-rate defect** ``delta = 1 - (p3/p2)/max(lam)``, in ``[0, 1)``, zero
  at both the equal and the single-dominant limit, which drives the deep tail.

Here ``p_r = sum_j lam_j^r``.

Provenance
----------
Ported from ``tracegamma_tailbound_minimal.py`` (Lemmas 2 and 3) and
``verify_m1_m2.py`` (the standardized cumulants and the characteristic-function
modulus).
"""
from __future__ import annotations

import math

import numpy as np

__all__ = [
    "kurtosis_defect",
    "tail_rate_defect",
    "standardized_cumulant",
    "rho_ratio",
    "cf_modulus",
]


def kurtosis_defect(lam):
    r"""``Dgamma2 = 12 (p2 p4 - p3^2) / p2^3``, the fourth-cumulant mismatch.

    Non-negative for every real spectrum, and zero exactly when all eigenvalues
    are equal -- the case where the trace-gamma is not an approximation at all
    but the exact Pearson reference.

    Parameters
    ----------
    lam : array_like

    Returns
    -------
    float

    Examples
    --------
    >>> round(kurtosis_defect([1.0] * 5), 12)
    0.0
    >>> kurtosis_defect([10.0, 1.0, 1.0]) > 0
    True
    """
    lam = np.asarray(lam, float)
    p2, p3, p4 = (lam ** 2).sum(), (lam ** 3).sum(), (lam ** 4).sum()
    return float(12.0 * (p2 * p4 - p3 ** 2) / p2 ** 3)


def tail_rate_defect(lam):
    r"""``delta = 1 - (p3/p2)/max(lam)``, the exponential-rate mismatch.

    The trace-gamma's tail decays at rate ``1/(2a) = p2/(2 p3)``; the exact law
    decays at ``1/(2 max lam)``. ``delta`` is the relative gap, in ``[0, 1)``,
    and vanishes at *both* ends: equal eigenvalues and one dominant eigenvalue.

    Examples
    --------
    >>> round(tail_rate_defect([1.0] * 5), 12)
    0.0
    >>> 0 < tail_rate_defect([4.0, 2.0, 1.0]) < 1
    True
    """
    lam = np.asarray(lam, float)
    p2, p3 = (lam ** 2).sum(), (lam ** 3).sum()
    return float(1.0 - (p3 / p2) / lam.max())


def standardized_cumulant(lam, r):
    r"""``gamma_{r-2} = kappa_r / kappa_2^{r/2}`` for ``Q = sum lam_j chi^2_1``.

    Uses ``kappa_r = 2^{r-1} (r-1)! p_r``.

    Examples
    --------
    >>> round(standardized_cumulant([1.0], 3), 10)
    2.8284271247
    """
    lam = np.asarray(lam, float)
    kap = lambda j: 2.0 ** (j - 1) * math.factorial(j - 1) * (lam ** j).sum()
    return float(kap(r) / kap(2) ** (r / 2.0))


def rho_ratio(lam):
    r"""``max(lam) / sqrt(p2)``: how far the spectrum is from flat.

    One when a single eigenvalue carries everything, ``1/sqrt(m)`` when ``m`` are
    equal.
    """
    lam = np.asarray(lam, float)
    return float(lam.max() / np.sqrt((lam ** 2).sum()))


def cf_modulus(t, lam):
    r"""``|phi_Q(t)|`` for ``Q = sum lam_j chi^2_1``.

    The characteristic function is ``prod_j (1 - 2 i lam_j t)^{-1/2}``, so its
    modulus is ``prod_j (1 + 4 lam_j^2 t^2)^{-1/4}``.
    """
    lam = np.asarray(lam, float)
    return float(np.prod((1.0 + 4.0 * lam ** 2 * t ** 2) ** -0.25))
