"""Distributional contract: the interface must behave like a distribution."""
import numpy as np
import pytest
from scipy.stats import chi2

from tracegamma import TraceGamma

SPECTRA = {
    "equal-5": [1.0] * 5, "two-point": [3.0, 1, 1, 1, 1], "geometric": list(2.0 ** -np.arange(6)),
    "dominant": [10.0, 1, 1], "welch-like": [1.0, .5, .25, .125], "spread": [100.0, 10, 1, .1],
    "single": [2.0],
}
QS = np.array([1e-4, 0.01, 0.1, 0.5, 0.9, 0.99, 1 - 1e-4])


@pytest.mark.parametrize("name", list(SPECTRA))
def test_cdf_ppf_roundtrip(name):
    tg = TraceGamma.from_eigs(SPECTRA[name])
    assert np.allclose(tg.cdf(tg.ppf(QS)), QS, atol=1e-12)


@pytest.mark.parametrize("name", list(SPECTRA))
def test_cdf_monotone_and_sf_complementary(name):
    tg = TraceGamma.from_eigs(SPECTRA[name])
    grid = np.linspace(tg.ppf(1e-6), tg.ppf(1 - 1e-6), 200)
    F = tg.cdf(grid)
    assert np.all(np.diff(F) >= -1e-15)
    assert np.allclose(tg.sf(grid), 1.0 - F, atol=0)


@pytest.mark.parametrize("name", list(SPECTRA))
def test_pdf_is_the_derivative_of_the_cdf(name):
    """Central difference, not quadrature: for nu < 2 the density is singular at
    the shift, so integrating from a low quantile measures the grid, not the code."""
    tg = TraceGamma.from_eigs(SPECTRA[name])
    xs = tg.ppf(np.linspace(0.2, 0.8, 25))
    h = 1e-5 * max(1.0, abs(tg.a) * tg.nu)
    num = (tg.cdf(xs + h) - tg.cdf(xs - h)) / (2 * h)
    assert np.allclose(num, tg.pdf(xs), rtol=1e-6, atol=1e-10)


@pytest.mark.parametrize("name", list(SPECTRA))
def test_moments_of_draws_match_the_fitted_cumulants(name):
    tg = TraceGamma.from_eigs(SPECTRA[name])
    x = tg.rvs(400_000, np.random.default_rng(12345))
    assert abs(x.mean() - (tg.b + tg.a * tg.nu)) < 6 * x.std() / np.sqrt(x.size)
    assert abs(x.var() / (2 * tg.a ** 2 * tg.nu) - 1.0) < 0.02


def test_scalar_in_scalar_out():
    tg = TraceGamma.from_eigs([2.0, 1.0])
    for v in (tg.cdf(1.0), tg.sf(1.0), tg.ppf(0.5), tg.pdf(1.0), tg.cutoff()):
        assert isinstance(v, float)
    assert isinstance(tg.cdf([1.0, 2.0]), np.ndarray)


def test_pearson_is_the_equal_eigenvalue_member():
    """Equal unit eigenvalues must reproduce chi^2_m exactly, not approximately."""
    for m in (1, 3, 5, 12):
        tg = TraceGamma.from_eigs([1.0] * m)
        assert tg.params() == pytest.approx((1.0, float(m), 0.0), abs=1e-12)
        x = np.linspace(0.1, 3 * m, 50)
        assert np.allclose(tg.cdf(x), chi2.cdf(x, m), atol=1e-14)


def test_welch_branch_is_requested_not_discovered():
    """No positive spectrum reaches the two-cumulant branch; k3=0 does."""
    for name, lam in SPECTRA.items():
        assert TraceGamma.from_eigs(lam).branch == "three-cumulant"
    w = TraceGamma(10.0, 20.0, 0.0)
    assert w.branch == "welch-two-cumulant"
    assert w.params() == pytest.approx((1.0, 10.0, 0.0))


def test_negative_third_cumulant_warns_and_drops_to_two_cumulants():
    with pytest.warns(RuntimeWarning, match="negative"):
        tg = TraceGamma(10.0, 20.0, -40.0)
    assert tg.branch == "welch-two-cumulant"
    assert tg.params() == pytest.approx(TraceGamma(10.0, 20.0, 0.0).params())
