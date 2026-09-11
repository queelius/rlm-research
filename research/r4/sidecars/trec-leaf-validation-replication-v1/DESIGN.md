# Clean-validation replication of leaf instructions and constraints

Declared 2026-09-08 before any inference on these300 validation questions.

Question: do the development improvements from category definitions and decoder
constraints persist on source-question groups outside the inspected OOLONG pool?
This is exploratory replication on validation, not a pristine confirmatory test.

Use exactly the300 validation groups in sibling
`trec-leaf-split-provenance-v1/PROPOSED_SPLIT.json`, SHA256
`3f5f648488d512d2052b9f3d57c02e030af8e939ca363998c07a556a47d7f457`.
Authenticate the source train bytes and normalization via that sidecar's inventory.
Do not read or evaluate the489 source-test groups for this experiment.

Keep the original leaf72 system message, tool schema, user label-list prefix,
category definitions, four arms, temperature0.5, top_p1, top_k-1, min_p0 and
256-output-token cap unchanged. The model is original Qwen3-4B-Instruct-2507 with
the original zero-update rank8 adapter, not either newly trained checkpoint.

Sort validation question groups by their SHA256, choose the declared first source
representative, and form60 fixed batches of five. Use three new sample seeds
980260100,980260101,980260102, shared within every four-arm batch/repetition.
Rotate arm order by batch plus repetition index. Total720 model requests and
3600 requested labels, but only300 unique question groups and60 shared batches.
Concurrency4, per-request timeout30seconds, total dispatch cap600seconds.
No retries, tool execution, answer fallback, or silent dropping of constraints.
If the first live API error occurs, stop new dispatch and preserve inflight results.

Primary: canonical per-record accuracy with paired per-question contrasts,
summarized across repetitions. Also report strict array vocabulary/cardinality,
macro/classwise accuracy, format failures, cost, and the explicitly separate
DESC-alias sensitivity. Report attempted and observable denominators separately;
errors are null, not invented predictions. Confidence intervals, if computed,
must group repeated predictions together; do not treat3600 labels as independent.
Only five validation questions are abbreviations, limiting classwise precision.

Freeze a new source/spec/attempt and authenticate actual live original4B alias.
Reuse pure old request/scoring helpers if useful; never modify the frozen leaf72
driver or its completed output. Replace its hardcoded89 denominators honestly.
Checkpoint every request with group/source IDs, request+response, tokens, seed,
arm, exact weights and source hashes. Rootless MRCR may share this inference
server; wall-time comparisons are therefore descriptive, not isolated benchmarks.

Promote the observed instruction/contract intervention to a full-RLM development
comparison if its benefit persists. A null/reversed replication revises that plan.
Do not claim schema improves only formatting: it changes the sampling distribution
and may change semantic decisions as well. Questions for user review are recorded,
not blocking. No repository production code or home configuration is changed.
