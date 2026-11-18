\name{trace_gamma}
\alias{trace_gamma}
\title{The trace-gamma reference distribution}
\usage{
trace_gamma(k1 = NULL, k2 = NULL, k3 = NULL, lam = NULL, M = NULL,
            D = NULL, kurt_widen = 0, skew_shift = 0)
}
\description{
Fits \eqn{Q \approx b + a\,\chi^2_\nu} to three cumulants. Supply the
cumulants directly, or give \code{lam}, or \code{M} and \code{D}.
}
\arguments{
\item{k1}{the first three cumulants.}
\item{k2}{the first three cumulants.}
\item{k3}{the first three cumulants.}
\item{lam}{eigenvalues; if given, the cumulants are derived from them.}
\item{M}{form matrix and covariance; if given, the traces are derived.}
\item{D}{form matrix and covariance; if given, the traces are derived.}
\item{kurt_widen}{added to \eqn{\kappa_2}: the marginal-kurtosis widening.}
\item{skew_shift}{added to \eqn{\kappa_1}.}
}
\section{The two-cumulant branch is requested, not discovered}{
The fit falls to Satterthwaite's two-moment form -- Welch's reference --
when the standardized skewness does not exceed \code{SKEW_FLOOR}. No
spectrum of positive eigenvalues reaches that in practice: the skewness is
\eqn{2\sqrt{2}\,p_3/p_2^{3/2}}, minimised at equal eigenvalues, where it is
\eqn{2\sqrt{2}/\sqrt{m}}, so \code{1e-6} would need about 8e12 eigenvalues.
The branch is reached by supplying \code{k3 = 0}, which is how the paper
states the Welch special case, or a negative \code{k3}.
}
\section{A negative third cumulant is discarded, with a warning}{
An indefinite \code{M} can give \code{k3 < 0}. The standardized skewness is
then negative, the three-cumulant fit does not apply, and the third cumulant
plays no part in the answer. Inspect \code{$branch} to see which fit you have.
}
\value{An object of class \code{trace_gamma} with elements \code{a}, \code{nu}, \code{b}, \code{k1}, \code{k2}, \code{k3}, \code{branch}.}
\examples{
tg <- trace_gamma(lam = c(4, 2, 1, 1))
tg$branch
round(tg_cutoff(tg, 0.05), 6)

w <- trace_gamma(10, 20, 0)      # Welch's two-cumulant member
w$branch
}
