# (c) 2026 William J. Dwyer. MIT License.

#' Number of half-period panels used by the panel method
#' @export
IMHOF_PANELS <- 400

.imhof_kernel <- function(lam, x) {
  lam <- as.numeric(lam)
  theta <- function(u) 0.5 * sum(atan(lam * u)) - 0.5 * x * u
  f <- function(u) vapply(u, function(uu)
    sin(theta(uu)) / (uu * prod((1 + (lam * uu)^2)^0.25)), numeric(1))
  list(f = f, theta = theta)
}

.imhof_quad <- function(x, lam) {
  k <- .imhof_kernel(lam, x)
  0.5 + stats::integrate(k$f, 0, Inf, subdivisions = 500L,
                         rel.tol = 1e-12, abs.tol = 1e-12)$value / pi
}

.imhof_panel <- function(x, lam, panels = IMHOF_PANELS) {
  k <- .imhof_kernel(lam, x); f <- k$f; theta <- k$theta
  zero_for <- function(j) {
    target <- -j * pi; hi <- 1
    while (theta(hi) > target) { hi <- hi * 2; if (hi > 1e14) return(NA_real_) }
    stats::uniroot(function(u) theta(u) - target, c(1e-12, hi), tol = 1e-14)$root
  }
  edges <- 1e-12
  for (j in seq_len(panels)) {
    z <- zero_for(j)
    if (is.na(z) || z <= edges[length(edges)]) break
    edges <- c(edges, z)
  }
  if (length(edges) < 2L)
    stop(sprintf("no oscillation panel found for x=%.6g", x))
  # Geometric subdivision, not linear: the integrand's mass sits near
  # u ~ 1/max(lam) while the first panel can span 2*pi/x, so for small x an
  # adaptive rule started on the whole panel samples only the empty part and
  # returns ~0 -- which gives sf = 0.5 for every small x. See the Python
  # package's exact.py for the measurement that found this.
  parts <- numeric(length(edges) - 1L)
  for (i in seq_len(length(edges) - 1L)) {
    a <- edges[i]; b <- edges[i + 1L]
    n <- max(1L, min(200L, as.integer(ceiling(log10(b / a) * 12))))
    cuts <- exp(seq(log(a), log(b), length.out = n + 1L))
    parts[i] <- sum(vapply(seq_len(n), function(j)
      stats::integrate(f, cuts[j], cuts[j + 1L], subdivisions = 200L,
                       rel.tol = 1e-14, abs.tol = 1e-14)$value, numeric(1)))
  }
  s <- cumsum(parts)
  for (i in 1:10) { if (length(s) < 3L) break; s <- 0.5 * (head(s, -1) + tail(s, -1)) }
  0.5 + s[length(s)] / pi
}

#' Exact survival function of a generalized chi-square (Imhof 1961)
#'
#' \eqn{P(Q > x)} for \eqn{Q = \sum_j \lambda_j \chi^2_1}, by numerical
#' inversion. This is the law the trace-gamma approximates in closed form.
#'
#' @param x quantile.
#' @param lam eigenvalues.
#' @param method \code{"panel"} integrates between successive zeros of the
#'   integrand and accelerates the alternating series; \code{"quad"} is a single
#'   adaptive call over the half-line, which reproduces the deposited code.
#'
#' @section Accuracy:
#' \code{method = "quad"} is not reliable for small spectra, measured against
#' the exact oracle \eqn{\sum_{j=1}^m \chi^2_1 = \chi^2_m}: worst relative
#' error about 0.69 at \eqn{m = 1}, 1.0e-2 at \eqn{m = 2}, 1.1e-3 at
#' \eqn{m = 3}, falling to 1e-10 by \eqn{m = 10}. \code{method = "panel"}
#' stays below 5e-9 throughout and is slower. The default is \code{"panel"}.
#'
#' @return The survival probability, clipped to \eqn{[0,1]}.
#' @examples
#' abs(imhof_sf(10, rep(1, 5)) - pchisq(10, 5, lower.tail = FALSE)) < 1e-9
#' @export
imhof_sf <- function(x, lam, method = c("panel", "quad")) {
  method <- match.arg(method)
  v <- if (method == "panel") .imhof_panel(x, lam) else .imhof_quad(x, lam)
  min(max(v, 0), 1)
}

#' Exact distribution function of a generalized chi-square
#' @inheritParams imhof_sf
#' @return \eqn{P(Q \le x)}.
#' @export
imhof_cdf <- function(x, lam, method = c("panel", "quad"))
  1 - imhof_sf(x, lam, method = match.arg(method))

#' Exact quantile of a generalized chi-square
#'
#' @inheritParams imhof_sf
#' @param q probability in (0, 1).
#' @return The exact \code{q}-quantile.
#' @export
imhof_ppf <- function(q, lam, method = c("panel", "quad")) {
  method <- match.arg(method)
  lam <- as.numeric(lam)
  if (any(lam <= 0))
    stop(sprintf("imhof_ppf expects positive eigenvalues; got min %.6g", min(lam)))
  lo <- 1e-6; hi <- 12 * sum(lam) + 120
  f <- function(t) imhof_cdf(t, lam, method = method) - q
  flo <- f(lo); fhi <- f(hi)
  if (flo * fhi > 0)
    stop(sprintf(paste0("quantile q=%.6g is outside the search bracket [%.6g, %.6g] ",
      "(cdf spans [%.8f, %.8f]); widen the bracket"), q, lo, hi, flo + q, fhi + q))
  stats::uniroot(f, c(lo, hi), tol = 1e-10)$root
}
