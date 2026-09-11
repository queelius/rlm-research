# Delegated batch-size endpoints

Exploratory design frozen before new model calls, 2026-09-08. The supervised child
was trained with five-item arrays. Fixed batches of five and sixteen both achieved
15/24 strict counts using the selected child, with 624 versus 192 calls across
both weight arms. The free-root system remained much less reliable. This followup
asks whether the learned classification/format skill transfers to singleton calls
and whole-document (64-item) calls, and where accuracy versus call/token cost breaks.

Reuse the six frozen 64-record documents, 384 source-test questions, 48 parent
task/arm/seed coordinates, original and validation-selected adapters, definitions,
native leaf first-response contract, T=0.5 and full sampling support. Each variant
contains the same 3072 repeated record assignments, not 3072 independent questions.
Use contiguous batches of size 1 or 64: 3072 or 48 model calls respectively. The
record order, parent coordinates and seeds are preserved; different prompts and
batching necessarily produce different random-sampling trajectories.

Both endpoint variants use a 1024-token output cap to leave room for 64 complete
canonical labels. Earlier five/sixteen variants used 256 tokens. Therefore this is
an operational batch strategy comparison, not a single-variable equal-budget
causal effect. Report actual tokens and truncation for every variant. No grammar,
retry, repair, fallback or dropped record; no root model or generated-code execution.
Gold remains a host-only scoring input and never enters model requests.

Primary endpoint is strict whole-document count correctness, counting any malformed
or noncanonical constituent array as failure. Also report itemwise canonical
correctness, full-array validity, coverage, truncation, calls and logical/cached/
output tokens. Infrastructure and unrun coordinates are null, not model negatives.
These already inspected public questions are exploratory, not untouched evaluation.

Compute cap: 900 seconds per variant, four HTTP workers, 60-second request timeout.
Write every raw call and completed coordinate atomically. Preserve failed attempts.
Launch whole-document first, then singleton; CPU preparation overlaps native root
rollout collection. Do not stop the shared owned inference service until all clients
finish. Freeze source, specification, every request hash and bound weights before
launch. Reuse the previously tested fixed operator/scorer without changing its files.

Implementation: add a thin parameterized layout wrapper and one focused invariant
test; demonstrate missing implementation failure, then verify coverage, pairing,
seeds, budget and absence of gold in request construction. Prepare both immutable
specifications, run them, and compare with the two completed batch strategies.
