\name{kurtosis_defect}
\alias{kurtosis_defect}
\title{Kurtosis defect}
\usage{kurtosis_defect(lam)}
\description{
\eqn{\Delta\gamma_2 = 12(p_2p_4 - p_3^2)/p_2^3}, the fourth-cumulant
mismatch. Non-negative by Cauchy-Schwarz, and zero exactly at equal
eigenvalues, where the trace-gamma is not an approximation at all.
}
\arguments{
\item{lam}{eigenvalues.}
}
\value{A single number.}
\examples{
round(kurtosis_defect(rep(1, 5)), 12)   # 0
}
