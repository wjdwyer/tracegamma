\name{print.trace_gamma}
\alias{print.trace_gamma}
\title{Print a trace-gamma fit}
\usage{\method{print}{trace_gamma}(x, ...)}
\description{
Prints the fitted parameters \code{a}, \code{nu} and \code{b}, the three
cumulants they were matched to, and the branch that was taken -- either the
three-cumulant fit or the two-cumulant Welch limit. The branch matters: on the
Welch branch the third cumulant has been discarded.
}
\arguments{
\item{x}{a \code{trace_gamma} object.}
\item{...}{further arguments, ignored.}
}
\value{
\code{x}, invisibly.
}
