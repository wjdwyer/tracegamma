# (c) 2026 William J. Dwyer. MIT License.

#' Standardized fourth and sixth moments of the standard normal
#' @export
NORMAL_MU4 <- 3
#' @rdname NORMAL_MU4
#' @export
NORMAL_MU6 <- 15

#' Exact cumulants of a sum of squares under a non-normal marginal
#'
#' For \eqn{Q = \sum_{j=1}^m a_j^2} with \eqn{a_j} standardized i.i.d. with
#' standardized moments \eqn{\mu_4, \mu_6}: \eqn{\kappa_1 = m},
#' \eqn{\kappa_2 = m(\mu_4 - 1)}, \eqn{\kappa_3 = m(\mu_6 - 3\mu_4 + 2)}.
#' These are exact. The normal values return the Gaussian answer
#' \eqn{(m, 2m, 8m)}, which is a check worth running.
#'
#' @param m number of terms.
#' @param mu4,mu6 standardized moments of the common marginal.
#' @return A numeric vector \code{c(k1, k2, k3)}.
#' @examples
#' marginal_cumulants(5)                  # 5 10 40
#' cumulants_from_eigs(rep(1, 5))         # the same
#' @export
marginal_cumulants <- function(m, mu4 = NORMAL_MU4, mu6 = NORMAL_MU6) {
  m <- as.numeric(m)
  c(m, m * (mu4 - 1), m * (mu6 - 3 * mu4 + 2))
}

#' Trace-gamma reference under a common non-normal marginal
#' @inheritParams marginal_cumulants
#' @return A \code{trace_gamma} object.
#' @export
tracegamma_from_marginal <- function(m, mu4 = NORMAL_MU4, mu6 = NORMAL_MU6) {
  k <- marginal_cumulants(m, mu4, mu6)
  trace_gamma(k[1], k[2], k[3])
}

#' Plug-in standardized moments from a pooled sample
#'
#' The deployable half of the correction: the oracle version needs moments you
#' do not have, this one estimates them from the same data.
#'
#' @param pool a numeric vector.
#' @return A numeric vector \code{c(mu4, mu6)}.
#' @export
estimate_moments <- function(pool) {
  x <- as.numeric(pool)
  x <- (x - mean(x)) / (sd(x) * sqrt((length(x) - 1) / length(x)))
  c(mu4 = mean(x^4), mu6 = mean(x^6))
}

#' Marginal-kurtosis widening of the second cumulant
#'
#' \eqn{\sum_i M_{ii}^2 \kappa_4(a_i)}; pass as \code{kurt_widen} to
#' \code{\link{trace_gamma}}.
#'
#' @param M_diag diagonal of the form matrix.
#' @param kappa4 fourth cumulant of each input.
#' @return A single number.
#' @export
kurtosis_widening <- function(M_diag, kappa4)
  sum(as.numeric(M_diag)^2 * as.numeric(kappa4))
