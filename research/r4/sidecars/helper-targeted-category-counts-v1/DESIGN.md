# Task-targeted helper outputs: count one category

Status: design only, awaiting MAIN approval. No implementation, GPU launch, training or queued-source mutation is authorized by this document.

## Question and fixed comparison

When a root task needs the count of one specified category, does a target-or-other helper map provide better task-relevant information than deriving the same decisions from a full-category map? The host computes counts deterministically from actual returned maps; no root generation or gold substitution occurs.

Use exactly the already frozen256 records in `helper-unseen-generalization-panel-v1`:128 TREC-test and128 AGNews-test records, each dataset in its existing order, partitioned into eight16-record blocks. Same unchanged c32, tokenizer wrapper, category definitions, keyed schema order and temperature0 throughout one fresh batch-invariant-v4 native service. All labels are predeclared targets, never selected from model outputs or error analysis.

| Dataset | Blocks | Targets per block | Full-map calls | Target-map calls | Target count tasks |
|---|---:|---:|---:|---:|---:|
| TREC |8|6|8|48|48|
| AGNews |8|4|8|32|32|
| Total |16|—|16|80|80|

There are96 physical calls,1536 planned physical label slots, and1280 binary decisions per comparison arm after deriving all target decisions from the16 reusable full maps. These are related decisions on256 unique records, not independent samples.

## Prompt and output treatment

Full arm: preserve the existing16-record full-category prompt and schema exactly, using all six TREC or four AGNews labels; fresh seeds are fixed below. Target arm: preserve every category definition and the primary-answer/topic rule, but replace the output instruction/schema with two allowed values in this order: `["<actual target>", "other"]`. The runtime request contains the literal target label, not the angle-bracket notation.

Add: “For this request, return the target label only when the record belongs to that category under the complete definitions above. Return `other` for every remaining category; `other` is the union of [the other labels in original order], not an additional semantic category. Return one keyed answer for every supplied record.” State the exact target explicitly. Keep all16 records, their order and IDs unchanged. Gold remains in the host-only map; the target identifies a user task, not the record's true label.

TREC target order: human being, location, abbreviation, entity, description and abstract concept, numeric value. AGNews: World, Sports, Business, Sci/Tech. Independent targeted requests may disagree or mark several categories positive; do not reconcile them into a forced full classification. Report this consistency diagnostic separately.

## Schedule, provenance and operating bounds

Seeds are fixed before scoring:202609120820 for every TREC request and202609120821 for every AGNews request, both arms; temperature0, max1024 new tokens and unchanged8192-token service context. Check every frozen prompt plus1024 fits before READY; no post-result shortening or cap changes.

For block index0–7, alternate dataset order (TREC then AGNews on even blocks, reverse on odd blocks). Within a dataset/block, cyclically rotate its original target order by the block index; insert the one full-map call at position `block_index mod (K+1)` among theK target calls. This fixed schedule spreads baseline/target ordering and cache exposure. Evaluate every target even if early results are poor.

Proposed future sidecar: `helper-targeted-category-counts-v1`. Inspiration is the sealed size evaluator's request freezing, strict keyed validation and per-call audits; do not modify its336-call owner or any other queued closure. Use the sealed batch-invariant-v4 service and require its engine pre-exec attestation. Fresh full-map baseline16 calls are mandatory: older flag-off baselines and different-order size-study responses are not pooled.

Owner cap900seconds, external timeout1000seconds, MAIN-only shared-GPU-flock launch. Freeze PUBLIC/HOST_GOLD provenance, model/config/runtime hashes,96 ordered request bodies/token IDs/schemas,80 target-task links and seeds before generation. Each call saves REQUEST, raw RESPONSE if returned, validated CALL and atomic progress immediately. No retries or outcome-based stopping; unavailable and cap-unattempted slots remain explicit. Release the single service on success, exception or signal.

## Matched scientific endpoints

For each block/target, derive full-arm positives by `full_label == target`; targeted positives by `binary_label == target`. Compare both against the same host predicate `gold_label == target`.

Report TP/FP/TN/FN and missing positive/negative slots per target; aggregate each target across its128 dataset records for positive recall, specificity and balanced accuracy `(recall + specificity)/2`, then macro-average across dataset targets. Each dataset label has positives in the frozen panel. For individual blocks with no positives or no negatives, the corresponding rate is undefined, not zero or perfect. Do not headline negative-dominated binary accuracy or compare it to full-label accuracy. Missing predictions receive planned-denominator recall/specificity bounds, not confident negative labels.

For all80 block/target tasks, report each predicted/gold count, exact-count success, signed count error and absolute count error. Headline exact-count totals and summed absolute error separately for TREC48 and AGNews32; show summed signed error only as a bias diagnostic because cancellation is possible. Invalid maps produce unavailable count tasks, never count0. A missing full map affects allK derived target tasks but remains one failed physical call. Provide availability/bounds and paired task wins/losses; do not treat reused baseline decisions or80 related tasks as independent inferential trials.

## Fair cost views

Single requested target: compare that target call's observed cost with one full-map call for the same block. Under a predeclared uniform choice amongK targets, expected targeted cost is the average of theK measured targeted-call costs; full-map cost is paid once. Report this separately by dataset, with total input+output tokens, cache tokens and calls. Keeping all definitions and adding a target instruction may increase input tokens despite shorter outputs.

All categories requested: compare the sum ofK targeted calls against the single reusable full map. Never charge the baseline mapK times in physical totals. Report actual experiment costs separately:16 full calls versus80 targeted calls. Returned-usage subtotals, unknown-usage call counts and requested input tokens remain distinct. Timings reflect this warm shared-service schedule, not cold-start single-query latency or whole-RLM cost; report startup and owner time separately.

## Expected information and prospective decision

The experiment distinguishes improved target discrimination from a mere negative-label prior, and task-count improvement from apparent full-label/binary metric differences. It also exposes where specialization is useful only for one requested target while a reusable full map dominates multiple queries.

Proposed dataset-specific promotion rule for a subsequent genuine-root count ablation: targeted exact-count success increases, summed absolute count error decreases, and macro target-balanced accuracy does not decrease, with complete comparable availability. For a uniform single-target workload, require observed total-token cost no more than1.25 times the full-map baseline; this is an explicit proposed25% accuracy-for-cost budget, not a measured threshold. MAIN may revise this budget before implementation, never after reading outcomes. Otherwise retain the result as negative or tradeoff evidence without claiming improvement. Any promoted lead requires an independent sample/replication; do not pick favorable categories post hoc.

This panel is now research-exposed. It was absent from verified c32 SFT optimizer inputs and the new32-record updates, not necessarily base pretraining. No selector training, data expansion, general recursion claim or full-label classification superiority is inferred. Approval of this design is separate from implementation and GPU launch authority.
