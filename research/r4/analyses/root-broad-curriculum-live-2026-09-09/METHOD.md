# BROAD16 independent analysis method

Frozen before this analyst reads any BROAD16 live outcome. The parent has disclosed only launch/service activity and that a validation directory exists, not scores. Earlier campaigns, curriculum construction and the bounded source review are already known; this is not a claim that the research direction was selected without prior evidence.

## Question and fixed estimand

Does this original-start, 16-update broad root-only curriculum improve exact aggregation outcomes over its original root on the prescribed paired transfer coordinates, with the same frozen child? The primary trained policy is **fixed final16**. The earliest validation maximum is descriptive and must not replace it. A stopped campaign without final16 cannot supply this primary comparison; completed lower-step training/validation remains reportable as partial evidence.

The planned run has 384 training episodes (16 rounds × three task groups × eight samples), 80 validation episodes (the same 16 coordinates at steps 0/4/8/12/16), and 96 transfer episodes (48 original/final pairs). Training uses 24 context groups across 16/32/64 records, with each group visited twice under different targets. Validation has eight different contexts. Transfer contains 15 distinct context groups, not 48 independent items or 96 independent observations.

Report the primary paired exact-result vector separately for:

- Composition, 64 records: six contexts, trained requested target (12 pairs) and reserved requested target (12 pairs), with their within-context contrast. Reserved DESC/ABBR targets are known semantic classes, not novel labels.
- Length, 128 records: four contexts, eight pairs.
- Length, 256 records: two contexts, four pairs.
- Leaf-test-exposed, 32 records: three contexts, twelve pairs; keep this exposure category separate from child-training-supported transfer.

For each stratum report original/final exact successes, planned and observed denominators, complete-pair gains/losses/ties, mean paired binary difference, and every context-group summary. Retain task/seed repeats nested within contexts. Any all-transfer total is descriptive only and does not turn these strata into a new pooled benchmark. No significance or population-generalization claim is prespecified for these few exposed clusters. The treatment also changes breadth, update count and rollout volume relative to earlier campaigns; cross-campaign differences are not a breadth-only causal effect.

## Outcome and missingness rules

Authenticate the immutable planned task, context, question, seed, gold/scorer identity and child binding on both sides of every pair. Read raw terminal output/recorded scoring and recompute the existing exact metric without repair, code execution, new answer extraction or new reward rules. An observed, admitted wrong/malformed answer remains the recorded task failure. A missing coordinate, infrastructure exception, unobservable terminal or the existing narrow overflow exclusion remains separately classified with `exact = null` when the existing scoring contract does not yield an admitted result. Distinguish collection stops, global/per-episode budgets, integrity failures and model errors. Preserve both raw score and admission status; do not turn an excluded raw zero into an admitted negative.

Observed successes/planned may be shown as a clearly labeled coverage-sensitive lower bound, never as an uncensored success-rate estimate. Complete-pair effects use only observed/admitted pairs and state their denominator, with missing-side counts. No imputation, reroll, retries, selection of favorable samples or substitution of an intermediate checkpoint.

## Training, lineage and native provenance

Check original adapter `857a7ce6…` with empty Adam/zero inherited updates, fixed child `c32de129…`, seed 981268001 and new campaign namespace. For each committed round, authenticate its predecessor adapter, fresh planned/executed rows, export/group identity, checkpoint members, saved input binding and correction capture. Check exactly one finite nonzero full-batch update, adapter delta, Adam cursor/order and RNG continuity, including 8→9→16. Count all attempted/completed/admitted/excluded/mixed trajectories, task groups, root turns and action tokens. Absence of mixed groups is a training-signal stop, not an applied update.

Use recorded native token/role provenance and root-only masks to verify root action credit; child/tool/observation tokens are uncredited. Check current-policy/role bindings, actual request sampling, causal action IDs/masks/old log probabilities, guard results and saved correction statistics. Sampled-action likelihood summaries are not entropy. Do not infer correct child semantics, coverage or tool consumption from a successful final count, unparsed code, or lexical marker absence. Static markers may be summarized only with unparsed/missing counts explicitly retained.

## Costs and operational state

Separate service startup/release, rollout collection, optimizer work, CPU authentication/analysis, cleanup and total accepted-operation elapsed time. Record physical root/child/provider calls; logical prompt, cached prompt, uncached prompt and completion/action tokens, including failed calls where captured. Recover cache counts from native wire usage when present, without treating missing cache information as zero. Sum only known values and report missing-value counts. Repeated full prefixes and child calls count each time. Provider-call duration sums may overlap; they are not wall time or GPU utilization.

Authenticate terminal/STOP, selection/final and parent child-exit/timeout/release records. Keep launcher/lifecycle failures distinct from policy failures. Record post-release scheduling-lock/CPU tail if observable; do not acquire a GPU/operation lock or query/signal processes. Run caps remain 18000 work, 18120 inclusive and 18150 outer seconds, with inherited per-stage limits; measured elapsed time is reported even on STOP.

## Incremental execution and publication plan

1. On a parent milestone trigger (4/8/12/16) or STOP/terminal trigger, inspect only finalized new stages and immutable input identities. No permanent watcher or polling loop. An unfinished stage is pending, not missing at final.
2. Build an analysis-owned cache keyed by resolved artifact path and SHA-256. Authenticate shared immutable closures once per audit lineage, not once per episode. Reuse the source-review identities and previously sealed stage projections; reject a changed already-audited artifact rather than silently rescoring it. Do not repeatedly deserialize checkpoints or rescan old traces.
3. Project each newly complete stage once into analysis-owned rows with exact source paths/hashes, nulls and integrity findings. Stage receipts record which files were read. Final analysis merges those receipts and audits only newly ready terminal/transfer artifacts.
4. Publish immutable milestone files in separate stage directories; label them interim and do not claim transfer efficacy from training or validation. At terminal publish `REPORT.md`, `METRICS.json`, `SOURCES.json` and a hash manifest. If output is not yet ready, return that filesystem-readiness finding without waiting indefinitely. Material integrity failures go to the parent promptly.

All implementation/analysis is CPU-only, additive under this analysis directory, and read-only with respect to research sources, inputs and live outputs. No GPU/model calls, service actions, signals, generated-code execution, locks, source edits, acceptance changes or subagents. This method does not authorize new inference.
