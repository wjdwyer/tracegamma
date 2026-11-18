"""The exact law, and the measured accuracy envelope of each method."""
import numpy as np
import pytest
from scipy.stats import chi2

from tracegamma.exact import imhof_cdf, imhof_ppf, imhof_sf

# Equal unit eigenvalues give Q = chi^2_m EXACTLY, so this is a true oracle.
PANEL_TOL = 5e-9
QUAD_WORST = {1: 1e0, 2: 2e-2, 3: 2e-3, 5: 1e-5, 10: 1e-9, 20: 1e-10}


@pytest.mark.parametrize("m", [1, 2, 3, 5, 10, 20])
def test_panel_method_is_accurate_at_every_m(m):
    for p in (0.5, 0.9, 0.99, 0.999):
        x = chi2.ppf(p, m)
        assert abs(imhof_sf(x, np.ones(m)) - chi2.sf(x, m)) / chi2.sf(x, m) < PANEL_TOL


@pytest.mark.parametrize("m", sorted(QUAD_WORST))
def test_quad_method_degrades_for_small_spectra_as_documented(m):
    """Pins the accuracy table in exact.py. If this fails the table is stale."""
    worst = max(
        abs(imhof_sf(chi2.ppf(p, m), np.ones(m), method="quad") - chi2.sf(chi2.ppf(p, m), m))
        / chi2.sf(chi2.ppf(p, m), m)
        for p in (0.5, 0.9, 0.99, 0.999)
    )
    assert worst < QUAD_WORST[m]
    if m <= 3:                      # the documented failure, asserted as a failure
        assert worst > 1e-4, "quad is no longer inaccurate at m=%d; update the table" % m


def test_cdf_and_sf_are_complementary():
    lam = [4.0, 2.0, 1.0]
    for x in (1.0, 5.0, 20.0):
        assert imhof_cdf(x, lam) + imhof_sf(x, lam) == pytest.approx(1.0, abs=1e-15)


def test_ppf_inverts_the_cdf():
    lam = [4.0, 2.0, 1.0, 1.0]
    for q in (0.05, 0.5, 0.95, 0.99):
        assert imhof_cdf(imhof_ppf(q, lam), lam) == pytest.approx(q, abs=1e-8)


def test_ppf_rejects_non_positive_eigenvalues():
    with pytest.raises(ValueError, match="positive eigenvalues"):
        imhof_ppf(0.5, [1.0, -1.0])


def test_ppf_reports_an_unbracketed_quantile_rather_than_failing_obscurely():
    with pytest.raises(ValueError, match="outside the search bracket"):
        imhof_ppf(1 - 1e-300, [1.0])
