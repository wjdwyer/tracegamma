# (c) 2026 William J. Dwyer. MIT License.

#' Skewness floor below which the fit degenerates to the two-cumulant form
#' @export
SKEW_FLOOR <- 1e-6
#' Lower clamp on the second cumulant
#' @export
VAR_FLOOR <- 1e-12

#' Cumulants of a quadratic form from its traces
#'
#' Lancaster's identity \eqn{\kappa_r = 2^{r-1}(r-1)!\,t_r} at \eqn{r = 1,2,3},
#' where \eqn{t_r = tr((MD)^r)}.
#'
#' @param t1,t2,t3 the traces.
#' @return A numeric vector \code{c(k1, k2, k3)}.
#' @examples
#' cumulants_from_traces(1, 1, 1)   # 1 2 8
#' @export
cumulants_from_traces <- function(t1, t2, t3) c(t1, 2 * t2, 8 * t3)

#' Exact traces of a quadratic form
#'
#' @param M symmetric form matrix.
#' @param D covariance of the input; a vector is read as the diagonal.
#' @return A numeric vector \code{c(t1, t2, t3)}.
#' @export
traces_from_quadform <- function(M, D) {
  M <- as.matrix(M)
  Dm <- if (is.null(dim(D))) diag(as.numeric(D), nrow = length(D)) else as.matrix(D)
  MD <- M %*% Dm
  MD2 <- MD %*% MD
  c(sum(diag(MD)), sum(diag(MD2)), sum(diag(MD2 %*% MD)))
}

#' Cumulants of the exact generalized chi-square
#'
#' For \eqn{Q = \sum_j \lambda_j \chi^2_1} these are exact, not approximate.
#'
#' @param lam eigenvalues.
#' @return A numeric vector \code{c(k1, k2, k3)}.
#' @examples
#' cumulants_from_eigs(rep(1, 5))   # 5 10 40
#' @export
cumulants_from_eigs <- function(lam) {
  lam <- as.numeric(lam)
  c(sum(lam), 2 * sum(lam^2), 8 * sum(lam^3))
}

#' Closed-form parameters from the eigenvalue power sums
#'
#' With \eqn{p_r = \sum_j \lambda_j^r}, \eqn{a = p_3/p_2},
#' \eqn{\nu = p_2^3/p_3^2}, \eqn{b = p_1 - p_2^2/p_3}. This is the same object
#' as the cumulant match in \code{\link{trace_gamma}}, written in the traces;
#' the two agree to floating-point rounding and each is the other's oracle.
#'
#' @param lam eigenvalues, strictly positive.
#' @return A numeric vector \code{c(a, nu, b)}.
#' @export
params_from_power_sums <- function(lam) {
  lam <- as.numeric(lam)
  p1 <- sum(lam); p2 <- sum(lam^2); p3 <- sum(lam^3)
  c(a = p3 / p2, nu = p2^3 / p3^2, b = p1 - p2^2 / p3)
}

#' The trace-gamma reference distribution
#'
#' Fits \eqn{Q \approx b + a\,\chi^2_\nu} to three cumulants. Supply the
#' cumulants directly, or give \code{lam}, or \code{M} and \code{D}.
#'
#' @param k1,k2,k3 the first three cumulants.
#' @param lam eigenvalues; if given, the cumulants are derived from them.
#' @param M,D form matrix and covariance; if given, the traces are derived.
#' @param kurt_widen added to \eqn{\kappa_2}: the marginal-kurtosis widening.
#' @param skew_shift added to \eqn{\kappa_1}.
#'
#' @section The two-cumulant branch is requested, not discovered:
#' The fit falls to Satterthwaite's two-moment form -- Welch's reference --
#' when the standardized skewness does not exceed \code{SKEW_FLOOR}. No
#' spectrum of positive eigenvalues reaches that in practice: the skewness is
#' \eqn{2\sqrt{2}\,p_3/p_2^{3/2}}, minimised at equal eigenvalues, where it is
#' \eqn{2\sqrt{2}/\sqrt{m}}, so \code{1e-6} would need about 8e12 eigenvalues.
#' The branch is reached by supplying \code{k3 = 0}, which is how the paper
#' states the Welch special case, or a negative \code{k3}.
#'
#' @section A negative third cumulant is discarded, with a warning:
#' An indefinite \code{M} can give \code{k3 < 0}. The standardized skewness is
#' then negative, the three-cumulant fit does not apply, and the third cumulant
#' plays no part in the answer. Inspect \code{$branch} to see which fit you have.
#'
#' @return An object of class \code{trace_gamma} with elements \code{a},
#'   \code{nu}, \code{b}, \code{k1}, \code{k2}, \code{k3}, \code{branch}.
#' @examples
#' tg <- trace_gamma(lam = c(4, 2, 1, 1))
#' tg$branch
#' round(tg_cutoff(tg, 0.05), 6)
#'
#' w <- trace_gamma(10, 20, 0)      # Welch's two-cumulant member
#' w$branch
#' @export
trace_gamma <- function(k1 = NULL, k2 = NULL, k3 = NULL, lam = NULL,
                        M = NULL, D = NULL, kurt_widen = 0, skew_shift = 0) {
  if (!is.null(lam)) {
    k <- cumulants_from_eigs(lam); k1 <- k[1]; k2 <- k[2]; k3 <- k[3]
  } else if (!is.null(M) && !is.null(D)) {
    t <- traces_from_quadform(M, D)
    k <- cumulants_from_traces(t[1], t[2], t[3]); k1 <- k[1]; k2 <- k[2]; k3 <- k[3]
  }
  if (is.null(k1) || is.null(k2) || is.null(k3))
    stop("supply k1, k2, k3, or lam, or both M and D")
  k1 <- as.numeric(k1) + skew_shift
  k2 <- max(as.numeric(k2) + kurt_widen, VAR_FLOOR)
  k3 <- as.numeric(k3)
  g1 <- k3 / k2^1.5
  if (g1 > SKEW_FLOOR) {
    branch <- "three-cumulant"
    nu <- 8 / g1^2
    a <- sqrt(k2 / (2 * nu))
    b <- k1 - a * nu
  } else {
    branch <- "welch-two-cumulant"
    if (k3 < 0)
      warning(sprintf(paste0("third cumulant k3=%.6g is negative, so the standardized ",
        "skewness is negative and the three-cumulant fit does not apply; falling back ",
        "to the two-cumulant (Welch) reference, which ignores k3 entirely. Inspect ",
        "$branch to confirm which fit you have."), k3), call. = FALSE)
    nu <- 2 * k1^2 / k2
    a <- k2 / (2 * k1)
    b <- 0
  }
  structure(list(a = a, nu = nu, b = b, k1 = k1, k2 = k2, k3 = k3, branch = branch),
            class = "trace_gamma")
}

#' @export
print.trace_gamma <- function(x, ...) {
  cat(sprintf("trace_gamma(a=%.4g, nu=%.4g, b=%.4g; k1=%.4g, k2=%.4g, k3=%.4g, branch=%s)\n",
              x$a, x$nu, x$b, x$k1, x$k2, x$k3, x$branch))
  invisible(x)
}

#' Distribution function of a trace-gamma
#' @param object a \code{trace_gamma}.
#' @param x quantiles.
#' @return Numeric vector of probabilities.
#' @export
tg_cdf <- function(object, x) {
  x <- as.numeric(x)
  if (object$a > 0) pchisq((x - object$b) / object$a, object$nu)
  else pchisq((object$b - x) / -object$a, object$nu)
}

#' Survival function of a trace-gamma
#' @inheritParams tg_cdf
#' @return Numeric vector of upper-tail probabilities.
#' @export
tg_sf <- function(object, x) 1 - tg_cdf(object, x)

#' Quantile function of a trace-gamma
#' @param object a \code{trace_gamma}.
#' @param q probabilities.
#' @return Numeric vector of quantiles.
#' @export
tg_ppf <- function(object, q) object$b + object$a * qchisq(as.numeric(q), object$nu)

#' Density of a trace-gamma
#' @inheritParams tg_cdf
#' @return Numeric vector of densities.
#' @export
tg_pdf <- function(object, x) dchisq((as.numeric(x) - object$b) / object$a, object$nu) / object$a

#' Random variates from a trace-gamma
#' @param object a \code{trace_gamma}.
#' @param n number of draws.
#' @return Numeric vector of draws.
#' @export
tg_rvs <- function(object, n) object$b + object$a * rchisq(n, object$nu)

#' Upper-tail critical value of a trace-gamma
#' @param object a \code{trace_gamma}.
#' @param alpha level.
#' @return The \code{1 - alpha} quantile.
#' @export
tg_cutoff <- function(object, alpha = 0.05) tg_ppf(object, 1 - alpha)
