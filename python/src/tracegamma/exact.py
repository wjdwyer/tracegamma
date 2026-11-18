# (c) 2026 William J. Dwyer. MIT License.
r"""The exact generalized chi-square, by Imhof's (1961) numerical inversion.

For ``Q = sum_j lam_j chi^2_1`` Imhof's formula gives the survival function:

.. math::
    P(Q > x) = \tfrac12 + \frac1\pi \int_0^\infty
        \frac{\sin \theta(u)}{u\,\rho(u)}\,du, \qquad
    \theta(u) = \tfrac12\sum_j \arctan(\lambda_j u) - \tfrac{xu}{2}, \qquad
    \rho(u) = \prod_j (1 + \lambda_j^2u^2)^{1/4}.

This is the law the trace-gamma approximates in closed form, and it is the
ground truth against which the approximation's accuracy is stated.

Two methods, and why
--------------------
``method="panel"`` (default)
    Integrate between successive zeros of ``sin(theta)`` and accelerate the
    resulting alternating series by repeated averaging. Accurate across the
    whole range tested.

``method="quad"``
    One :func:`scipy.integrate.quad` call on ``[0, inf)``. This is what the
    deposited ``qgamma_imhof.py`` does, and it is kept so the published
    cross-check numbers remain exactly reproducible.

**The ``quad`` method is not reliable for small spectra, and this was measured,
not assumed.** The integrand decays like ``u^{-(1+m/2)}`` and oscillates with
period ``4 pi / x``, so for few eigenvalues ``quad`` cannot resolve the tail and
returns a poor answer while reporting only a subdivision warning. Against the
exact oracle ``sum_{j=1}^m 1 * chi^2_1 = chi^2_m``, worst relative error over
quantiles from 0.001 to 0.999 (measured, not asserted):

======  ======================  =====================
``m``   ``method="quad"``       ``method="panel"``
======  ======================  =====================
1       6.9e-01                 < 5e-09
2       1.0e-02                 < 5e-09
3       1.1e-03                 < 5e-09
5       2.3e-06                 < 5e-09
10      2.3e-10                 < 5e-09
20      7.1e-12                 < 5e-09
======  ======================  =====================

So ``quad`` is fine for the ten-plus eigenvalue spectra the paper uses and
unusable at ``m <= 2``. ``panel`` is uniformly good and slower. The default is
``panel`` because a package is called with inputs its author did not choose.
``tests/test_exact.py`` pins both columns of that table.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

__all__ = ["imhof_sf", "imhof_cdf", "imhof_ppf"]

#: Number of half-period panels used by ``method="panel"``.
PANELS = 400


def _kernel(lam, x):
    lam = np.asarray(lam, float)

    def theta(u):
        return 0.5 * np.sum(np.arctan(lam * u)) - 0.5 * x * u

    def rho(u):
        return np.prod((1.0 + (lam * u) ** 2) ** 0.25)

    return (lambda u: np.sin(theta(u)) / (u * rho(u))), theta


def _sf_quad(x, lam, limit=500, epsabs=1e-12, epsrel=1e-12):
    f, _ = _kernel(lam, x)
    val, _ = quad(f, 0, np.inf, limit=limit, epsabs=epsabs, epsrel=epsrel)
    return 0.5 + val / np.pi


def _sf_panel(x, lam, panels=PANELS):
    f, theta = _kernel(lam, x)

    def zero_for(k):
        target = -k * np.pi
        hi = 1.0
        while theta(hi) > target:
            hi *= 2.0
            if hi > 1e14:
                return None
        return brentq(lambda u: theta(u) - target, 1e-12, hi, xtol=1e-14, rtol=8.9e-16)

    edges = [1e-12]
    for k in range(1, panels + 1):
        z = zero_for(k)
        if z is None or z <= edges[-1]:
            break
        edges.append(z)

    # A panel whose endpoints differ by orders of magnitude cannot be integrated
    # by one adaptive quad call: the integrand's mass sits near u ~ 1/max(lam),
    # and for small x the first zero is near 2*pi/x, so the opening panel can span
    # 1e7 while the mass occupies the first unit of it. quad then samples only the
    # empty part and returns ~0 -- which silently gave sf = 0.5 for every small x.
    # Subdividing GEOMETRICALLY puts the sample points where the mass is;
    # subdividing linearly does not, and was the first fix that failed here.
    parts = []
    for a, b in zip(edges[:-1], edges[1:]):
        n = int(np.clip(np.ceil(np.log10(b / a) * 12.0), 1, 200))
        cuts = np.geomspace(a, b, n + 1)
        parts.append(sum(quad(f, c, d, limit=200, epsabs=1e-14, epsrel=1e-14)[0]
                         for c, d in zip(cuts[:-1], cuts[1:])))

    if not parts:
        raise ValueError("no oscillation panel found for x=%.6g; the integrand never "
                         "turns over, which should not happen for finite x" % x)
    s = np.cumsum(parts)
    for _ in range(10):                      # Euler transform of an alternating series
        if len(s) < 3:
            break
        s = 0.5 * (s[:-1] + s[1:])
    return 0.5 + s[-1] / np.pi


def imhof_sf(x, lam, method="panel", **kw):
    r"""Exact ``P(Q > x)`` for ``Q = sum_j lam_j chi^2_1``.

    Parameters
    ----------
    x : float
    lam : array_like
        Eigenvalues.
    method : {"panel", "quad"}
        See the module docstring. ``"quad"`` reproduces the deposited code.

    Returns
    -------
    float
        Clipped to ``[0, 1]``.

    Examples
    --------
    Equal unit eigenvalues give exactly a chi-square, so this is checkable:

    >>> from scipy.stats import chi2
    >>> bool(abs(imhof_sf(10.0, [1.0] * 5) - chi2.sf(10.0, 5)) < 1e-11)
    True
    """
    val = _sf_panel(x, lam, **kw) if method == "panel" else _sf_quad(x, lam, **kw)
    return float(min(max(val, 0.0), 1.0))


def imhof_cdf(x, lam, **kw):
    """Exact ``P(Q <= x)``; see :func:`imhof_sf`."""
    return 1.0 - imhof_sf(x, lam, **kw)


def imhof_ppf(q, lam, xtol=1e-10, rtol=1e-12, **kw):
    r"""Exact ``q``-quantile, by root-finding on the Imhof CDF.

    Raises
    ------
    ValueError
        If the eigenvalues are not positive, or if the search bracket does not
        contain the root. The deposited code used a fixed bracket with no such
        check, so an out-of-bracket quantile surfaced only as a brentq failure
        with no stated cause.
    """
    lam = np.asarray(lam, float)
    if np.any(lam <= 0):
        raise ValueError("imhof_ppf expects positive eigenvalues; got min %.6g" % lam.min())
    lo, hi = 1e-6, 12.0 * lam.sum() + 120.0
    f = lambda t: imhof_cdf(t, lam, **kw) - q
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        raise ValueError(
            "quantile q=%.6g is outside the search bracket [%.6g, %.6g] "
            "(cdf spans [%.8f, %.8f]); widen the bracket" % (q, lo, hi, flo + q, fhi + q)
        )
    return float(brentq(f, lo, hi, xtol=xtol, rtol=rtol))
