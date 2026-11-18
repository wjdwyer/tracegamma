# (c) 2026 William J. Dwyer. MIT License.
r"""The Berger-Boos scale mixture: the guaranteed test's oracle law.

The guaranteed statistic ``T_BB`` dilates the trace-gamma cutoff by a
data-dependent log-variance scale. Equivalently, the deployed statistic is the
trace-gamma core *divided* by an independent scale, so its law is a scale
mixture of the core over the log-chi-square dispersion -- the object the paper
names the **Berger-Boos scale mixture**.

Scope warning
-------------
This module is here because the scope chosen for the package was "everything in
the project tree". The statistic itself belongs to a different paper in the
series (m01A / T_BB), not to the trace-gamma paper. Nothing in the trace-gamma
propositions depends on it. Treat it as a convenience, and read that paper
before relying on the constant ``ks``.
"""
from __future__ import annotations

import numpy as np

__all__ = ["bb_scale_mixture"]


def bb_scale_mixture(core_cutoff, ks, rbar, k):
    r"""Inflate a trace-gamma cutoff to the guaranteed ``T_BB`` cutoff.

    ``T_BB`` rejects when ``Q_obs > exp(ks sqrt(rbar/k)) * core_cutoff``.

    Parameters
    ----------
    core_cutoff : float or array_like
        The trace-gamma cutoff, e.g. from
        :meth:`tracegamma.core.TraceGamma.cutoff`.
    ks : float
        The Berger-Boos constant for the design.
    rbar : float
        The design radius (log-variance dispersion).
    k : int
        Number of groups.

    Returns
    -------
    float or ndarray
        The inflated cutoff.

    Examples
    --------
    >>> round(float(bb_scale_mixture(10.0, 0.0, 1.0, 4)), 12)
    10.0
    """
    return np.exp(ks * np.sqrt(rbar / k)) * core_cutoff
