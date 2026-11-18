# (c) 2026 William J. Dwyer. MIT License.

#' Kurtosis defect
#'
#' \eqn{\Delta\gamma_2 = 12(p_2p_4 - p_3^2)/p_2^3}, the fourth-cumulant
#' mismatch. Non-negative by Cauchy-Schwarz, and zero exactly at equal
#' eigenvalues, where the trace-gamma is not an approximation at all.
#'
#' @param lam eigenvalues.
#' @return A single number.
#' @examples
#' round(kurtosis_defect(rep(1, 5)), 12)   # 0
#' @export
kurtosis_defect <- function(lam) {
  lam <- as.numeric(lam)
  p2 <- sum(lam^2); p3 <- sum(lam^3); p4 <- sum(lam^4)
  12 * (p2 * p4 - p3^2) / p2^3
}

#' Tail-rate defect
#'
#' \eqn{\delta = 1 - (p_3/p_2)/\max\lambda}, in \eqn{[0,1)}, zero at both the
#' equal-eigenvalue and single-dominant limits.
#'
#' @param lam eigenvalues.
#' @return A single number.
#' @export
tail_rate_defect <- function(lam) {
  lam <- as.numeric(lam)
  1 - (sum(lam^3) / sum(lam^2)) / max(lam)
}

#' Standardized cumulant of a generalized chi-square
#'
#' \eqn{\gamma_{r-2} = \kappa_r/\kappa_2^{r/2}} using
#' \eqn{\kappa_r = 2^{r-1}(r-1)!\,p_r}.
#'
#' @param lam eigenvalues.
#' @param r order, an integer at least 2.
#' @return A single number.
#' @export
standardized_cumulant <- function(lam, r) {
  lam <- as.numeric(lam)
  kap <- function(j) 2^(j - 1) * factorial(j - 1) * sum(lam^j)
  kap(r) / kap(2)^(r / 2)
}

#' Flatness ratio of a spectrum
#'
#' \eqn{\max\lambda/\sqrt{p_2}}: one when a single eigenvalue carries
#' everything, \eqn{1/\sqrt m} when \eqn{m} are equal.
#'
#' @param lam eigenvalues.
#' @return A single number.
#' @export
rho_ratio <- function(lam) { lam <- as.numeric(lam); max(lam) / sqrt(sum(lam^2)) }

#' Modulus of the characteristic function
#'
#' \eqn{|\phi_Q(t)| = \prod_j (1 + 4\lambda_j^2t^2)^{-1/4}}.
#'
#' @param t argument.
#' @param lam eigenvalues.
#' @return A single number.
#' @export
cf_modulus <- function(t, lam) { lam <- as.numeric(lam); prod((1 + 4 * lam^2 * t^2)^-0.25) }
