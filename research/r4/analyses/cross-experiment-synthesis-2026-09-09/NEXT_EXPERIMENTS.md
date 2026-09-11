# Five comparisons that would change the research decision

These are candidate designs, not launched jobs or modifications to the live queue. Counts and caps below are prospective engineering choices. Runtime ranges are estimates from the recent 4B leaf and root runs, not measured future costs. Use the existing one-A100 base and authenticated LoRA identities; no larger model is proposed. Freeze a new spec, source hashes, prompts, seeds, budget and selection rule before every comparison.

## 1. Validate a correspondence mechanism on fresh permutations and vocabulary

**N1 / Q1. Priority: first; the completed representation/rotation controls support this branch.**

Hypothesis: an input/output anchor prevents loss of record correspondence, rather than merely forcing a valid array or allowing more output tokens.

Smallest comparison: prospectively choose the indexed representation from the completed development screen, with its selection explicitly recorded. It improved405/512versus181/512labels without requiring full question echoes. Compare plain array versus indexed output with identical question order, labels, decoder validity constraints where applicable, and a common token cap sufficient for both. Include batch5 as the competence control and batch64 as the stress condition. Do not rerun the old24/32control cells unchanged.

Data: two fresh hash-frozen permutations of each of the six existing TREC64contexts, explicitly reused public questions; separately,256 SST-2 validation groups outside the earlier256-group slice, selected by normalized-group hash without labels. Four fresh64contexts for that vocabulary transfer. The SST comparison is task transfer, not a pure label rename. Freeze seeds `910901` and `910907`; no checkpoint selection from these outcomes.

Model: old SFT only, matching the positive representation screen. Freeze that identity in the new spec. Adding all weights would multiply cost without resolving the immediate representation-transfer question.

Metrics/unit: strict full64correctness; exact schema/cardinality coverage; item accuracy by output quartile; errors attached to question ID across permutations; logical and generated tokens. Report ten context groups and individual normalized sentences, not hundreds of calls as independent cases. Primary inference is a paired context difference; repeated permutations diagnose position, not create independent data.

One-A100 shape: one loaded4B adapter; four workers; at most600leafcalls and1,536output tokens/call, with prompt+cap≤8,192. Expected5–15min warm; hard30min cap including acquisition after service ready. Persist each response, actual prompt IDs, alias and error. No retries, no answer repair. Checkpoint policy: per-call immutable outputs; no weight update.

Decision: promote to representation-targeted SFT only if valid64coverage≥95%, canonical accuracy improves by≥10percentage points on TREC with no>2point batch5 loss, and direction is not confined to one permutation. A positive SST direction strengthens transfer; failure there narrows the claim. If cardinality improves without item accuracy, revise toward alignment/semantic explanations. Retire the proposed anchor if neither correspondence nor completeness improves at the common cap. These thresholds are prospective screening decisions, not statistical significance criteria.

## 2. Hold the root prefix fixed and replace only the returned evidence

**N2 / Q2. Priority: high; targets the missing child-to-root causal link.**

Hypothesis: a significant part of the fixed-aggregation/free-root gap is caused by root consumption or final commitment, after sufficient evidence has already been acquired.

Smallest comparison: from a newly captured root trajectory, freeze the physical root context immediately before consuming a classification result. Replay the identical continuation state with (a) the actual child return, (b) canonicalized serialization of exactly the same labels, and (c) an explicitly identified oracle-label return in the same contract. These are diagnostic counterfactual observations, not live sampled child actions and never eligible for RL log-probability credit. Preserve all private gold solely in the evaluation construction; it must not leak into unrelated live rollouts.

Use12prefixes selected by a predeclared rule from six contexts, not only failed examples: the first eligible classification-return point per task/seed, with ineligible coordinates retained. For each state use seeds `910911`, `910919`, `910927`, `910933`; three arms produce at most144continuations. The contexts may reuse exposed TREC source questions for mechanism work; reserve a later fresh composition readout for any promoted fix.

Metrics/unit: root parser/tool validity, complete consumption of returned IDs, report-implied answer, true answer, computed-answer versus submitted-answer equality, continuation calls/tokens. The paired unit is the saved prefix; original task/context clustering remains explicit. The MRCR computed-commit feasibility attempt did not obtain submissions, so it supplies no final-restatement effect estimate. Qualify the actual observation and submission path before reusing that seam here; do not duplicate a failed manipulation unchanged.

One-A100 shape: one original4B root plus fixed old-SFT child if additional calls are permitted; at most144continuations, four workers, maximum three root turns and16total successful model calls per continuation, output cap2,048/turn. Expected15–35min; hard45min, with a10,000generated-token ceiling per continuation. Budget-censored outcomes remain separate. Persist each fork's exact native state, aliases, observations and final marker; no training or checkpoint selection.

Decision: canonical serialization repairing at least four more prefixes than it harms, without changed labels, promotes an interface-specific intervention. Oracle evidence failing in most otherwise valid continuations points toward consumption/commitment rather than leaf training. Actual versus oracle differences with faithful consumption point back to child semantics. No difference with wide ceiling/floor censoring means redesign the state sample, not claim no bottleneck.

## 3. Test whether a process check distinguishes real success from cancellation

**N3 / Q3. Priority: high CPU-first; prerequisite to a new reward objective.**

Hypothesis: final counts alone admit materially different processes, and a small authoritative consistency check can separate them without requiring a specific recursion shape.

Smallest comparison: use the frozen completed TREC composition and root-campaign trajectories, reconstruct only auditable aligned labels, and compare current strict final reward with a diagnostic score containing coverage, report-implied aggregation and target false-positive/false-negative counts. Keep three states—pass, fail, unobservable—for every component. A trace lacking aligned evidence is not automatically a wrong label map.

To test discrimination rather than correlate with the same final answer, freeze two additional aggregate queries per fully observed label map, one on a hash-selected facet and one on a second class. Compare answers implied by predicted labels to authoritative gold. No model calls are needed for this first phase. Use source-group splits: develop the candidate check on existing development-context traces, then evaluate once on the six new-composition contexts, already exposed scientifically but not used to tune the new check. Freeze the check before reading that readout.

Metrics/unit: fraction of exact-final successes with incorrect target evidence, coverage uncertainty, sensitivity to known cancellation, and false rejection of fully correct evidence/aggregation. Unit is an episode nested in its source context; do not count alternate queries as fresh examples. This measures reward identifiability, not how a model would adapt to optimizing the score.

Compute/checkpoints: CPU only initially, a30min analysis cap and immutable projected-label/score artifacts with source hashes. If the screen finds useful discrimination, a separate one-A100 follow-up may collect at most64fresh root trajectories under the unchanged reward to test whether the check remains observable; estimated15–30min,45mincap,per-episode checkpoints. No reward change or training is authorized by this design itself.

Decision: promote a separately frozen objective comparison if the check detects≥80% of auditable known cancellation cases, rejects≤5% of fully correct complete solutions, and is observable on≥80% of fresh completed trajectories. Revise if low observability drives apparent gains. Retire the check if it mostly measures output format or imposes a favored recursion pattern rather than evidence correctness.

## 4. Compare a short fresh-root campaign with a contemporaneous unchanged policy

**N4 / Q4. Priority: after the specific admission policy is frozen; not a blind continuation.**

Hypothesis: root-only training improves executable tool use and evidence consumption beyond stochastic replay variability, with the child fixed.

Smallest comparison: two independent campaign seeds, four fresh32-trajectory generations per seed, persistent Adam within each campaign, starting from the same original root and fixed old-SFT child. Use the audited one-full-batch-step TIS objective unchanged initially. At step0,2,4 run a fixed16-trajectory validation set for both current root and unchanged original root with matched context/seed coordinates and counterbalanced service order. A validated narrow exclusion of fully authenticated unsampled provider rejection must be declared as a new policy; preserve the old stop and report excluded policy-overlength separately.

Data/seeds: retain the four root-training contexts to isolate optimization; fresh rollout seeds from independent masters `910941` and `910951`. Validation uses four newly frozen context compositions from held-out source groups, four tasks/seed coordinates per context. These may share public source questions with earlier component evaluation; state that limitation. Select each campaign's checkpoint using only mean validation strict score, ties to earlier step. After selection, one24-coordinate readout on six fresh compositions with fixed seeds `910967`,`910979`; no access until both selections are saved. Checkpoint4 and selected-checkpoint results must stay distinct.

Metrics/unit: strict final answers, tool-call parse validity, record coverage, faithful use of child results, successful/rejected root/child calls, token and latency tails, null exclusions. Training scores are fresh-seed unpaired diagnostics. Learning evidence is a difference from contemporaneous unchanged controls across two campaign seeds, clustered by context—not a best checkpoint's gain over one old replay.

One-A100 shape: owned dual-LoRA inference alternates with one4B root trainer; eight collection workers, unchanged one-step batches, model loading/release included. At most256training episodes,192validation episodes plus48selected transfer episodes. This is materially more expensive than a leaf control: estimated90–150min, hard3hours; bound each episode to the already qualified action/token envelope rather than silently reducing it midrun. If the cap prevents both seeds, label the comparison incomplete. Save adapter, Adam, RNG, cursor, source/group identities and distribution capture after every actual step; no update on stale rollouts.

Decision: promote only if both seeds improve over contemporaneous unchanged controls at selected validation, the fresh transfer direction agrees, and gains are not explained by more invalid/missing episodes or a>25%increase in median logical tokens. A useful process gain with flat strict answers revises the reward/coverage hypothesis. Retire the current objective on this task after two properly completed seeds show no consistent process or strict gain; do not respond by merely adding steps or a larger root.

## 5. Separate useful input selection from task reframing on unfamiliar layouts

**N5 / Q5. Priority: medium; positive-control bridge to adaptive orchestration.**

Hypothesis: reducing irrelevant input while keeping the child classification contract fixed improves the efficiency frontier; changing the label task is a distinct, potentially harmful operation.

Smallest comparison: fixed full mapping, deterministic visible-metadata filtering with unchanged six-way labels, and filtering plus binary target/other labels. First use fixed Python scope selection to qualify the information/contract effect. Only if that succeeds add a frozen root controller that must discover the visible scope from the input. Do not conflate a hand-coded filter with learned exploration.

Data:24fresh synthetic context groups generated from a pinned generator and master seed `910991`,64records each, with held-out renderer/layout families rather than merely new text under known templates. Eight groups are a development screen;16are unopened readout. Include both metadata-visible queries and semantic queries, with required relevant records known to the private verifier. Retain existing natural TREC controls as a boundary rather than training on these readout answers.

Model: the existing8B checkpoint only if its authenticated environment fits the currently available single A100; otherwise predeclare the available4B model and rerun all three arms, not mix models between scope conditions. No larger model or new download is necessary. Two seeds `911003`,`911009`; keep label semantics, output constraints and per-call cap matched where the intervention allows.

Metrics/unit: whole-context answer correctness, relevance recall, unnecessary child-input tokens, complete record/ID coverage, and end-to-end logical/output tokens including controller inspection. Unit is the generated context group. Record direct or fixed full mapping as the budget reference; input savings alone are not a FLOP or wall-time claim.

One-A100 shape: initial component screen≤288calls, four workers,1,024outputtokens; expected5–15min,30mincap. A promoted controller readout≤96episodes,60mincap,per-call/episode checkpoints. Freeze any controller checkpoint before readout; no training unless the qualification demonstrates both room for improvement and sufficiently reliable child behavior.

Decision: promote learned scope training if unchanged-contract filtering reduces total logical input≥40% with no more than one lost exact readout context, and relevance recall is complete. If binary reframing underperforms while filtering works, retain the stable semantic task. If controller inspection erases savings or loses relevant input, revise exploration rather than call the component token reduction an end-to-end gain.

## Portfolio discipline

Run one informative short control before a long training job whenever it resolves the training target. Keep the next two ready choices available, but never fill an idle GPU with a comparison whose outcome cannot change a decision. Acquisition, serving transitions, failed attempts and idle gaps belong in cost accounting. The proposed thresholds above are exploratory go/no-go rules; a confirmatory claim would require a new frozen protocol and appropriate uncertainty estimates.
