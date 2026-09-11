# What should we train next to make the root question-sensitive?

September 9, 2026. **Decision memo only: no experiment, source reservation, recipe,
READY, implementation or launch.** Pending uptake96/adaptive40 model outputs were
not read. This memo uses their frozen contracts, existing trainers, completed
historical evidence and immutable source partitions. The accompanying
[machine feasibility](../../../ARTIFACTS.md#unpublished-files "Not published: 2026-09-09-adaptive-root-training-feasibility.json") records
exact source hashes, remaining pools and a reproducible unreserved allocation.

## Recommendation: establish the bottleneck, then train one thing

If the free root can use the child interface but misses the operator filter's
accuracy/work opportunity, start with **eight fresh-generation terminal-reward
root-only updates** on query-varied documents, not another homogeneous global
count campaign. Use the same historical step8 root as adaptive40 and fixed c32de
child so the before/after question is incremental question-sensitive learning.
Reset Adam explicitly for this new objective/data campaign; retain the historical
checkpoint's origin, never rename it an untrained original.

Do **not** assume terminal reward will teach efficiency. If both all16 and filter16
are equally accurate and the free root is already correct, binary terminal reward
has no reason to prefer the cheaper plan. That is a separate cost-objective question.
If basic import/call/strict-map failures dominate instead, test a tiny interface
SFT warm start before RLVR. Do not train on non-admitted or fabricated traces just
to obtain a nonzero gradient.

| Pending evidence, read only when complete | Smallest useful next option | What it identifies |
| --- | --- | --- |
| Fixed plans work; free mistakes are primarily API/decoder handling | Interface-only SFT versus the same initial root | Whether valid use of the existing interface is learnable |
| Free can execute; exact terminal outcomes vary within identical prompts; fixed filter exposes headroom | Terminal-only RLVR, initial versus fixed final8 | Whether correctness feedback improves question-conditioned orchestration |
| Both plans/free are accurate but user filtering has a substantial work advantage | Separately declared cost-aware RLVR versus terminal-only RLVR | Whether an explicit efficiency objective is necessary/useful |
| Fixed plans fail structurally or child labels dominate errors | No root training yet | Interface/child prerequisite is unresolved |

Uptake96 is evidence about the public interface/prompt package, not new training
data and not an independent adaptive-planning test. If its taught interface helps,
freeze one common prompt/interface for all future training and evaluation arms.
Do not simultaneously change the prompt and then attribute the whole gain to SFT
or RLVR. If adaptive40's free root already filters appropriately, test transfer
first; extra training is not automatically informative.

## Exact data feasibility after adaptive512

The immutable TREC split has 5,065 leaf-training groups, 300 validation groups and 489
test groups. Reconstructed named exclusions include legacy OOLONG windows6/8,
root-only PUBLIC, both root-campaign transfer files, leaf-composition DATA, **all**
TREC root-curriculum groups including unused strata, and adaptive40's512 groups.
Later return-contract/receipt/uptake/child-role catalogues reuse that union.

| Original leaf partition | Total | Previously named-root excluded | Adaptive512 | Remaining |
| --- | ---: | ---: | ---: | ---: |
| Training |5,065|3,611|512|**942**|
| Validation |300|256|0|**44**|
| Test |489|480|0|**9**|

The named exclusion union is 4,348 groups before adaptive and 4,860 afterward.
Training remainder set SHA256 is
`7bee8765f31cf40683c9213cda3f0334ea048d10c922b4a630cbbb572767a487`
(newline-joined sorted group IDs). Full path/hash provenance and the other two
set hashes are in the machine file. These are normalized official group identities,
not a semantic/paraphrase or pretraining exclusion. TREC data license remains
unspecified/unknown; a loader license does not confer dataset rights.

Only 53 groups remain both child-training-heldout and unexposed to this named root
union: 44 validation + 9 test. That cannot fill one unique 64-record context. Those
groups have nevertheless participated in prior leaf validation/test evaluations;
do not call them untouched. An optional two16-record heldout-child-training probe
could fit in the44 validation groups, but would be small and separately declared.
It is not included in the main candidate below. Do not quietly shrink exclusions
or add duplicates to manufacture a64-record heldout stratum.

### One allocation that fits, without answer-conditioned sampling

| New role | Contexts | Source groups | Intended distinction |
| --- | --- | ---: | --- |
| Train |4×32 +4×64|384|Eight documents, two scope queries each |
| Validation |2×32 +2×64|192|Root-disjoint documents; seen query forms |
| Query-form transfer |2×32|64|Fresh documents; single-user versus two-user union |
| Length transfer |2×128|256|Fresh documents; seen single-user/global forms |
| Total |16 contexts|**896**|Leaves46 groups unallocated |

All 896 draw from the 942 leaf-training-supported remainder; none overlaps another
candidate stratum or adaptive512. This is **root composition/query transfer with
a leaf-trained helper**, not unseen-question or cross-domain generalization.
Training max64 makes128 genuine extrapolation beyond this adaptive curriculum's
training length. It is not an assertion that the pretrained model has never seen128
records. Two heldout clusters per transfer family remain only an exploratory screen.

The machine file specifies a single prospective namespace, hash-sorts groups using
`[namespace,"source",group_id]`, then allocates the above fixed sizes. Public IDs
follow displayed order. Label-independent hashed user assignment gives8 rows/user
(4/8/16 users for32/64/128). Query user and adjacent second user are determined by
within-stratum context index. Targets cycle NUM/HUM/ENTY/LOC by that same index;
no target, user or context is selected using the computed answer. Both training
queries ask for the same target category on a single user versus the whole file.
The union query form is absent from training. Plain queries and definitions are
public; category gold remains host-only.

After this single deterministic allocation, training answers are:

| Context | Size / category | Single-user | Global |
| --- | --- | ---: | ---: |
|0|32 / NUM|0|6|
|1|32 / HUM|3|9|
|2|32 / ENTY|3|9|
|3|32 / LOC|2|4|
|4|64 / NUM|2|14|
|5|64 / HUM|6|18|
|6|64 / ENTY|2|10|
|7|64 / LOC|1|11|

There are 11 distinct answers across 16 training queries. Best global constant gets
3/16; best within single-user family gets 3/8, versus adaptive40's known constant-2
baseline 6/8. This is **not label-balanced sampling**: zeros and skew stay. It is
also not proof of mixed model rewards, nor protection against all metadata-only
shortcuts. Retain per-target, per-size, per-scope constant baselines and inspect
actual policy work. Validation/transfer gold in the machine file is descriptive
after allocation and must not be used to revise memberships or choose weights.

These candidates are not reserved. Before an eventual data freeze, reconstruct
the named exclusion union again, report any intervening allocation and re-run the
same label-independent rule only under a new explicit data identity. Do not silently
reuse the present candidate hash after its availability changes.

## Option 1: tiny interface-only SFT, only for an interface bottleneck

Proposed screen: 32 operator-authored root-action examples, two record exposures
(two epochs), effective batch16, four optimizer updates, fixed final4. The16
training queries each provide two causal action examples: ordinary public-file
loading, then ordinary `rlm(request_for(records[:4]))` plus `strict_map` use. Targets
teach API serialization/import/decoder behavior, **not** a query-aware filtering
algorithm or oracle labels. Render each root prefix/action with the actual native
Qwen3/tools/thinking contract. Any preceding tool observation must be a real
operator-defined execution result from the owned CPU runtime and be masked. No
invented child answer is required; the example can end with the root call action.

Provisional optimizer recipe for a later declaration: BF16 frozen base, FP32 root
LoRA, AdamW LR1e-4/weight decay0, clip1, no dropout, fixed four updates, no validation
selection. This is a small feasibility intervention, not adequate general SFT by
assertion. Save each update with exact adapter/config, Adam/RNG and example cursor;
record target-token exposure and losses. Actual token counts must be frozen after
native rendering;32 examples does not imply compute matching with any leaf SFT.

The operator is an **author of supervised targets**, not a sampled behavior policy.
There are no old root logprobs, on-policy advantages or RL admission to fabricate.
Adaptive40 operator traces have0 sampled root actions and cannot be passed to the
root RLVR exporter. If full query-aware filtering/reduction scripts are instead
used as targets, rename the intervention **plan SFT**, not interface SFT. A useful
plan-SFT question would compare canonical all-record versus adaptive scripts from
one initial root at matched target-token budgets; that is not this tiny warm-start
screen and needs its own design.

The existing leaf-SFT trainer provides authenticated PEFT loading/audit, token-sum
causal CE, collate masks, atomic checkpoints and cursor checks. Its `data.render`
is a leaf-array/plain-assistant contract and cannot generate these root tool-call
examples unchanged. Its epoch16-example boundary is reusable for32×2, but native
root rendering, source masks, initial-root identity and evaluation callbacks need
a narrow private adapter plus tiny actual-PEFT/prefix/checkpoint tests. No new
general training framework is needed. Budget roughly30–55 A100 minutes including
load and a48-episode initial/final validation+transfer readout; cap3300s inclusive,
with training≤600s and reserved cleanup. Do not combine warm-start SFT and RLVR
before measuring this checkpoint against its exact starting model.

## Option 2: terminal-only RLVR is the closest reusable learning experiment

Proposed8 new updates from historical step8 root473210b1… with empty *new-campaign*
Adam and fixed c32de. Each update samples2 fixed training prompts×8 fresh seeds =16
episodes. Across rounds1–4, pair small context i with large context i+4. Alternate
which gets single-user/global scope by i parity; rounds5–8 revisit the same context
pairs with opposite scope. Thus each of16 declared prompts receives8 samples once,
not a stale second optimizer pass over an earlier rollout generation. Total128
training episodes. Every next generation must serve the exact new root checkpoint.

Validation:4 source-disjoint contexts×2 scopes×one fixed seed=8 episodes, at new
steps0/4/8, total24. Final primary is **fixed new-step8**, not best validation.
Final initial-versus-final comparison: two fresh32 contexts×single-user/union×two
fresh seeds and two fresh128 contexts×single-user/global×two fresh seeds =16
coordinates per weight,32 episodes. Total proposed model episodes184. Keep matched
first-root prompt IDs/sampling and all nested context outcomes; trajectories can
diverge and equal seeds do not make GPU replay deterministic. No evaluation
outcomes choose curriculum, hyperparameters or a checkpoint.

Reuse the authenticated campaign update math: native sampled root action tokens
only, child/tool/public observations masked; population-standardized advantages
within an identical task prompt; equal episode/turn weighting; one full-batch update
after all forwards; capIS2 and the frozen distribution guards. HF `current.detach`
is valid only for that one update's proximal term, with real native sampled
logprobs supplying the separate correction. The child is not loaded into the
trainable model. Persistent Adam/RNG continues **within** this new campaign, with
checkpoint after every update and committed-checkpoint recovery without double-step.

No recursion-shape/coverage admission filter: a valid direct solution can learn.
Completed wrong or malformed but otherwise native-valid root trajectories can
supply negative reward; missing terminals/partial captures, fabricated probabilities,
unsampled operator roots or causal truncation cannot. Excluded observable failures
remain visible in endpoint/cost tables. A provider/overflow null must not become
a made-up negative to increase gradient supply.

Before launching the full update sequence, the pending pilot should show at least
two distinct free-root prompts with both observed successes and observed failures,
plus successful native root export—not merely variation between different prompts.
This is a usefulness trigger, not cherry-picking those tasks into the new data.
On the new fixed curriculum, record every8-sample group: all-correct/all-wrong gives
no group-relative gradient. If an entire round has no mixed admitted group, stop
and retain it; do not reroll until mixed, switch targets by reward, or claim an
optimizer step occurred. If two successive completed rounds yield fewer than8
eligible episodes each, use the saved checkpoints to reassess the allocation rather
than extending training automatically. This stopping proposal must be fixed before
future collection, not improvised after poor scores.

### Real reuse limits, not a drop-in command

`root-rlvr-campaign-v1/campaign_train.py` supplies persistent Adam/masks/TIS/save/
recovery; the broad adapter already demonstrates24-row8/8/8 admission. The proposed
16-row8/8 admission needs a narrow count adapter and corresponding exact group test.
The native tasks/export must replace old OOLONG question/answer assumptions with
the new public query/host-gold contract while keeping honest native likelihoods.
The already-qualified operator baseline is an evaluation comparator only.

`campaign_common.original_policy/authenticate_policy` explicitly requires857a for
new step0. It cannot silently accept473210 or an interface-SFT checkpoint. A new
starting-policy manifest must distinguish historical training origin from new
optimizer generation0, bind the entire exact checkpoint closure, and explicitly
declare Adam reset; new generations1–8 then authenticate their real predecessor.
Alternatively857a/emptyAdam is the least-code baseline, but tests a different
starting policy than adaptive40 and should not be called its incremental followup.
Carrying historical Adam step8 while pretending a new step0 is unacceptable.

Provisional binary recipe otherwise retains LR5e-5, AdamW wd0, clip1, BF16 base/
FP32 LoRA, temperature0.5/native2048 cap, max8192 causal tokens, fixed depth1 and no
compaction. Existing ≥8192 rejected-child null rules and their provenance must be
explicitly selected; no broader credit relaxation. Inherited nano transient retries
remain bounded and auditable, not falsely described as zero API retries.

## Option 3: efficiency is a new objective, not a reinterpretation of correctness

Use only if completed pilot evidence shows comparable accuracy/coverage for the
fixed plans but substantial per-user work savings and free does not exploit them.
Report both global and user queries: global all16/filter16 cost is shared/identical
by construction, not an independent difference. First prefer an initial/final
accuracy–cost frontier readout; do not attach a cost reward because extra calls
merely look wasteful.

A concrete future objective candidate is
`r = exact_correct * (1 - 0.05 * min(total_logical_model_tokens / 32768, 1))`.
Total includes root and child native logical input+completion tokens, including
known work from errors; cache discounts and asynchronous wall time are not hidden
reward terms. Correct known-cost trajectories score0.95–1, wrong observed ones0;
unknown terminal/cost stays undefined and separately counted. The32768 scale and
0.05 coefficient are **proposals**, to be declared before training, not tuned on
heldout outcomes. Clipping may remove cost variation at high usage and must be
reported. A cheap-but-risky policy can still change expected reward; the coefficient
does not mathematically guarantee population accuracy preservation.

This cannot run through unchanged binary `training_group`: the reward domain,
group-advantage recomputation, continuous-reward provenance/admission and capped
token-cost accounting need a new explicit adapter and tests. Do not compare a
cost-trained checkpoint only with its untrained root and infer “cost reward helps”;
the relevant comparator is equal-budget terminal-only RLVR from the same start,
with the same declared prompt schedule, sampling counts and fixed-final rule.
Fresh rollouts must come from each arm's evolving policy, never shared stale data.
Two eight-update campaigns are unlikely to fit this memo's single1–2hour allowance.
If this trigger fires, propose a separate paired4-update-per-arm screen with its
own power/compute limitations rather than squeezing both campaigns into one claim.

## Compute, checkpoints and decisions

Completed historical root evidence bounds expectations, not promises: eight
updates used297.32 optimization seconds but the combined original/continuation
envelopes consumed2074.01+3410.33 seconds across256 training episodes, validations,
transfer, loads and saved failures. Selected transfer had more calls/logical input
despite shorter observed elapsed time. Service/loading/recursive tails, not just
backward passes, dominate planning.

For the184-episode terminal screen, propose one A100,4 concurrent root episodes,
work cap6900s +120 cleanup =7020s owned,7050s parent outer. Planning allowances:
up to4500s cumulative collection,1500s startup/authentication/model loading,600s
cumulative optimization/checkpointing and300s bookkeeping. These sum to the work
cap; they are planning reservations, not independent resettable guarantees.
Each execution retains the common setup45/rollout300/finalize15/scoring15 limits,
subordinate to remaining global time. Checkpoint every optimizer step, authenticate
base/adapter/source/optimizer/RNG/cursor, record real root-credit/delta/guard/token
and clock metrics. A cap may yield fewer than8 steps; report last committed versus
fixed final8 distinctly, and do not present a missing final readout as zero benefit.

Proposed decision criteria, finalized before any new study:

- **Promote to replication:** fixed-final improves at least4/16 paired final
  successes, no query/length stratum net decline, improvement spans at least3/4
  heldout context clusters, no lower observable coverage; native work shows
  question-conditioned selection rather than merely better final formatting.
  These are exploratory promotion thresholds, not a significance claim.
- **Revise:** early interface failures dominate; or only trained query forms
  improve; or savings come from more nulls/shortcuts; or group rewards stay flat.
  Identify that bottleneck before another run, preserve the data and partial steps.
- **Retire this training direction:** fixed filtering has no useful accuracy/work
  opportunity, free already achieves it, or a fixed-final training screen gives
  no transferable advantage while harming global accuracy/coverage. Do not respond
  with more updates/larger models without a new uncertainty they would resolve.

The analogous bootstrap research design contributes two useful principles:
same context/different question to expose planning, and valid variable rewards
before RLVR. Its 8B/two-GPU/multi-family program and SFT-first mandate are **not**
adopted wholesale here. This memo needs no new literature collection or models.

## Source guide

Exact SHA256s are in the machine feasibility file. Most relevant sources:

- [Adaptive40 frozen design](2026-09-09-adaptive-filter-pilot-design.md),
  [independent source review](../operations/2026-09-09-continuous-allocation/ADAPTIVE_FILTER_SOURCE_REVIEW.md),
  and [retry/projection caveats](../operations/2026-09-09-continuous-allocation/ADAPTIVE_FILTER_ACCEPTANCE_CAVEATS.md).
- [TREC source partitions and renderer](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/trec-leaf-sft-v1/source/data.py"),
  [SFT token loss/checkpoint loop](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/trec-leaf-sft-v1/source/experiment.py").
- [Persistent root trainer](../sidecars/root-rlvr-campaign-v1/campaign_train.py),
  [initial policy/generation identity](../sidecars/root-rlvr-campaign-v1/campaign_common.py),
  [broad24 admission adapter](../sidecars/root-broad-curriculum-v1/campaign_train.py),
  [native root mask/logprob validation](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/root-only-credit-v1/source/train_root.py").
- [Completed historical root training/transfer/timing audit](../analyses/root-continuation-live-2026-09-09/REPORT.md).
- [Bootstrap adaptive program, Study1/2/4](../../../ARTIFACTS.md#unpublished-files "Not published: ../../../repos/rlm-bootstrap/docs/superpowers/specs/2026-08-28-adaptive-context-research-program-design.md").

No pending model outputs were used. Choosing one option, freezing a starting-policy
identity, new seed namespace and final numeric recipe, reserving data, preparing
source adapters and accepting a GPU successor all remain future decisions.
