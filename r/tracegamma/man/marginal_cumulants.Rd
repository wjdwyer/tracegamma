\name{marginal_cumulants}
\alias{marginal_cumulants}
\title{Exact cumulants of a sum of squares under a non-normal marginal}
\usage{marginal_cumulants(m, mu4 = NORMAL_MU4, mu6 = NORMAL_MU6)}
\description{
For \eqn{Q = \sum_{j=1}^m a_j^2} with \eqn{a_j} standardized i.i.d. with
standardized moments \eqn{\mu_4, \mu_6}: \eqn{\kappa_1 = m},
\eqn{\kappa_2 = m(\mu_4 - 1)}, \eqn{\kappa_3 = m(\mu_6 - 3\mu_4 + 2)}.
These are exact. The normal values return the Gaussian answer
\eqn{(m, 2m, 8m)}, which is a check worth running.
}
\arguments{
\item{m}{number of terms.}
\item{mu4}{standardized moments of the common marginal.}
\item{mu6}{standardized moments of the common marginal.}
}
\value{A numeric vector \code{c(k1, k2, k3)}.}
\examples{
marginal_cumulants(5)                  # 5 10 40
cumulants_from_eigs(rep(1, 5))         # the same
}
