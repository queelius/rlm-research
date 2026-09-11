# Adaptive-question feasibility: data available, start with filtering versus global count

CPU-only feasibility audit, 2026-09-09. No live BROAD16 outcomes were opened for this task, no acquired/generated code was executed, and no experiment dataset or launch was created. This proposal remains behind identity384 in the queue. The brainstorming feasibility-spike approach kept the work to membership checks and one deterministic, non-model preview.

## Decision

**Eight new, mutually question-group-disjoint 128-record documents fit the named-history exclusion policy: 1,454 groups remain, leaving 430 spare.** They do not fit a stronger exclusion of the entire OOLONG source pool: only 278 remaining groups are outside that pool. Thus “disjoint from the inspected/frozen root studies” is defensible within the enumerated scope; “unexposed to any prior root study” without that qualification is not established. All candidates are from the existing 5,065-group leaf-training partition, not leaf-semantic holdout or a pretraining-clean benchmark.

The strongest first question is whether one root can exploit a public user filter while avoiding that filter for a global count. Cross-user joins change aggregation logic but do not inherently defeat classify-all inspection. Earliest-common-class queries offer cheap early stopping, but the inspected preview has no long-search cases. Do not promote all four families as equally demonstrated adaptive-planning challenges.

## Actual available data and exclusions

Remaining unique normalized groups: HUM 340, ENTY 342, DESC 300, NUM 238, LOC 217, ABBR 17. The 3,611 excluded leaf-training groups are the union of the named legacy contexts, root-only training/validation contexts, old campaign transfer contexts and the **entire frozen candidate curriculum**, including its unlaunched optional strata. Leaf validation/test records were never candidates for this remaining pool. The all-partition exclusion union has 4,348 groups; do not confuse that number with training-pool consumption.

Checked old OOLONG windows 6/8, root-only inputs, both original/independent campaign transfer inputs and the earlier leaf-composition set. Fresh native training/heldout and recursive capture reuse windows 8/6. The newer return-contract and receipt task catalogues each resolve to the same six excluded transfer-context hashes, with zero additional contexts. Replays/continuations reuse those source sets. Older synthetic RLVR inputs retain the prior pinned inventory's zero-TREC-overlap finding; this bounded audit did not rescan every archived output or paraphrase. The remaining-group-set SHA256 is `db4418a688e759bf159b2a24922caa32c7115c358b007d74c10ba7e87003dff2`.

Source representatives were checked directly against the pinned official training bytes and declared coarse labels using the existing normalization: the documented byte repair, Unicode NFKC, case folding and word-token normalization. No dataset loader or clone code was executed. Full counts, input hashes and reproducible preview allocation are in the [machine inventory](../../../ARTIFACTS.md#unpublished-files "Not published: 2026-09-09-adaptive-question-feasibility.json").

## One label-independent preview, not the experiment allocation

Hash-ordered 1,024 remaining groups into eight documents without class quotas or resampling. Independently shuffled 16 synthetic users, exactly eight records each, and 128 unique date ranks per document. Queried user equals document index. Metadata assignment never inspected labels; labels were used afterward only to compute diagnostic answers. No model outcomes influenced this preview. Real dates, final seeds and model payloads have not been frozen.

| Task | Preview answers across eight documents | What differs in a useful plan |
| --- | --- | --- |
| NUM count for one user | 3, 1, 0, 1, 1, 0, 1, 2 | Filter public metadata first: 8 semantic records versus 128. |
| Global NUM count | 23, 23, 19, 22, 20, 20, 13, 19 | The user filter is invalid; obtain task-sufficient evidence across all 128 records. |
| Users with both HUM and NUM | 11, 12, 11, 12, 11, 10, 8, 9 | Join by user and count each user once, not records or independent class totals. |
| Earliest NUM, sorted rank | 3, 12, 11, 3, 4, 2, 3, 12 | Sort public dates and stop only after a target and complete preceding-prefix evidence. |

User-query “always 1” scores 4/8 here; across all 128 user subsets the NUM-count histogram is 0:36, 1:44, 2:29, 3:19. This is real answer skew, not evidence that a model can solve the tasks by that shortcut. Global mode scores 2/8 and join mode 3/8; join is neither always zero nor all 16. NUM occurs within the first sorted16 in **8/8**, so one such batch suffices with a correct classifier. ABBR is absent in three documents and its first ranks in the others are 14, 27, 27, 106 and 2; rare-class searches offer variation but add rare-label competence and “NONE” skew as confounds.

Do not force identical per-document label quotas: that would make global counts constant. Fix metadata/target schedules before generation outcomes, report constant-answer baselines and full answer prevalence, and preserve zero/absent cases. If a later design stratifies questions by host-computed counts or search depth, disclose that selection explicitly; it is no longer an unconditional label-independent sample. Seventeen ABBR groups cannot support a broadly balanced rare-class training/evaluation program without reuse.

## Exact verifier and headroom contracts

- **User count:** `sum(label_i == target and user_i == requested_user)`. Count records, including distinct questions by the same user; never infer labels from metadata. Strict final grammar `Answer: N`, ASCII nonnegative integer, then exact equality.
- **Global count:** `sum(label_i == target)` over the whole document, same grammar. A full six-class map is unnecessary: correct target/non-target decisions suffice. Final correctness alone does not certify complete evidence or prevent cancellation.
- **Cross-record join:** number of distinct users for whom both `exists HUM` and `exists NUM` hold. Because classes are mutually exclusive, the witnesses must be different records. Use the same strict integer grammar. A positive user needs two witnesses; ruling out a negative user may need its remaining records. Classify-all remains valid; this tests a new reduction/interface burden as much as adaptive inspection.
- **Earliest match:** minimum ISO date among target records, or `Answer: NONE` iff none exist. Prefer unique dates to avoid tie ambiguity; with ties, score the date only, not an arbitrary record. Strict `Answer: YYYY-MM-DD`/`Answer: NONE`, valid dates, exact match. Every earlier record must be ruled out for a sound prefix strategy. Randomize actual calendar values independently so the earliest answer is not a common fixed date.

All labels/gold, oracle subset sizes, prefix ranks and join certificates remain host-only. Runtime receives record IDs, synthetic users/dates, question text and the query. Do not require a complete label map as a universal reward condition. Optional source-bound observation diagnostics can measure what was requested/returned; unobservable coverage stays null. An oracle semantic-inspection count is not an attainable model guarantee, and fewer child calls do not prove less semantic work if the root classifies records itself.

## Smallest informative pilot

Recommend **four disjoint 128-record development contexts, two families (user-NUM/global-NUM), two fresh sampling seeds and three methods: 48 episodes**. Keep the other four candidate contexts ungenerated/unconsumed for follow-up. Use one already fixed root checkpoint and fixed c32de child; do not add the original/trained-weight factorial yet or select a root using this pilot's outcomes.

Methods: (1) fixed classify-all in 16-record batches, (2) deterministic question-aware filter-then-classify for the user query and classify-all for the global query, (3) free root in the qualified file-backed native/rootless environment. The second baseline demonstrates an achievable planning opportunity with the actual child, rather than presenting host-label oracle savings as a model result. Keep child definitions, representation, sampler and native protocol common wherever requests coincide; free-root worker wording may still differ, so this is a whole-policy comparison, not isolated routing causality.

Fresh calls for each episode: no shared label cache across questions or arms. Fixed-all costs 128 child calls across its 16 episodes; query-aware costs 72 (64 global, eight filtered), before free-root calls and any failures. Freeze strict child-cardinality handling with no repair/retry; protocol failures remain separate. Primary outcomes are per-family paired exact success and full physical-call/token costs, clustered by the four source documents. Report root/child actions separately, cached versus logical input, model/infrastructure failures and count-cancellation diagnostics when an aligned map is genuinely observed. Four clusters only support an exploratory screen.

One warm A100: plan roughly 20–40 minutes, proposed 45-minute inclusive cap subject to the final qualified lifecycle/episode budgets; this is an estimate, not measured timing. Save every episode and keep partials on the cap. Promote join/earliest or adaptive reward training only if this small screen establishes executable competence and an accuracy/cost opportunity beyond fixed rules. No new reward, forced recursion, answer repair or launch is authorized here.

## Provenance

Frozen leaf partition ID `36e7d2e1ad83210f6420a0312ec46e8a8c70d764e9df0e6d631c67f6fd16c764`; split file SHA `3f5f648488d512d2052b9f3d57c02e030af8e939ca363998c07a556a47d7f457`. Official unversioned CogComp train bytes SHA `9e4c8bdcaffb96ed61041bd64b564183d52793a8e91d84fc3a8646885f466ec3`; pinned HF loader revision `eb1e45c1ba990fecca7cf84b67ce845edbcf49bf`. Data license is unknown/unspecified; Apache-2.0 applies to loader code, not inferred dataset rights. OOLONG pool/repository revision `0bb7eabe839218fee7fe8d007f41cfc2fd3ae24c`, dataset revision `f0d59eaf0febf130664cfceb710436c8e3216b2b`; source-pool reuse is explicit. No new download was needed.

This follows the [adaptive-family proposal](2026-09-09-adaptive-question-families.md) and the [context-lens/headroom memo](2026-09-09-output-correspondence-and-context-lenses.md), not a novelty claim about filtering, joins, early stopping or decomposition. Unknown whole-history and base-pretraining exposure remain unknown.
