\name{estimate_moments}
\alias{estimate_moments}
\title{Plug-in standardized moments from a pooled sample}
\usage{estimate_moments(pool)}
\description{
The deployable half of the correction: the oracle version needs moments you
do not have, this one estimates them from the same data.
}
\arguments{
\item{pool}{a numeric vector.}
}
\value{A numeric vector \code{c(mu4, mu6)}.}
