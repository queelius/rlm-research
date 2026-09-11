# Operator-dose audit: availability arithmetic correction

The sealed audit report's aggregate NULL count is corrected from 23/96 to **27/96**. Fixed6 has
31/48 native finals and 17 NULLs; fixed24 has 38/48 native finals and 10 NULLs. At the paired level,
27 coordinates have both finals, 4 fixed6 only, 11 fixed24 only, and 6 neither.

No score or inference changes: strict results remain 5/48 and 29/48 on the planned denominators,
with the previously reported bounds unchanged. See the additive analysis-side
`AVAILABILITY_ERRATUM.md`; original sealed artifacts remain untouched.
