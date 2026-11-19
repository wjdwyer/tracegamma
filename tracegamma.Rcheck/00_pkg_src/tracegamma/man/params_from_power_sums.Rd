\name{params_from_power_sums}
\alias{params_from_power_sums}
\title{Closed-form parameters from the eigenvalue power sums}
\usage{params_from_power_sums(lam)}
\description{
With \eqn{p_r = \sum_j \lambda_j^r}, \eqn{a = p_3/p_2},
\eqn{\nu = p_2^3/p_3^2}, \eqn{b = p_1 - p_2^2/p_3}. This is the same object
as the cumulant match in \code{\link{trace_gamma}}, written in the traces;
the two agree to floating-point rounding and each is the other's oracle.
}
\arguments{
\item{lam}{eigenvalues, strictly positive.}
}
\value{A numeric vector \code{c(a, nu, b)}.}
