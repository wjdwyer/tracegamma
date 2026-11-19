\name{cumulants_from_traces}
\alias{cumulants_from_traces}
\title{Cumulants of a quadratic form from its traces}
\usage{cumulants_from_traces(t1, t2, t3)}
\description{
Lancaster's identity \eqn{\kappa_r = 2^{r-1}(r-1)!\,t_r} at \eqn{r = 1,2,3},
where \eqn{t_r = tr((MD)^r)}.
}
\arguments{
\item{t1}{the traces.}
\item{t2}{the traces.}
\item{t3}{the traces.}
}
\value{A numeric vector \code{c(k1, k2, k3)}.}
\examples{
cumulants_from_traces(1, 1, 1)   # 1 2 8
}
