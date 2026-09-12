# Fresh selective-singleton comparison — design only

Status: proposed for MAIN approval. Data acquisition/selection is complete; no native runner, model preparation, GPU launch, or runnable READY has been created. Existing closures and analyses remain unchanged.

## Question and prior-art boundary

Does a fixed disagreement-triggered smaller-request rule offer a useful accuracy/token tradeoff beyond ordinary contextual majority voting on new local held-out records? This is not a claim that batch ordering, ensembling, adaptive request size, or recursion is a new algorithm.

[BatchPrompt §§2–3](https://arxiv.org/html/2309.00384v2#S2) uses repeated within-batch permutations and majority voting; its confidence-based early stopping removes resolved examples. Our column-preserving companion regroupings are a known-style contextual ensemble, not an exact BPE/SEAS reproduction. Neither confidence labels nor learned selection is used here.

The additive [THREE_VOTE.md](../../analyses/helper-companion-position-local-review-2026-09-12/THREE_VOTE.md) reports all previously specified replay rules. Original+A→singleton versus original+A+B vote gives TREC 121 versus 119/128 (2 paired wins, 0 losses; 0.870 replayed token ratio), but AG News 112 versus 113/128 (0 wins, 1 loss; 0.821 ratio). The old data are evaluation-exposed, and singleton outputs came from a separate service history. These are hypothesis-generating observations, not a confirmed selection rule. Original+A was the requested fixed primary rule before this stronger-baseline comparison; neither the rule nor data selection is chosen by the new panel's outcomes.

## Frozen data and exposure

Use only [helper-adaptive-fresh-panel-v1/MANIFEST.json](../../../../ARTIFACTS.md), identity `9df078b519bd7523a724bd627ceaea8caa60a6ff7a5b677683e7b0e39ac080c3`, with separate PUBLIC.json and HOST_GOLD.json. Selection namespace: `helper-adaptive-fresh-panel-v1|202609121200`.

- TREC: 64 test questions; human/location/entity/description 13 each, numeric 12, abbreviation 0. All seven test abbreviation groups occurred in the old panel and are excluded. Keep the same six-label schema. This is explicitly a five-observed-class study, not replication of the old six-class distribution.
- AG News: 64 test items, 16 per class.
- Exclude the old 256 panel, actual 5,065 c32 SFT questions consumed twice, all current 32 helper-optimization inputs, and 320 known root-SFT group IDs. Both normalized text checks plus source/group-ID checks have zero selected overlap. Remaining candidate counts before selection: TREC 361, AG News 7,472.
- Strata use host gold only to set prospective quotas. Selection is SHA256-ranked within each class; final ordering is a separate label-free SHA256 rank, then four consecutive groups of 16 per dataset. Gold is never used in grouping, routing, prompts, or outcome selection.

The manifest pins raw files, acquisition receipts, source revisions, split inventory, selection source, actual c32 training manifest and consumed-step state, exclusion inventories, and all selected artifacts. TREC's unversioned source is pinned by content hash with unknown data license; AG News revision is `eb185aade064a813bc0b7f42de02595523103ca4`, with unknown/research-noncommercial licensing caution. Reused external caches only; no dataset redistribution. The exposure claim covers verified local helper optimization, not every possible root run or unknown base-model pretraining.

## Four fixed policies, one matched component experiment

| Policy | Decisions | Calls across both datasets |
|---|---|---:|
| Original16 | One original full map per group | 8 |
| Three-vote | Original, neighbor_A, neighbor_B; majority; three different labels returns original | 24 |
| Selective singleton — primary | Original and neighbor_A agree: accept; disagree: use one fresh singleton | 16 + D |
| Always singleton | One singleton per record | 128 |

`D` is the number of valid original/A category disagreements across 128 unique records, determined without gold. No neighbor_B variant, threshold tuning, best-rule selection, or training. All four policies and both datasets are reported regardless of direction.

The physical experiment executes 24 full-map calls plus 128 singleton calls = **152 calls**, with **512 requested record-output slots** and **128 unique records**. Full-map predictions are shared across policies; actual live selected-singleton calls are also members of the always-singleton reference. This is a matched component experiment, not four independent cold-service policy executions. Shared observations do not create extra independent trials.

### Gold-free companion maps and seeds

Represent each dataset's frozen order as four rows × 16 columns. For each neighbor arm A/B and each column, independently shuffle the four row indices with `random.Random(int(SHA256(namespace), 16))`; namespace is `helper-adaptive-fresh-live-v1|202609121212|dataset|neighbor_A_or_B|column`. Put each shuffled record in the same numbered column. Every record appears exactly once per arm, with slot preserved; absolute token offset is not preserved. Identity/fixed-point permutations are allowed and recorded, not rejected after inspection. This is companion regrouping, not an attention-causality intervention.

Native sampling seeds are fixed per dataset for every component request: TREC `202609121210`, AG News `202609121211`. Preserve exact c32 weights, native batch-invariant v4 service, full-category definitions, model alias, keyed ordered schema, temperature 0, and max output 1,024. Only the supplied record partition changes. No old output is reused.

### Explicit live ordering

1. Collect original and A full maps. Iterate original block indices 0–3; within each block iterate TREC then AG News, and alternate O/A call order by `(block + dataset_index) % 2`.
2. Commit `ESCALATION.json` from only valid O/A categories and IDs, with hashes of both source call inventories. It contains the fixed disagreeing ID list in PUBLIC order. Commit before any B call or singleton reference not selected for escalation. The runner does not load HOST_GOLD until all model calls are terminal.
3. Execute selected singleton calls in committed PUBLIC order. These are actual model calls taken through the live disagreement branch, not offline substitution.
4. Collect B full maps, block 0–3 and TREC then AG News.
5. Execute all remaining singleton references in PUBLIC order, without changing earlier adaptive predictions. Every record has exactly one physical singleton request over stages 3+5.

Each request body, actual raw response, ID/finish/schema/token inventory, usage, elapsed time, and validation outcome is checkpointed immediately. No retries, hidden rescue, new labels, or answer fallbacks. A malformed/missing O/A map makes its records unavailable to the selective policy; it is not converted into an artificial disagreement. Other scheduled components still run, within the cap. Three-vote requires all three valid maps for a record; invalid calls do not become votes. Unavailable predictions are explicit failures, not excluded from fixed-denominator correct/64 readouts. Paired wins/losses additionally identify the valid-pair subset and missing branches; incomplete panels cannot pass the decision screen.

## Costs, metrics, and prospective decision

Report each dataset separately: correct/64, per-class confusion, paired wins/losses and label disagreements for every policy versus original and versus three-vote, plus primary versus always-singleton. Preserve selected IDs, escalation fraction, and wrong agreeing O/A consensus that the selector cannot detect. There are only four original request clusters per dataset, and neighbor maps couple those clusters; do not treat every record as an independent experimental replicate or claim confirmatory power.

For each logical policy, sum the actual prompt+completion tokens of exactly its component calls once; also list input/output/cache tokens, calls, output-token upper bounds and missing-usage counts. The three-vote control pays for three full passes, the selective policy for two passes plus D singleton calls, and always-singleton for 128 calls. Separately report the **152-call physical experiment total**, one startup, and owner time. Never add logical-policy totals and label the sum the physical experiment cost. Missing usage means an observed subtotal with unknown remainder, not zero cost. Shared cache history and execution order forbid transferring latency/cache savings to independent deployed runs. No cross-run pooling with older flag-off or earlier-service scores.

Primary descriptive screen, fixed before scoring: within a dataset, selective singleton must have at least as many correct records as three-vote, strictly fewer observed input+output tokens, and complete valid coverage/usage/runtime qualification. Passing is only a reason to replicate, not a confirmed gain; report the full tradeoff if it fails. A higher-accuracy/higher-cost result revises the tradeoff question but does not pass this screen. A dataset-specific pass is not a cross-dataset claim. Retain original16 and always-singleton comparisons even if they dominate the primary rule; do not tune the rule to repair a negative result.

## Compute boundary and implementation seams after approval

Proposed owner cap **1,100 seconds**, outer shared-flock timeout **1,200 seconds**, with 90 seconds reserved for cleanup inside the owner cap. No new requests after the collection deadline; per-request remaining-time bounds and unconditional clean release. The bounded forecast is approximately 24 long-map decodes plus 128 singleton decodes and one service startup; this is an estimate, not a runtime guarantee. If capped, preserve fixed denominators and missingness; no automatic continuation, sample-size change, or post-hoc cap increase.

After approval, a thin independent sidecar can reuse the sealed arbitrary-record prompt/schema builder from helper-unseen-size-comparison-v1, the native send/strict actual-token validation seams used by companion64, and the same v4 service closure. It must not patch those sources. Before READY: pin c32/base/tokenizer/service closures; measure every possible request's prompt tokens and require `prompt + 1024 <= actual max_model_len 8192`; verify pre-exec batch-invariant receipt and final real EngineCore marker. Any context-bound violation blocks readiness without truncating text or changing templates. Two bounded CPU fixtures suffice: disagreement/routing/three-way tie with shared physical-vs-logical cost accounting, and permutation/partition/ordered-schema inventories with missing-map handling. No broad framework, model installation, or GPU model preparation.

Expected artifacts after separately approved implementation: immutable source/READY and request inventory; per-call raw artifacts; committed escalation receipt; final policy metrics and physical/logical token accounting; runtime binding/qualification and cleanup receipts. MAIN remains sole launcher. No implementation or launch approval is inferred from this design.
