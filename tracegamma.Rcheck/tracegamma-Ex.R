pkgname <- "tracegamma"
source(file.path(R.home("share"), "R", "examples-header.R"))
options(warn = 1)
base::assign(".ExTimings", "tracegamma-Ex.timings", pos = 'CheckExEnv')
base::cat("name\tuser\tsystem\telapsed\n", file=base::get(".ExTimings", pos = 'CheckExEnv'))
base::assign(".format_ptime",
function(x) {
  if(!is.na(x[4L])) x[1L] <- x[1L] + x[4L]
  if(!is.na(x[5L])) x[2L] <- x[2L] + x[5L]
  options(OutDec = '.')
  format(x[1L:3L], digits = 7L)
},
pos = 'CheckExEnv')

### * </HEADER>
library('tracegamma')

base::assign(".oldSearch", base::search(), pos = 'CheckExEnv')
base::assign(".old_wd", base::getwd(), pos = 'CheckExEnv')
cleanEx()
nameEx("bb_scale_mixture")
### * bb_scale_mixture

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: bb_scale_mixture
### Title: Berger-Boos dilation of a trace-gamma cutoff
### Aliases: bb_scale_mixture

### ** Examples

bb_scale_mixture(10, 0, 1, 4)   # 10



base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("bb_scale_mixture", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("cumulants_from_eigs")
### * cumulants_from_eigs

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: cumulants_from_eigs
### Title: Cumulants of the exact generalized chi-square
### Aliases: cumulants_from_eigs

### ** Examples

cumulants_from_eigs(rep(1, 5))   # 5 10 40



base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("cumulants_from_eigs", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("cumulants_from_traces")
### * cumulants_from_traces

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: cumulants_from_traces
### Title: Cumulants of a quadratic form from its traces
### Aliases: cumulants_from_traces

### ** Examples

cumulants_from_traces(1, 1, 1)   # 1 2 8



base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("cumulants_from_traces", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("imhof_sf")
### * imhof_sf

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: imhof_sf
### Title: Exact survival function of a generalized chi-square (Imhof 1961)
### Aliases: imhof_sf

### ** Examples

abs(imhof_sf(10, rep(1, 5)) - pchisq(10, 5, lower.tail = FALSE)) < 1e-9



base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("imhof_sf", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("kurtosis_defect")
### * kurtosis_defect

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: kurtosis_defect
### Title: Kurtosis defect
### Aliases: kurtosis_defect

### ** Examples

round(kurtosis_defect(rep(1, 5)), 12)   # 0



base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("kurtosis_defect", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("marginal_cumulants")
### * marginal_cumulants

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: marginal_cumulants
### Title: Exact cumulants of a sum of squares under a non-normal marginal
### Aliases: marginal_cumulants

### ** Examples

marginal_cumulants(5)                  # 5 10 40
cumulants_from_eigs(rep(1, 5))         # the same



base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("marginal_cumulants", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
cleanEx()
nameEx("trace_gamma")
### * trace_gamma

flush(stderr()); flush(stdout())

base::assign(".ptime", proc.time(), pos = "CheckExEnv")
### Name: trace_gamma
### Title: The trace-gamma reference distribution
### Aliases: trace_gamma

### ** Examples

tg <- trace_gamma(lam = c(4, 2, 1, 1))
tg$branch
round(tg_cutoff(tg, 0.05), 6)

w <- trace_gamma(10, 20, 0)      # Welch's two-cumulant member
w$branch



base::assign(".dptime", (proc.time() - get(".ptime", pos = "CheckExEnv")), pos = "CheckExEnv")
base::cat("trace_gamma", base::get(".format_ptime", pos = 'CheckExEnv')(get(".dptime", pos = "CheckExEnv")), "\n", file=base::get(".ExTimings", pos = 'CheckExEnv'), append=TRUE, sep="\t")
### * <FOOTER>
###
cleanEx()
options(digits = 7L)
base::cat("Time elapsed: ", proc.time() - base::get("ptime", pos = 'CheckExEnv'),"\n")
grDevices::dev.off()
###
### Local variables: ***
### mode: outline-minor ***
### outline-regexp: "\\(> \\)?### [*]+" ***
### End: ***
quit('no')
