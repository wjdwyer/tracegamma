# (c) 2026 William J. Dwyer. MIT License.
r"""The estimable non-normal correction.

When the input vector is not exactly normal, the Gaussian trace cumulants are
wrong in a way that is itself estimable. For the simplest case ``Q = sum_j a_j^2``
with ``a_j`` standardized i.i.d. with standardized moments ``mu4``, ``mu6``:

.. math::
    \kappa_1 = m, \qquad
    \kappa_2 = m(\mu_4 - 1), \qquad
    \kappa_3 = m(\mu_6 - 3\mu_4 + 2).

These are exact, not asymptotic. Substituting the normal values
``mu4 = 3, mu6 = 15`` returns the Gaussian answer ``(m, 2m, 8m)``, which is the
identity :func:`tracegamma.core.cumulants_from_eigs` gives for ``m`` unit
eigenvalues -- a check worth running, and ``tests/test_identities.py`` runs it.

Provenance
----------
Ported from ``qgamma_cumulant_correction.py``, where the oracle (true moments)
and plug-in (estimated moments) versions are both exercised against realized
size.
"""
from __future__ import annotations

import numpy as np

from .core import TraceGamma

__all__ = ["marginal_cumulants", "tracegamma_from_marginal", "estimate_moments",
           "kurtosis_widening"]

#: Standardized fourth and sixth moments of the standard normal.
NORMAL_MU4, NORMAL_MU6 = 3.0, 15.0


def marginal_cumulants(m, mu4=NORMAL_MU4, mu6=NORMAL_MU6):
    r"""Exact ``(kappa1, kappa2, kappa3)`` of ``Q = sum_{j=1}^m a_j^2``.

    Parameters
    ----------
    m : int
        Number of standardized i.i.d. terms.
    mu4, mu6 : float
        Standardized fourth and sixth moments of the common marginal. The
        defaults are the normal values, which reproduce the Gaussian cumulants.

    Returns
    -------
    tuple of float

    Examples
    --------
    >>> marginal_cumulants(5)
    (5.0, 10.0, 40.0)
    """
    m = float(m)
    return m, m * (mu4 - 1.0), m * (mu6 - 3.0 * mu4 + 2.0)


def tracegamma_from_marginal(m, mu4=NORMAL_MU4, mu6=NORMAL_MU6):
    """The reference for ``Q = sum a_j^2`` under a common non-normal marginal."""
    return TraceGamma(*marginal_cumulants(m, mu4, mu6))


def estimate_moments(pool):
    """Plug-in ``(mu4, mu6)`` from a pooled sample, after standardizing it.

    This is the deployable half of the correction: the oracle version needs
    moments you do not have, this one estimates them from the same data.
    """
    x = np.asarray(pool, float)
    x = (x - x.mean()) / x.std()
    return float((x ** 4).mean()), float((x ** 6).mean())


def kurtosis_widening(M_diag, kappa4):
    r"""The ``kappa_2`` widening ``sum_i M_ii^2 kappa4(a_i)``.

    Pass the result as ``kurt_widen`` to
    :meth:`tracegamma.core.TraceGamma.from_traces`.

    Parameters
    ----------
    M_diag : array_like
        The diagonal of the form matrix ``M``.
    kappa4 : array_like or float
        Fourth cumulant of each ``a_i`` (``mu4 - 3`` for a standardized input).
    """
    M_diag = np.asarray(M_diag, float)
    return float(np.sum(M_diag ** 2 * np.asarray(kappa4, float)))
