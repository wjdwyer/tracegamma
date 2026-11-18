"""Pin the port to the deposited module. If this fails, the port is wrong."""
import os
import pathlib
import sys

import numpy as np
import pytest

from tracegamma import TraceGamma, bb_scale_mixture

# The deposited research module is not part of this repository -- it lives with
# the paper's Zenodo deposit. Point TRACEGAMMA_DEPOSIT at a directory containing
# mseries_qgamma.py to run these, or let them skip. They are the strongest
# evidence the port is faithful, so run them at least once before a release.
DEPOSIT = os.environ.get(
    "TRACEGAMMA_DEPOSIT",
    str(pathlib.Path(__file__).resolve().parents[2] / "mdist_work"),
)

if os.path.isdir(DEPOSIT) and DEPOSIT not in sys.path:
    sys.path.insert(0, DEPOSIT)
try:
    import mseries_qgamma as DEP
except Exception:                                    # pragma: no cover
    DEP = None

pytestmark = pytest.mark.skipif(
    DEP is None,
    reason="deposited mseries_qgamma.py not importable; set TRACEGAMMA_DEPOSIT",
)

GRID = [[1.0] * 5, [3.0, 1, 1, 1, 1], [10.0, 1, 1], [1.0, .5, .25, .125],
        [100.0, 10, 1, .1], [2.0], [4.0, 2.0, 1.0, 1.0]]
QS = np.array([1e-4, 0.01, 0.05, 0.5, 0.95, 0.99, 1 - 1e-4])


@pytest.mark.parametrize("lam", GRID)
def test_parameters_match_the_deposit_bit_for_bit(lam):
    mine, theirs = TraceGamma.from_eigs(lam), DEP.TraceGamma.from_eigs(lam)
    assert (mine.a, mine.nu, mine.b) == (float(theirs.a), float(theirs.nu), float(theirs.b))


@pytest.mark.parametrize("lam", GRID)
def test_quantiles_and_probabilities_match_the_deposit(lam):
    mine, theirs = TraceGamma.from_eigs(lam), DEP.TraceGamma.from_eigs(lam)
    assert np.array_equal(np.asarray(mine.ppf(QS)), np.asarray(theirs.ppf(QS)))
    x = np.asarray(theirs.ppf(QS))
    assert np.array_equal(np.asarray(mine.cdf(x)), np.asarray(theirs.cdf(x)))
    assert np.array_equal(np.asarray(mine.pdf(x)), np.asarray(theirs.pdf(x)))


def test_bb_scale_mixture_matches_the_deposit():
    for args in [(10.0, 1.2, 0.8, 4), (3.5, 0.0, 1.0, 2), (7.0, 2.0, 2.5, 6)]:
        assert float(bb_scale_mixture(*args)) == float(DEP.bb_scale_mixture(*args))


def test_the_where_branch_in_the_deposited_cdf_was_a_no_op():
    """Both arms of the deposited numpy.where compute the same value."""
    tg = DEP.TraceGamma(10.0, 20.0, 40.0)
    x = np.array([-5.0, 0.0, 5.0, 50.0])
    assert np.array_equal((x - tg.b) / tg.a, (tg.b - x) / -tg.a)
