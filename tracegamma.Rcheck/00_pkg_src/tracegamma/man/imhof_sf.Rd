\name{imhof_sf}
\alias{imhof_sf}
\title{Exact survival function of a generalized chi-square (Imhof 1961)}
\usage{imhof_sf(x, lam, method = c("panel", "quad"))}
\description{
\eqn{P(Q > x)} for \eqn{Q = \sum_j \lambda_j \chi^2_1}, by numerical
inversion. This is the law the trace-gamma approximates in closed form.
}
\arguments{
\item{x}{quantile.}
\item{lam}{eigenvalues.}
\item{method}{\code{"panel"} integrates between successive zeros of the integrand and accelerates the alternating series; \code{"quad"} is a single adaptive call over the half-line, which reproduces the deposited code.}
}
\section{Accuracy}{
\code{method = "quad"} is not reliable for small spectra, measured against
the exact oracle \eqn{\sum_{j=1}^m \chi^2_1 = \chi^2_m}: worst relative
error about 0.69 at \eqn{m = 1}, 1.0e-2 at \eqn{m = 2}, 1.1e-3 at
\eqn{m = 3}, falling to 1e-10 by \eqn{m = 10}. \code{method = "panel"}
stays below 5e-9 throughout and is slower. The default is \code{"panel"}.
}
\value{The survival probability, clipped to \eqn{[0,1]}.}
\examples{
abs(imhof_sf(10, rep(1, 5)) - pchisq(10, 5, lower.tail = FALSE)) < 1e-9
}
