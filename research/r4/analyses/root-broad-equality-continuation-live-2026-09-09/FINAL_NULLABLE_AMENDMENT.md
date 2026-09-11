# Terminal merge-only nullable-schema recovery

The first final audit verified and saved both48-episode raw/native transfer
projections, their exact frozen pairing and the terminal/selection/operation/
service-release checks. It then exited1 in aggregate(training), with
`TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'` at frozen
audit_final16.py line35: `sum(r['terminal_schema_valid'] for r in rows)`.
Historical setup-null rows legitimately carry a null schema-validity field.
No METRICS.json or final source receipt had yet been written. The frozen source
and both saved raw projections remain unchanged.

The additive wrapper counts only literal true schema-valid fields and reports a
separate unknown count. It changes no score, admission, endpoint or scientific
source. It loads the saved transfer projections by their pinned hashes instead
of calling the raw scorer/native graph reconstruction again. Original input bytes
named by those projections are hashed once more against the saved episode/result
hashes to recover the input receipt lost on process exit; paired request hashes
are recorded now. Serving prefixes are verified again at their declared bounded
length. This is a disclosed second byte-authentication pass on new transfer files,
not a second graph analysis, outcome selection or per-episode closure hash loop.
All older raw episode files and optimizer tensors remain unopened.

The initial graph/request/native/scoring assertions are supported by the saved
projections and first execution output, not counted as freshly rerun assertions.
The recovery report distinguishes its metadata/merge checks from that initial
pass. The original-null fixture reproduces the TypeError; the new fixture must
retain unobservable endpoint/admission nulls and schema_unknown=1. Future source
hashes, outputs and this amendment are pinned before recovery execution.
