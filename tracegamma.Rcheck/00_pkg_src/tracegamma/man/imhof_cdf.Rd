\name{imhof_cdf}
\alias{imhof_cdf}
\title{Exact distribution function of a generalized chi-square}
\usage{imhof_cdf(x, lam, method = c("panel", "quad"))}
\description{
Exact distribution function of a generalized chi-square
}
\arguments{
\item{x}{quantile.}
\item{lam}{eigenvalues.}
\item{method}{\code{"panel"} integrates between successive zeros of the integrand and accelerates the alternating series; \code{"quad"} is a single adaptive call over the half-line, which reproduces the deposited code.}
}
\value{\eqn{P(Q \le x)}.}
