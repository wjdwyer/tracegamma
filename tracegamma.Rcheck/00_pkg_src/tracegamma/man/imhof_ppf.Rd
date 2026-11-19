\name{imhof_ppf}
\alias{imhof_ppf}
\title{Exact quantile of a generalized chi-square}
\usage{imhof_ppf(q, lam, method = c("panel", "quad"))}
\description{
Exact quantile of a generalized chi-square
}
\arguments{
\item{q}{probability in (0, 1).}
\item{lam}{eigenvalues.}
\item{method}{\code{"panel"} integrates between successive zeros of the integrand and accelerates the alternating series; \code{"quad"} is a single adaptive call over the half-line, which reproduces the deposited code.}
}
\value{The exact \code{q}-quantile.}
