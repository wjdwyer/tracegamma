\name{bb_scale_mixture}
\alias{bb_scale_mixture}
\title{Berger-Boos dilation of a trace-gamma cutoff}
\usage{bb_scale_mixture(core_cutoff, ks, rbar, k)}
\description{
The guaranteed statistic rejects when
\eqn{Q_{obs} > \exp(k_s\sqrt{\bar r/k}) \times} cutoff, so its law is a
scale mixture of the trace-gamma core over the log-chi-square dispersion --
the Berger-Boos scale mixture.
}
\arguments{
\item{core_cutoff}{the trace-gamma cutoff.}
\item{ks}{the Berger-Boos constant for the design.}
\item{rbar}{the design radius.}
\item{k}{number of groups.}
}
\section{Scope}{
The statistic belongs to a different paper in the series, not to the
trace-gamma paper, and nothing in the trace-gamma propositions depends on
it. Read that paper before relying on the constant \code{ks}.
}
\value{The inflated cutoff.}
\examples{
bb_scale_mixture(10, 0, 1, 4)   # 10
}
