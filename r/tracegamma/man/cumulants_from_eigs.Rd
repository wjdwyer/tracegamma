\name{cumulants_from_eigs}
\alias{cumulants_from_eigs}
\title{Cumulants of the exact generalized chi-square}
\usage{cumulants_from_eigs(lam)}
\description{
For \eqn{Q = \sum_j \lambda_j \chi^2_1} these are exact, not approximate.
}
\arguments{
\item{lam}{eigenvalues.}
}
\value{A numeric vector \code{c(k1, k2, k3)}.}
\examples{
cumulants_from_eigs(rep(1, 5))   # 5 10 40
}
