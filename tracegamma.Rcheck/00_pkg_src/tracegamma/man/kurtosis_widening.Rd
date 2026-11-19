\name{kurtosis_widening}
\alias{kurtosis_widening}
\title{Marginal-kurtosis widening of the second cumulant}
\usage{kurtosis_widening(M_diag, kappa4)}
\description{
\eqn{\sum_i M_{ii}^2 \kappa_4(a_i)}; pass as \code{kurt_widen} to
\code{\link{trace_gamma}}.
}
\arguments{
\item{M_diag}{diagonal of the form matrix.}
\item{kappa4}{fourth cumulant of each input.}
}
\value{A single number.}
