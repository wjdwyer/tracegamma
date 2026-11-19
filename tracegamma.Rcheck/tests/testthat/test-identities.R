# Identities that must hold in R on their own terms, without the fixture.
SPECTRA <- list(rep(1, 5), c(3, 1, 1, 1, 1), c(10, 1, 1), c(1, .5, .25, .125),
                c(100, 10, 1, .1), 2, c(4, 2, 1, 1))

test_that("the closed form equals the cumulant fit", {
  for (lam in SPECTRA) {
    tg <- trace_gamma(lam = lam); cf <- params_from_power_sums(lam)
    expect_equal(unname(cf), c(tg$a, tg$nu, tg$b), tolerance = 1e-12)
  }
})

test_that("Lancaster's identity holds at r = 1, 2, 3", {
  for (lam in SPECTRA) {
    t <- vapply(1:3, function(r) sum(lam^r), numeric(1))
    expect_equal(cumulants_from_traces(t[1], t[2], t[3]), cumulants_from_eigs(lam),
                 tolerance = 1e-12)
  }
})

test_that("traces of a diagonal form are the power sums", {
  for (lam in SPECTRA) {
    got <- traces_from_quadform(diag(lam, nrow = length(lam)), rep(1, length(lam)))
    expect_equal(got, vapply(1:3, function(r) sum(lam^r), numeric(1)), tolerance = 1e-12)
  }
})

test_that("the normal marginal correction returns the Gaussian cumulants", {
  for (m in c(1, 4, 6, 10))
    expect_equal(marginal_cumulants(m), cumulants_from_eigs(rep(1, m)), tolerance = 1e-12)
})

test_that("Pearson is the equal-eigenvalue member, exactly", {
  for (m in c(1, 3, 5, 12)) {
    tg <- trace_gamma(lam = rep(1, m))
    expect_equal(c(tg$a, tg$nu, tg$b), c(1, m, 0), tolerance = 1e-12)
    x <- seq(0.1, 3 * m, length.out = 50)
    expect_equal(tg_cdf(tg, x), pchisq(x, m), tolerance = 1e-13)
  }
})

test_that("cdf and ppf invert each other and the cdf is monotone", {
  qs <- c(1e-4, .01, .1, .5, .9, .99, 1 - 1e-4)
  for (lam in SPECTRA) {
    tg <- trace_gamma(lam = lam)
    expect_equal(tg_cdf(tg, tg_ppf(tg, qs)), qs, tolerance = 1e-12)
    g <- tg_ppf(tg, seq(1e-6, 1 - 1e-6, length.out = 200))
    expect_true(all(diff(tg_cdf(tg, g)) >= -1e-12))
  }
})

test_that("the Welch branch is requested, not discovered", {
  for (lam in SPECTRA) expect_identical(trace_gamma(lam = lam)$branch, "three-cumulant")
  expect_identical(trace_gamma(10, 20, 0)$branch, "welch-two-cumulant")
})

test_that("a negative third cumulant warns and drops to two cumulants", {
  expect_warning(tg <- trace_gamma(10, 20, -40), "negative")
  expect_identical(tg$branch, "welch-two-cumulant")
  expect_equal(c(tg$a, tg$nu), c(trace_gamma(10, 20, 0)$a, trace_gamma(10, 20, 0)$nu))
})

test_that("the exact law reproduces chi-square for equal eigenvalues", {
  for (m in c(1, 2, 3, 5)) {
    x <- qchisq(0.99, m)
    expect_equal(imhof_sf(x, rep(1, m)), pchisq(x, m, lower.tail = FALSE), tolerance = 1e-7)
  }
})

test_that("imhof_ppf rejects non-positive eigenvalues", {
  expect_error(imhof_ppf(0.5, c(1, -1)), "positive eigenvalues")
})
