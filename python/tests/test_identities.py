"""Identities that must hold exactly, each checkable against an independent route."""
import numpy as np
import pytest

from tracegamma import (TraceGamma, cumulants_from_eigs, cumulants_from_traces,
                        marginal_cumulants, params_from_power_sums, traces_from_quadform)

SPECTRA = [[1.0] * 5, [3.0, 1, 1, 1, 1], [10.0, 1, 1], [1.0, .5, .25, .125],
           [100.0, 10, 1, .1], [2.0], list(2.0 ** -np.arange(6))]


@pytest.mark.parametrize("lam", SPECTRA)
def test_closed_form_equals_the_cumulant_fit(lam):
    """a = p3/p2, nu = p2^3/p3^2, b = p1 - p2^2/p3 is the same object as the fit."""
    assert params_from_power_sums(lam) == pytest.approx(TraceGamma.from_eigs(lam).params(), rel=1e-12)


@pytest.mark.parametrize("lam", SPECTRA)
def test_traces_of_a_diagonal_form_are_the_power_sums(lam):
    M, D = np.diag(lam), np.ones(len(lam))
    assert traces_from_quadform(M, D) == pytest.approx(
        [sum(x ** r for x in lam) for r in (1, 2, 3)], rel=1e-12)


@pytest.mark.parametrize("lam", SPECTRA)
def test_lancaster_identity(lam):
    """kappa_r = 2^{r-1}(r-1)! t_r at r = 1, 2, 3."""
    t = [sum(x ** r for x in lam) for r in (1, 2, 3)]
    assert cumulants_from_traces(*t) == pytest.approx(cumulants_from_eigs(lam), rel=1e-12)
    assert cumulants_from_traces(*t) == pytest.approx((t[0], 2 * t[1], 8 * t[2]), rel=1e-12)


@pytest.mark.parametrize("m", [1, 4, 6, 10])
def test_normal_marginal_correction_returns_the_gaussian_cumulants(m):
    """mu4=3, mu6=15 must give exactly the m-unit-eigenvalue answer."""
    assert marginal_cumulants(m) == pytest.approx(cumulants_from_eigs([1.0] * m), rel=1e-12)


def test_quadform_constructor_agrees_with_the_eigenvalue_constructor():
    rng = np.random.default_rng(7)
    for _ in range(5):
        p = 4
        A = rng.normal(size=(p, p))
        M = A @ A.T
        d = rng.uniform(0.5, 2.0, p)
        lam = np.linalg.eigvalsh(np.diag(np.sqrt(d)) @ M @ np.diag(np.sqrt(d)))
        assert TraceGamma.from_quadform(M, d).params() == pytest.approx(
            TraceGamma.from_eigs(lam).params(), rel=1e-9)
