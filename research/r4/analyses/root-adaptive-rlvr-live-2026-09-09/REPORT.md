# Seven real updates, unchanged mid-run validation, no final-eight readout

The adaptive root campaign stopped according to its frozen rule after seven optimizer updates. Its eighth rollout generation had no within-prompt reward variation: one task was correct in all eight samples, while the other had seven admitted wrong samples and one infrastructure-null. There was therefore no eligible eighth update. **The planned fixed-final-eight policy and its validation/transfer results do not exist.** Checkpoint seven is the last saved policy, not a retrospectively selected final policy.

The only completed paired post-update evaluation is validation at update four: **2/8 → 2/8**, one win, one loss and six ties across four contexts. Final-answer protocol compliance improved, but exact counting accuracy did not. The result neither demonstrates an overall adaptive-planning gain nor establishes that the last saved policy has no benefit: that policy was not evaluated on the held-out readouts in this run.

This report independently reconstructs outcomes, native evidence and checkpoint accounting. The auditor did not author this adaptive RL implementation, but authored/shared earlier SFT and harness components and reviewed the integration. [Main method](METHOD.md) and [auditor method](AUDITOR_METHOD.md) were written after launch and before this auditor opened outcomes; this is not prelaunch preregistration. The later map-to-count screen is explicitly [posthoc](SECONDARY_DIAGNOSTIC.md).

## What actually ran

- Scientific run: [attempt-001](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-adaptive-rlvr-v1/outputs/attempt-001/"), campaign `51afee1b…`, initial root `efab2913…` (fixed interface-SFT checkpoint four), fresh campaign Adam. The child remains `c32de129…` throughout.
- Planned: 128 fresh training episodes, 24 validation episodes at policies 0/4/8, and 32 transfer episodes at policies 0/8: 184 total. Recorded: **160**. All 128 training episodes completed collection; validation eight and transfer eight account for the 24 unrun episodes.
- Seven optimizer commits, 95 selected training episodes, **68,008 credited root-action tokens in 572 turns**. Child and observation loss tokens are zero. The child adapter is not loaded into the training model.
- [Original STOP](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-adaptive-rlvr-v1/outputs/attempt-001/STOP-19319d28dd474bc2bf06b366e991b5dd.json"), SHA `ecd1c7f4221ae83017b748c3b7ad75129eadeb53df9073b78f94efbd2a296de2`, records the no-mixed-group reason and last policy. It remains unchanged; there was no reroll or substitute eighth update.

The public allocation contains 896 source-question groups: 384 root-training, 192 validation, 64 query-transfer and 256 length-transfer groups. Training uses eight contexts (four each at 32/64 records), validation four (two each at 32/64), query transfer two 32-record contexts, and length transfer two 128-record contexts. These groups are disjoint within this allocation but are supported by the fixed child's earlier supervised TREC training. Query transfer changes the requested category/family, not the domain. Length 128 exceeds the root-training maximum 64. Public/pretraining exposure remains unresolved; these are not globally unseen texts.

The unit is a planned task/seed coordinate nested within a source context—not an independent question or an independent context for every rollout. Fresh training-round scores must not be read as a paired learning curve.

## Training happened, but the eighth group was uninformative for this objective

| Generation | Strict correct / 16 collected | Admitted | Selected for update | Credited root tokens | Actual Adam cursor |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 4 | 15 | 15 | 7,575 | 1 |
| 2 | 6 | 16 | 16 | 9,479 | 2 |
| 3 | 5 | 16 | 8 | 5,810 | 3 |
| 4 | 11 | 16 | 16 | 9,422 | 4 |
| 5 | 3 | 16 | 8 | 7,961 | 5 |
| 6 | 4 | 16 | 16 | 17,366 | 6 |
| 7 | 8 | 16 | 16 | 10,395 | 7 |
| 8 | 8 | 15 | 0 | 0 | No update |

Overall training endpoints are 49/128 correct, or 49/126 among admitted trajectories. Of the 126 admitted episodes, 31 belong to homogeneous groups and contribute no update; two further collected episodes are infrastructure-null. All 41 training successes before generation eight are among the 95 selected episodes. The eight successes in the final generation are not silently incorporated into RL.

Generation eight's `train-03/single_user` task has gold 2 and eight exact `Answer: 2` replies. Its `train-07/global` task has gold 11 and no admitted correct answer: validly formatted wrong values include 10, 12, 16 and 19, alongside protocol failures and one null. This is not aggregate reward saturation at success: one task is solved while the other remains unsolved. Per-prompt normalization correctly does not turn this contrast between different tasks into a within-task advantage.

[Checkpoint audits](../../../../ARTIFACTS.md#unpublished-files "Not published: checkpoints/") authenticate adapter/config/state/Adam/RNG/input/group/correction hashes once per commit. All 504 Adam parameter states have the expected cursor; the initial optimizer/RNG ancestry is fresh, and later ancestry matches the preceding committed policy. Gradients and per-update parameter deltas are finite and nonzero (gradient norms 0.148–0.680; per-update delta L2 0.080–0.200). These deltas are not summed and called a cumulative weight distance.

Actual correction captures contain root-only turns and pass all frozen distribution bounds: mean absolute log-ratio 0.0021–0.0097; raw token ESS fraction 0.9950–0.9993; removed capped importance mass at most 0.000427. This is the declared token-capped conditional correction with one same-forward full-batch update per fresh generation, not a claim of an unbiased full-trajectory policy gradient. No new source defect or native proof discrepancy was found in this outcome audit.

Last saved adapter: `809fc46ed50d36c5e61b2e8ae785ae84083b509fcb8bdd3b1914eaca3c0c842a`, [checkpoint seven](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-adaptive-rlvr-v1/outputs/attempt-001/round-07/training/checkpoint-7/"). No validation-best selection occurred.

## The completed paired comparison

| Readout | Strict correct | Correct final protocol | Wrong number with valid protocol | Protocol failure | Admission-null |
| --- | ---: | ---: | ---: | ---: | ---: |
| Validation 0 | 2/8 | 3/8 | 1 | 5 | 0 |
| Validation 4 | 2/8 | 5/8 | 3 | 3 | 0 |
| Transfer 0 | 0/16 planned; 0/15 admitted | 5/16 | 5 | 10 | 1 |
| Validation 8 | Not run | — | — | — | — |
| Transfer 8 | Not run | — | — | — | — |

The failure columns are mutually exclusive admission-aware reporting categories. A protocol-invalid reply can also contain a wrong number; it is not repaired into a numeric score. Leading/trailing whitespace is treated exactly as in the frozen whole-reply contract.

All eight validation pairs have identical initial physical prompt-token arrays and complete sampling dictionaries, with their actual root bindings recorded. Later child requests and trajectories are adaptive and need not match. The individual validation outcomes are:

| Context / query | Gold | Initial → update 4 strict score | Update-four final outcome |
| --- | ---: | ---: | --- |
| validation-00 / single user | 2 | 0 → 0 | Proposed code/prose, not the required answer |
| validation-00 / global | 3 | 0 → 0 | `Answer: 6` |
| validation-01 / single user | 0 | 0 → 1 | `Answer: 0` (initial reply was bare `0`) |
| validation-01 / global | 6 | 0 → 0 | `Answer: 7` |
| validation-02 / single user | 1 | 1 → 0 | Correct-number explanation plus `Answer: 1`; invalid whole reply |
| validation-02 / global | 14 | 0 → 0 | Announces further processing rather than answering |
| validation-03 / single user | 2 | 0 → 0 | `Answer: 0` |
| validation-03 / global | 11 | 1 → 1 | `Answer: 11` |

Exact coordinate IDs, seeds, raw paths, per-context results and prefix proofs are in [terminal metrics](../../../../ARTIFACTS.md#unpublished-files "Not published: TERMINAL_METRICS.json"). Initial query transfer is 0/8; initial length transfer is 0/8 planned, with one null. There is no post-update transfer comparison. Prior studies' replay variance is useful caution, not a matched control for these new seeds/runtime trajectories.

## Where the pipeline fails

Native-authenticated helper use is common: 159/160 recorded episodes include an eligible helper invocation. In validation, all child maps are duplicate-free and cover exactly their requested IDs: 15/15 maps initially, 26/26 after four updates. Label-occurrence correctness is 205/216 and 161/172 respectively; repeated records/calls are not independent items. Baseline transfer maps are 27/27 structurally valid, with 381/404 label occurrences correct. Thus free-map formatting failure is not the principal explanation for these readouts.

However, querying the helper is not equivalent to completing the task. Validation has full query-relevant native map coverage in only 5/8 trajectories at both policies. Initial transfer has 7/16. Some roots stop after the demonstrated first four records, repeat them, or describe a future computation instead of performing it.

There are also failures downstream of usable, complete child evidence. A [source-linked validation example](../../../../ARTIFACTS.md#unpublished-files "Not published: CASE_VALIDATION4_MAP_COUNT.json") contains eight four-record maps on the final root's actual physical prompt branch. Their three numeric-value labels exactly match gold, but the root answers six. The sampled actions print and overwrite successive maps without computing a cross-batch count. No generated code was executed by the auditor.

The conservative [posthoc observation screen](../../../../ARTIFACTS.md#unpublished-files "Not published: map-fidelity/") requires complete, unambiguous root-visible maps supported by native child values. Its three eligible validation-four cases all imply the correct aggregate: two roots give wrong numbers, and one fails final formatting. Four initial-transfer cases qualify: two have correct map-implied aggregates but roots answer seven/eight rather than six; two have already-wrong map aggregates and also invalid final formatting. Many trajectories print only counts or other text, so they remain parser-partial. **This screen establishes coexistence of child-semantic and root map-to-count/final-format failures, not their exhaustive prevalence or a causal mediation estimate.**

## Nulls and cost are not hidden

All three admission-null trajectories retain an empty reply but have `HarnessError`, trace `ok=false`, and an IPython broker-scope shell wait ending in `_queue.Empty` at `get_shell_msg(timeout=30)`. They occur in transfer zero, training generation one, and training generation eight. Their retained physical calls have no provider-call error. These are not evidence of a model deliberately producing an empty answer or an endpoint outage; raw empty-score zero and training-null remain separate. Full coordinates and exact raw hashes are in [terminal details](../../../../ARTIFACTS.md#unpublished-files "Not published: TERMINAL_DETAILS.json").

There are **1,688 retained physical attempts**, agreeing with all 11 completed stage STATUS files: 911 root and 777 child, all recorded HTTP 200. Of these, 1,678 belong to the admitted native graph proofs; the ten remaining calls in excluded trajectories still count toward cost, not gradients. No provider-reported usage/cache field is missing after decoding embedded JSON.

| Provider-reported cost | Root | Child |
| --- | ---: | ---: |
| Input tokens, including cache hits | 1,618,263 | 719,445 |
| Cached input tokens | 1,559,824 | 665,216 |
| Uncached input tokens | 58,439 | 54,229 |
| Output tokens | 107,778 | 46,339 |

Validation calls increase 43 → 65 (root 28 → 39; child 15 → 26), with unchanged accuracy. Root output tokens rise 3,579 → 4,629; child output falls 1,970 → 1,586. There is only one jointly correct validation pair, whose root/child input/output costs are essentially unchanged; it cannot establish successful-task efficiency. No successful paired transfer cost ratio exists. Per-coordinate, matched-admitted and jointly-correct costs are retained separately in metrics.

Scientific elapsed time is 3,165.25 seconds (52.75 minutes), from 12:08:32 UTC to approximately 13:01:17 UTC. Recorded optimization totals 422.52 seconds; the remainder includes service, rollout and verification work and is not assigned wholesale to GPU compute. Peak training allocator statistics are 11.99 GB allocated / 41.06 GB reserved, not a whole-run hardware peak. The parent operation exits 1 without timeout, records no GPU processes after exit, and preserves the scientific STOP. These usage totals are provider accounting, not an independent measurement of unique GPU computation or proof of zero inherited API retry capability.

## What this changes next

1. **Evaluate the last saved policy as a new question.** MAIN has separately approved 72 fresh episodes: the same 24 coordinates for initial SFT `efab2913…`, the future fixed success-SFT checkpoint eight, and interrupted RL checkpoint seven. This tests whether seven updates changed outcomes without substituting for the missing fixed-final-eight primary. The new SFT-versus-RL comparison is an unequal-compute package comparison; its outcomes are not part of this report. This combined study avoids duplicating a separate last-saved-policy readout.
2. **Test evidence-to-count fidelity, not just another helper-call lesson.** Training-only successful native trajectories or a separately declared accumulation/ledger intervention can target retaining labels, computing the aggregate, and emitting it faithfully. Candidate selection must exclude evaluation traces and must not promote operator-authored zero-root traces into sampled RL likelihoods. Hold the typed child interface fixed and compare strict accuracy, coverage and actual cost—not helper uptake alone.
3. **Treat homogeneous groups as a curriculum limitation, not an exception to erase.** A future prospectively frozen schedule can include more task groups and explicitly define zero-update generations; it must preserve actual update counts and avoid reward-conditioned rerolls. The present run's solved small task versus unsolved global task identifies an uncertainty, not permission to alter the old stopping rule.

This is one small, exposed task family, one training seed, four validation contexts, and no final transfer readout. It supports an operationally real root-only training result and a concrete aggregation failure mode. It does not yet support a generic adaptive-planning, decomposition, or end-to-end generalization claim.

## Audit artifacts and reproducibility

[TERMINAL_METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: TERMINAL_METRICS.json") SHA `1f24d6ce992ee2cb48841162abd39e23123b8ddd210b331255f74b6022e17d80` contains paired/subgroup metrics and checkpoint ancestry. [TERMINAL_DETAILS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: TERMINAL_DETAILS.json") SHA `ea3d42e851076609bf77afb8e35783ca277a41937232ff28f0459db0f1abc1de` contains terminal/lifecycle identities, null causes, correction summaries and complete-stage count agreement. [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") indexes exact local provenance; [FINAL_MANIFEST.json](../../../../ARTIFACTS.md#unpublished-files "Not published: FINAL_MANIFEST.json") seals this analysis.

Reproducers: [audit.py](../../../../ARTIFACTS.md#unpublished-files "Not published: audit.py"), [summarize.py](../../../../ARTIFACTS.md#unpublished-files "Not published: summarize.py"), [terminal_details.py](../../../../ARTIFACTS.md#unpublished-files "Not published: terminal_details.py"), [map_fidelity.py](../../../../ARTIFACTS.md#unpublished-files "Not published: map_fidelity.py"), and [case_probe.py](../../../../ARTIFACTS.md#unpublished-files "Not published: case_probe.py"). Four focused scoring/cache/visibility fixtures pass. The missing-implementation RED cases and the corrected analysis-only semantic-link/physical-branch assumption were observed during preparation; no scientific source or outcome was changed. Completed stage/model closures were authenticated once and cached, not rehashed per episode. The source review is separately retained at [adaptive-rlvr-source-review](../adaptive-rlvr-source-review-2026-09-09/REPORT.md).
