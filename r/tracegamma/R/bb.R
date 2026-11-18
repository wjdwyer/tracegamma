# (c) 2026 William J. Dwyer. MIT License.

#' Berger-Boos dilation of a trace-gamma cutoff
#'
#' The guaranteed statistic rejects when
#' \eqn{Q_{obs} > \exp(k_s\sqrt{\bar r/k}) \times} cutoff, so its law is a
#' scale mixture of the trace-gamma core over the log-chi-square dispersion --
#' the Berger-Boos scale mixture.
#'
#' @section Scope:
#' The statistic belongs to a different paper in the series, not to the
#' trace-gamma paper, and nothing in the trace-gamma propositions depends on
#' it. Read that paper before relying on the constant \code{ks}.
#'
#' @param core_cutoff the trace-gamma cutoff.
#' @param ks the Berger-Boos constant for the design.
#' @param rbar the design radius.
#' @param k number of groups.
#' @return The inflated cutoff.
#' @examples
#' bb_scale_mixture(10, 0, 1, 4)   # 10
#' @export
bb_scale_mixture <- function(core_cutoff, ks, rbar, k)
  exp(ks * sqrt(rbar / k)) * core_cutoff
