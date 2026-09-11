# Free-emitted source-ID correspondence

The falsifiable question is whether the large source-correspondence advantage observed under exact
ID grammars survives when released Qwen3-4B must emit the IDs itself. This is an exposed-context
mechanism study, not a fresh-data replication.

The 96-call factorial crosses matching-ID objects, constant-tag objects and plain label arrays with
free versus exact decoding on all eight frozen fresh96 AG News/SST-2 contexts and both original
seeds. All calls use the same no-adapter checkpoint, one same-service stage, temperature 0.5,
full-support sampling, four workers and a 3,072-token cap. A free/exact pair differs only by removal
of `structured_outputs`.

Primary reporting uses the planned denominator. A completed malformed or invalid policy response is
observed and contributes zero strict correct labels; only missing/infrastructure outcomes are NULL
and receive explicit bounds. Position is never reconstructed from IDs. Literal ID position matches,
duplicates, omissions, extras, field order and conditional label-only correctness remain distinct
secondary diagnostics.

Free matching versus free constant is not a single-variable ID-semantic contrast because distinct
IDs are harder and more expensive to emit than one repeated tag. The within-arm free-versus-exact
contrast cleanly tests decoder support; the cross-arm free contrast is descriptive.

