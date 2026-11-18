# (c) 2026 William J. Dwyer. MIT License.
r"""The trace-gamma reference distribution and its three constructors.

A test statistic that is a quadratic form ``Q = a' M a`` in a near-normal vector
``a ~ N(mu, D)`` has an exact null law that is a generalized chi-square -- a
weighted sum of chi-squares, one per eigenvalue of ``M^{1/2} D M^{1/2}``. That
law has no closed form. The trace-gamma is the closed-form three-cumulant match

.. math::  Q \;\approx\; b + a\,\chi^2_\nu

a shifted, scaled chi-square (equivalently a shifted gamma, equivalently Pearson
Type III), whose three parameters are fixed by the first three cumulants of
``Q``. Those cumulants are *exact traces* (Lancaster's trace-cumulant identity):

.. math::  \kappa_r = 2^{r-1}(r-1)!\,\operatorname{tr}((MD)^r)

so ``kappa_1 = t_1``, ``kappa_2 = 2 t_2``, ``kappa_3 = 8 t_3`` with
``t_r = tr((MD)^r)``.

Two classical references are *members* of this family rather than competitors:

* ``TraceGamma(k1, k2, 0)`` is Satterthwaite's two-moment scaled chi-square,
  which applied to the between-group quadratic is Welch's (1951) reference;
* equal nonzero eigenvalues of ``MD`` give exactly ``chi^2`` on their number,
  which is Pearson's reference.

Provenance
----------
This module is a behaviour-preserving port of ``mseries_qgamma.py`` as deposited
with the paper (Zenodo concept DOI 10.5281/zenodo.22060095). The port changes no
formula and no constant. ``tests/test_deposited.py`` pins the port to the
deposited module on a fixed grid; if that test fails, the port is wrong, not the
deposit.

Two deliberate, documented differences, neither on the numerical path:

1. ``cdf`` uses an ``if`` where the deposited module used ``numpy.where``. The
   two arms of that ``where`` are algebraically identical -- ``(b - x)/(-a)``
   equals ``(x - b)/a`` for every ``a != 0`` -- and ``a`` is a scalar, so the
   branch was never selecting between different values. The ``if`` computes the
   same number without evaluating a dead arm.
2. The fitted branch is recorded in :attr:`TraceGamma.branch` and a negative
   third cumulant raises a warning. In the deposited module a negative ``k3``
   silently takes the two-cumulant branch (see :class:`TraceGamma`); the value
   returned here is unchanged, but the user is told.
"""
from __future__ import annotations

import warnings

import numpy as np
from scipy.stats import chi2 as _chi2

__all__ = [
    "cumulants_from_traces",
    "traces_from_quadform",
    "cumulants_from_eigs",
    "params_from_power_sums",
    "TraceGamma",
]

#: Skewness below which the fit degenerates to the two-cumulant (Welch) form.
#: Frozen at the deposited value; exposed so the threshold is inspectable rather
#: than buried in a comparison.
SKEW_FLOOR = 1e-6

#: Lower clamp on the second cumulant, frozen at the deposited value.
VAR_FLOOR = 1e-12


def cumulants_from_traces(t1, t2, t3):
    r"""Cumulants of ``Q = a'Ma`` with ``a ~ N(0, D)`` from the traces.

    Parameters
    ----------
    t1, t2, t3 : float
        The traces ``t_r = tr((MD)^r)``.

    Returns
    -------
    tuple of float
        ``(kappa1, kappa2, kappa3) = (t1, 2*t2, 8*t3)``, Lancaster's identity
        ``kappa_r = 2^{r-1}(r-1)! t_r`` at ``r = 1, 2, 3``.

    Examples
    --------
    >>> cumulants_from_traces(1.0, 1.0, 1.0)
    (1.0, 2.0, 8.0)
    """
    return t1, 2.0 * t2, 8.0 * t3


def traces_from_quadform(M, D):
    r"""Exact ``t1, t2, t3 = tr(MD), tr((MD)^2), tr((MD)^3)``.

    Parameters
    ----------
    M : array_like, shape (p, p)
        Symmetric form matrix.
    D : array_like, shape (p,) or (p, p)
        Covariance of ``a``. A 1-D argument is read as the diagonal.

    Returns
    -------
    tuple of float
        The three traces.
    """
    M = np.asarray(M, float)
    Dm = np.diag(np.asarray(D, float)) if np.ndim(D) == 1 else np.asarray(D, float)
    MD = M @ Dm
    MD2 = MD @ MD
    return np.trace(MD), np.trace(MD2), np.trace(MD2 @ MD)


def cumulants_from_eigs(lam):
    r"""Cumulants of the exact law ``sum_j lam_j chi^2_1``.

    This is the generalized chi-square itself, so these cumulants are exact, not
    an approximation: ``(sum lam, 2 sum lam^2, 8 sum lam^3)``.

    Parameters
    ----------
    lam : array_like
        Eigenvalues of ``M^{1/2} D M^{1/2}``.

    Returns
    -------
    tuple of float
        ``(kappa1, kappa2, kappa3)``.
    """
    lam = np.asarray(lam, float)
    return lam.sum(), 2.0 * (lam ** 2).sum(), 8.0 * (lam ** 3).sum()


def params_from_power_sums(lam):
    r"""The closed-form parameters, straight from the eigenvalue power sums.

    With ``p_r = sum_j lam_j^r`` (which equal the traces ``t_r`` when ``MD`` has
    eigenvalues ``lam``),

    .. math::
        a = \frac{p_3}{p_2}, \qquad
        \nu = \frac{p_2^3}{p_3^2}, \qquad
        b = p_1 - \frac{p_2^2}{p_3}.

    This is an *identity*, not a second method: it is the cumulant match of
    :class:`TraceGamma` rewritten in the traces. The two agree to floating-point
    rounding, and ``tests/test_identities.py`` checks that on designed spectra.
    Keeping both lets each serve as the other's oracle.

    Parameters
    ----------
    lam : array_like
        Strictly positive eigenvalues.

    Returns
    -------
    tuple of float
        ``(a, nu, b)``.
    """
    lam = np.asarray(lam, float)
    p1, p2, p3 = lam.sum(), (lam ** 2).sum(), (lam ** 3).sum()
    return p3 / p2, p2 ** 3 / p3 ** 2, p1 - p2 ** 2 / p3


def _unwrap(value, like):
    """Return a plain float when the input was scalar, else the array."""
    if np.ndim(like) == 0:
        return float(value)
    return value


class TraceGamma:
    r"""``Q ~ b + a * chi^2_nu``, matched to three cumulants of a quadratic form.

    Parameters
    ----------
    k1, k2, k3 : float
        The first three cumulants of ``Q``. ``k2`` is clamped below at
        :data:`VAR_FLOOR`.

    Attributes
    ----------
    a, nu, b : float
        Scale, degrees of freedom, shift.
    k1, k2, k3 : float
        The cumulants actually used, after clamping.
    branch : str
        ``"three-cumulant"`` or ``"welch-two-cumulant"`` -- which fit was taken.

    Notes
    -----
    **The two-cumulant branch is requested, not discovered.** It is taken when
    the standardized skewness ``gamma1 = k3 / k2**1.5`` does not exceed
    :data:`SKEW_FLOOR`. For a quadratic form with *positive* eigenvalues that
    cannot happen in practice: ``gamma1 = 2 sqrt(2) p_3 / p_2**1.5``, which is
    minimised at equal eigenvalues and is then ``2 sqrt(2) / sqrt(m)`` for ``m``
    of them, so reaching ``1e-6`` would take about ``8e12`` eigenvalues. The
    branch is therefore reached by *supplying* ``k3 = 0`` -- which is exactly how
    the paper states the Welch special case -- or a negative ``k3``.

    **A negative third cumulant is discarded, with a warning.** An indefinite
    ``M`` can give ``k3 < 0``. ``gamma1`` is then negative, so the fit falls to
    the two-cumulant form and the third cumulant plays no part. The deposited
    module does this silently; this class does the same arithmetic and warns.

    Examples
    --------
    Pearson's reference is the equal-eigenvalue member:

    >>> tg = TraceGamma.from_eigs([1.0] * 5)
    >>> [round(v, 12) for v in tg.params()]
    [1.0, 5.0, 0.0]
    >>> tg.branch
    'three-cumulant'

    Welch's reference is the two-cumulant member, obtained by asking for it:

    >>> w = TraceGamma(10.0, 20.0, 0.0)
    >>> w.branch
    'welch-two-cumulant'
    >>> [round(v, 12) for v in w.params()]
    [1.0, 10.0, 0.0]
    """

    def __init__(self, k1, k2, k3):
        self.k1 = float(k1)
        self.k2 = float(max(k2, VAR_FLOOR))
        self.k3 = float(k3)
        g1 = self.k3 / self.k2 ** 1.5
        if g1 > SKEW_FLOOR:
            self.branch = "three-cumulant"
            self.nu = float(8.0 / g1 ** 2)
            self.a = float(np.sqrt(self.k2 / (2.0 * self.nu)))
            self.b = float(self.k1 - self.a * self.nu)
        else:
            self.branch = "welch-two-cumulant"
            if self.k3 < 0.0:
                warnings.warn(
                    "third cumulant k3=%.6g is negative, so the standardized "
                    "skewness is negative and the three-cumulant fit does not "
                    "apply; falling back to the two-cumulant (Welch) reference, "
                    "which ignores k3 entirely. Inspect .branch to confirm which "
                    "fit you have." % self.k3,
                    RuntimeWarning,
                    stacklevel=2,
                )
            self.nu = float(2.0 * self.k1 ** 2 / self.k2)
            self.a = float(self.k2 / (2.0 * self.k1))
            self.b = 0.0

    # ---- constructors -----------------------------------------------------
    @classmethod
    def from_traces(cls, t1, t2, t3, kurt_widen=0.0, skew_shift=0.0):
        r"""Build from the traces, with the two estimable non-normal corrections.

        Parameters
        ----------
        t1, t2, t3 : float
            Traces ``tr((MD)^r)``.
        kurt_widen : float, optional
            Added to ``kappa_2``: the marginal-kurtosis widening
            ``sum_i M_ii^2 kappa4(a_i)``. See
            :func:`tracegamma.correction.kurtosis_widening`.
        skew_shift : float, optional
            Added to ``kappa_1``: the test-specific mean/variance covariance
            inflation.

        Returns
        -------
        TraceGamma
        """
        k1, k2, k3 = cumulants_from_traces(t1, t2, t3)
        return cls(k1 + skew_shift, k2 + kurt_widen, k3)

    @classmethod
    def from_quadform(cls, M, D, **kw):
        """Build from the form matrix and covariance directly."""
        return cls.from_traces(*traces_from_quadform(M, D), **kw)

    @classmethod
    def from_eigs(cls, lam):
        """Build from the eigenvalues of ``M^{1/2} D M^{1/2}``."""
        return cls(*cumulants_from_eigs(lam))

    # ---- distribution interface -------------------------------------------
    def cdf(self, x):
        """Distribution function ``P(Q <= x)``."""
        xa = np.asarray(x, float)
        z = (xa - self.b) / self.a
        out = _chi2.cdf(z, self.nu) if self.a > 0 else _chi2.cdf((self.b - xa) / -self.a, self.nu)
        return _unwrap(out, x)

    def sf(self, x):
        """Survival function ``P(Q > x)``."""
        return _unwrap(1.0 - self.cdf(x), x)

    def ppf(self, q):
        """Quantile function."""
        return _unwrap(self.b + self.a * _chi2.ppf(q, self.nu), q)

    def pdf(self, x):
        """Density."""
        z = (np.asarray(x, float) - self.b) / self.a
        return _unwrap(_chi2.pdf(z, self.nu) / self.a, x)

    def rvs(self, size, rng=None):
        """Draw variates. ``rng`` is a :class:`numpy.random.Generator`."""
        rng = rng or np.random.default_rng()
        return self.b + self.a * rng.chisquare(self.nu, size)

    def cutoff(self, alpha=0.05):
        """Upper-tail critical value, the ``1 - alpha`` quantile."""
        return self.ppf(1.0 - alpha)

    def cumulants(self):
        """The ``(k1, k2, k3)`` actually used, after clamping."""
        return self.k1, self.k2, self.k3

    def params(self):
        """The fitted ``(a, nu, b)`` as plain floats."""
        return float(self.a), float(self.nu), float(self.b)

    def __repr__(self):
        return (
            "TraceGamma(a=%.4g, nu=%.4g, b=%.4g; k1=%.4g, k2=%.4g, k3=%.4g, "
            "branch=%s)" % (self.a, self.nu, self.b, self.k1, self.k2, self.k3, self.branch)
        )
