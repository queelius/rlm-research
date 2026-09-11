# What would make these results misleading

This document is the claim boundary for the dossier. It separates contradictions worth investigating from ordinary uncertainty and from unfinished work. Detailed observations are in [Findings](FINDINGS.md); recommendations are in [Next experiments](NEXT_EXPERIMENTS.md).

## Independence and selection

- **Repeated outputs are not fresh data.** The 1,536 TREC predictions in a fixed-composition cell reuse384source questions four times. The24aggregate coordinates use onlysix contexts. The root pilot's eight validation trajectories use two contexts. Confidence intervals treating predictions or trajectories as independent would be spuriously narrow. Future resampling should cluster by source group/context, with training-seed replication reported separately.
- **New compositions are not untouched source questions.** The new TREC contexts recombine component-test questions. That tests composition under a new root prompt, not generalization to a new semantic dataset. Historical exposure and model-pretraining overlap cannot be ruled out for public TREC, SST-2 or MRCR.
- **Validation and test are differently constructed.** E01 validation intentionally excluded inspected historical material and has different subtype composition. Its83%versus97% gap is not a clean estimate of validation overfitting or ordinary sampling noise. Known normalized train/test duplicates were removed; unknown exposure was not magically eliminated.[^1]
- **Checkpoint names are not interchangeable.** Old child SFT was selected on validation. A/B are fixed-final epoch2. Campaign step2 is evaluated, step3 is last committed, and no campaign checkpoint was selected or final-tested. Later retrospective preference must not rewrite those decisions.
- **Adaptive studies used development readouts.** They preserve context-group separation and two optimization seeds, but taught routines, familiar renderer families and repeated development iteration narrow the transfer claim. Strong benchmark-specific bootstrap is not broad reasoning evidence.[^19][^24][^26]

## Endpoints that can move for different reasons

| Tempting statement | Why it overstates the evidence | Required distinction |
|---|---|---|
| “SFT adds118semantic correct answers.” | Strict whole-array invalidation recovered some already-correct siblings. | Strict355→473,canonical374→473,alias376→473; retain pairedchanges. |
| “Schema fixes reasoning.” | Trained singleton first-label choices were identical; only surplus output was removed. | Canonical decision, vocabulary, cardinality and aggregate validity. |
| “A/B have0long-batch accuracy, so every label is wrong.” | Invalid cardinality makes alignment unavailable; many prefixes look correct. | Primary unusability versus explicitly post-hoc partial-prefix diagnostic. |
| “Better final count means better decomposition.” | False positives/negatives cancel; roots can ignore reports or recover independently. | Component evidence, report-implied answer, root adherence and true answer. |
| “No admitted batch means no policy variation.” | Shape-based admission excluded completed negatives in a prior run. | Measured reward variance before/after eligibility, and null reasons. |
| “All trace errors are failed episodes.” | Overlong child requests can be recovered within a completed wrong root episode. | Failed provider attempt, recovered episode, unobservable terminal outcome. |
| “Three committed RL steps demonstrate learned orchestration.” | One noisy validation comparison, no step3readout, no selected/finaltransfer. | Update integrity versus improvement, replication and transfer. |

These are not hypothetical caveats: each has a concrete local example.[^1][^2][^3][^5][^6][^7][^8][^9]

## Main unresolved contradictions

**Small-batch skill versus64-output failure.** Old SFT is very accurate in small batches and at the beginning of a long batch. Schema fixes cardinality but not late labels. Mixed-size B stops cleanly but early. An earlier synthetic8B setup handles64well. The completed representation and rotation controls now support a correspondence/position mechanism; the template control weakens serialization as a sufficient explanation. Output-state maintenance, task familiarity and representation conventions remain distinct possibilities, not measured attention mechanisms.[^3][^4][^20]

**Strong fixed aggregation versus weak autonomous gains.** Fixed5trained reaches15/24 while freely acting trained-child RLM reaches6/24. Root parsing/coverage failures are observed, but the fixed and autonomous strategies differ in budget, prompt, tool behavior and number of calls. Moreover, first-root sampling differs before children in many nominally paired runs. “All the gap is bad aggregation” is unsupported. Shared-prefix counterfactuals can separate consumption from planning.[^2]

**Adaptive efficiency versus semantic simplification failure.** Filtering input with an unchanged label task works well; converting it to binary target/other is much worse. This argues against optimizing prompt length or label count in isolation. The contract itself may select a different learned task. A future efficiency claim needs whole-system costs and matched semantics.[^19][^21][^22]

**Report adherence versus true correctness.** Binding makes roots use reports but propagates wrong ones. Revision can harm valid evidence and has sometimes produced no candidate capable of repairing the final answer. “Use reports more” and “revise uncertain reports” are not universally helpful policies.[^28][^30]

## Compute and backend comparability

Training exposures, optimizer steps, prompt tokens, supervised tokens, inference requests and wall time are different budgets. A/B use two record exposures like all-five SFT but substantially more optimizer steps and different packed lengths. The earlier matched-controller campaign consumed19.85aggregateGPU-hours; comparing that directly with705seconds of one leaf-training loop would mix qualification, loading, screening and evaluation accounting.

The recent fixed-batch calls used different output caps at different sizes, concurrent workers and warm caches. Logical input savings are real request-level facts, but not automatically measured GPU FLOPs, isolated latency or dollar savings. Summed episode duration is not service wall time. Inherited retry capability does not establish additional inference cost because idempotent replay can return a previous response.

HF and vLLM need not produce identical probabilities with the same disk adapter. BF16 inference casting, scheduling and batching can change trajectories; the unchanged replay demonstrates the consequence but does not isolate its numerical cause. Exact semantic request objects are weaker evidence than physical prompt-token equality. One alleged backend-only control had different tool JSON key order and therefore different token IDs.[^4][^5][^32]

The actual root update uses conditional token-level truncated importance weights. Its token guards and exact recorded Adam progression do not establish an unbiased trajectory-level policy gradient. Observation tokens have zero direct loss but still influence representations causally. The claim is a faithfully implemented declared exploratory objective, not proven optimal credit assignment.[^7]

## Instrument boundaries, licensing and preservation

The main Responses-only kernel, pinned Prime/nano environment, standalone leaf collectors and sibling benchmark runners have different protocols and failure semantics. A defect in unused core cannot be blamed for an executed nano result. Conversely, a fixed core does not silently fix a frozen campaign exporter. Source hashes and actual request routes must accompany any cross-run comparison.[^7][^33][^34]

TREC underlying licensing is not established by the local training audit. SST-2's official dataset card records an unknown underlying license; the loader's Apache2.0 license is a separate software fact, not permission inferred for the corpus. The sources are public and provenance-pinned, not certified absent from pretraining. This limits distribution and generalization claims; it does not justify inventing a license.

Older reports and stop markers remain unchanged. The round04stop's diagnosis is superseded by a later authenticated overlength finding, not erased. New leaf controls are incorporated from primary aggregate files; their separately reported request-level crosscheck was not yet published at cutoff. No continuation, fresh campaign final or transfer is fabricated.

[^1]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Child"
[^2]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Composition"
[^3]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Batch"
[^4]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Mixed-size"
[^5]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Pilot"
[^6]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Terminal"
[^7]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Actual"
[^8]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Reward"
[^9]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Admission"
[^19]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Matched"
[^20]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Synthetic"
[^21]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Input"
[^22]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Binary"
[^24]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Layout"
[^26]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Controller"
[^28]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Binding"
[^30]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Revision"
[^32]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Serving"
[^33]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Core"
[^34]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Runtime"
