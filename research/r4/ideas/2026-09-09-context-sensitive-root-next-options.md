# Next root experiment: teach query-dependent scope, not another first-four probe

September9,2026. Design only for MAIN's decision. No running coverage48/high-LR outcomes read, no implementation, data reservation or GPU calls. The brainstorming skill structures the alternatives; the bootstrap repository supplies ideas, not binding requirements for this research store.

## Recommendation and evidence

Prefer a small **authored plan-SFT comparison: classify-all-then-filter versus filter-before-classify**, with an unchanged-root calibration. Both plans complete the task rather than teaching another first-four probe. Global-query targets are identical between trained arms; user-query targets differ only in where the public metadata filter is applied. This asks whether training makes the root select the relevant scope on transferred questions and contexts, and whether that preserves success while reducing real work.

The completed72-case audit gives efab5/24, success-SFT8 9/24 and RL7 9/24. SFT increases complete relevant-map coverage15→21/24, but all three policies copy the first-four example22/24. Query-transfer remains1/8 for SFT, and at least one complete correct child map becomes a wrong root count. The ledger16 comparison gives map3/8 versus appended counts0/8: all eight ledger roots stop after the initial four records despite explicit partial coverage. These observations motivate changing what the root is taught, not merely supplying more counts or repeating the same starter action.

Three options:

| Option | Small comparison | What it identifies |
|---|---|---|
| **A: paired authored plan SFT, preferred** | Two new fixed4 adapters + unchanged SFT8;48 readout episodes | Query-conditioned scope learning versus a complete canonical plan; not self-training |
| B: native later-turn-only ablation, cheapest reuse | One new fixed8 versus existing full-trajectory fixed8;48 readout episodes | Contribution of imitating the initial probe versus later successful transitions; not aggregation alone |
| C: acquire diverse native successes | ≤64 training rollouts, conditional fixed4 SFT, initial/final48 readout | Whether genuinely model-generated successes supply diverse transferable decisions; higher acquisition risk/cost |

Do not implement all three or cross them with every harness. Coverage/high-LR results may change MAIN's priority, but this document does not peek at them or retroactively select a starting checkpoint.

## A. Smallest planning-specific comparison

Start both new arms from the already fixed success-SFT8 adapter `66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5`, not a winner chosen from the pending high-LR study. Preserve fixed c32de child, typed batch contract, local image, native root renderer and unchanged root prompt including its optional first-four example. **No ledger** in this comparison. The taught complete action may override that optional example; both trained arms receive the same opportunity.

Training uses only the immutable original adaptive **train-00…train-07** contexts,384 normalized source groups,32/64 records and single-user/global questions. Make16 operator-authored **initial root action targets per arm** (eight contexts×two scopes). They contain a complete ordinary Python plan, not host answers. Global targets are byte-identical across arms. Single-user targets use the same public user/category literals, same request builder/parser, batches16, dictionary accumulation and final printing; the sole strategy difference is `selected = records` versus `selected = relevant`. Canonical classification processes all records then counts only the relevant IDs; adaptive classification processes only those relevant IDs. Both algorithms are valid with correct child labels.

Example for a public query about numeric-value questions from useru00; only the marked line differs:

```python
import json
from rlm.api import run as rlm
from batch_contract import request_for, strict_map
records = json.load(open("records.json"))
relevant = [row for row in records if row["user"] == "u00"]
selected = records  # canonical; adaptive uses: selected = relevant
labels = {}
for start in range(0, len(selected), 16):
    batch = selected[start:start + 16]
    child = await rlm(request_for(batch))
    labels.update(strict_map(child.answer, [row["id"] for row in batch]))
print(sum(labels[row["id"]] == "numeric value" for row in relevant))
```

For a global query use `relevant = records` and `selected = records` in both arms. User/category literals are read from the public question, not host semantic labels or gold counts. A missing/invalid map raises; do not silently repair or invent a label. These are deliberately transparent **authored plan targets**, not claims of model-discovered successful trajectories. Child semantic mistakes can still make a valid program's answer wrong.

Train fresh AdamW separately in each arm, LR2e-5, weight_decay0, clip1, BF16 base/FP32 rank8 LoRA, dropout0, four complete16-example passes and fixed final4. Same master/example-order seed and identical public prefixes. Equal example/current-action-token mean loss; no child/history/observation credit. Global targets match exactly; user-action target lengths need not match. Report actual target tokens/coefficient masses, not fake padding or claimed equal gradient shares. This is a controlled training-package strategy contrast, not equal-FLOP optimization. Save real adapter/Adam/RNG/cursor after every update, never import SFT8's old optimizer or select a partial checkpoint by performance.

Readout: three roots (unchanged66cce400, canonical4, adaptive4) × the same16 coordinates =48 episodes. Take the existing fixed24 readout's **eight query-transfer and eight length-transfer coordinates**, preserving source membership, scopes and repetition structure: two32-record contexts with single-user/union queries, two128-record contexts with single-user/global queries, two fresh seeds per scope. These320 source groups do not overlap the384 training groups; all remain developmental/public/leaf-supported exposures. Union scope and128 length are absent from this training. Keep the other192 validation groups out of training too. Freeze all48 coordinates/fresh seeds/phase order before any new inference; implementation must perform a bounded seed collision scan, not reuse this day's already crowded namespaces by guesswork.

Primary: adaptive4−canonical4 strict whole ASCII Answer correctness, paired within the four contexts; give all16 pairs and each context's four-coordinate mean. Each trained root versus unchanged is secondary calibration. Report planned/observable/format/correct/NULL separately and preserve empty completed0. Preserve actual selected/requested IDs, first-four copying, union handling, relevant/irrelevant classification coverage, map-to-count agreement and full root/child/cache costs. A correct direct root solution is valid; no hidden child-use or coverage requirement. Zero child calls or a shorter answer alone does not prove adaptive planning. Cost comparisons on jointly correct pairs are explicitly selection-conditioned and accompany all-planned costs.

Provisional one-GPU cap: **2430s outer,2400s owned,2280s shared work**. Planning allowances: two360s training invocations, three420s readouts, three100s startup allowances =2280s;120s final cleanup. All stages are clipped by one absolute clock; early service release also consumes work, so simultaneous phase maxima are not a completion guarantee. The existing SFT72 three-readout package took1769s including590s training; shorter authored targets make this plausible, not promised. All48 cells remain planned even if a stage fails. No retry, extra epoch, checkpoint substitution or extended wall budget.

Small qualification only: actual native initial-prefix/tool-action rendering and mask boundaries; vetted authored program fixtures for global and single-user counts with empty relevant subset and sequential map accumulation; confirm global arm targets equal and user differences match the declared assignment. Fixture outputs are clearly synthetic/operator-executed observations, never learned child accuracy evidence. No need to sample a fake root or assign probabilities: these examples have only an initial public prefix and an authored action target, so **no fabricated child observation is required in the SFT input**. Do not run generated model code on the host.

Promote if adaptive versus canonical improves or maintains success across more than one context while the native audit shows correct query-dependent exclusion of irrelevant work on user/union cases and preserved complete global work. Lower first-four copying in both trained arms is a shared teaching effect, not the adaptive contrast. If both merely emit the taught code in inappropriate contexts, accuracy falls, or most readouts remain format/count failures, do not add epochs automatically. Pivot to transition fidelity or narrower readout diagnostics. One seed/four clusters cannot establish general planning or an optimal algorithm.

## B. Lowest-preparation alternative: withhold initial-action imitation

Use exactly the already sealed27 successful **training-only** trajectories and efab start, fresh Adam, LR2e-5, eight full passes and original981308002 orders. Control is the existing low-LR full27 fixed8. New arm keeps all original causal prefixes, but supplies CE only for root turns after the initial root action. A bounded read of the sealed EPISODES finds114 total root turns/15256 targets:27 initial turns (all source node2),2565 targets;87 later turns,12691 targets. Thus the new arm has101528 target exposures over eight passes, versus122048 in the control. Every trajectory has at least three root turns.

Retain each later turn's original coefficient `1/(27 × original_episode_root_turns × current_action_tokens)` rather than renormalizing the shortened episode. Initial terms are omitted, not relabeled as observations; their tokens remain in later causal histories. This removes initial imitation while leaving the scale of each retained term unchanged. Objective mass and total target exposure differ by design; do not call it an equal-token experiment. The unchanged trainer currently divides by `len(episode['turns'])`, so a narrow original-denominator adapter is necessary—simply deleting turns would implement a different ablation.

This is **later-transition SFT**, not automatically “aggregation-only”: retained targets include additional child requests, recovery and formatting. Existing success selection and teacher root/native token/logprob provenance stay intact, no eval trajectories or edited targets. Recorded native behavior logprobs remain provenance only for SFT, never fabricated RL weights. Compare new fixed8 and old full8 on the complete fixed24 exposure-declared readout with fresh paired seeds,48 episodes. Suggested cap2430outer/2400owned/2280work, new training≤900 and each readout≤540, remaining shared time for services/verification plus120 cleanup. No replacement checkpoint if final8 missing.

A gain would show that reinforcing the initial action was unnecessary or harmful under this training package, not that the root learned a novel context-sensitive strategy. If later-only loses coverage but preserves format, initial trajectory learning may support continued execution; if both remain wrong after complete maps, try an explicitly aggregation-conditioned target study. This is the preferred cheap substitute if MAIN wants no authored plan intervention yet.

## C. Diverse successful self-trajectories: valuable, but acquisition is the experiment

If model-generated teaching is the priority, freeze64 training attempts: eight existing train contexts×two scope queries×four fresh seeds, fixed66cce400/c32, no retries. Keep a common **new no-worked-example prompt** for collection, SFT and both before/after readouts; API names/definitions remain, but the starter code is omitted. This common prompt change is declared in advance and is not silently pooled with old SFT72. Select the earliest admitted exact success per context/scope; predeclare at least eight successes spanning four contexts and both scopes before training, with a descriptive first-action/selection-pattern diversity report. If insufficient, publish acquisition failure; do not reroll until success or use evaluation trajectories.

Every selected target must be an actual native model-sampled root action with complete causal graph, current-action mask and exact source/behavior binding. Observations are masked inputs; no stronger teacher or authored repair is mixed into “self” data. Four complete passes/fixed4 from the same initial root with fresh Adam, before/after24 readout. Cap3630outer/3600owned, collection acquisition≤900, training≤600, two readouts≤600 each, other startup/verification within3480 shared work and120 cleanup. This is more expensive and may yield too little diversity; it ranks behind A/B for immediate queue continuity.

## Shared provenance and limits

Never repurpose the five-call coverage fixture, typed fake-provider fixtures or operator baselines' synthetic probabilities as root RL data. Authored targets have no behavior likelihood. Genuine sampled self-SFT targets carry real provenance but their old likelihood is not the CE objective. Only a separately frozen RL study may use native behavior probabilities with its authenticated correction and exact terminal reward; none of these proposals adds a reward, entropy term, coverage gate or hidden answer repair.

Bootstrap inspiration is the same-context/different-question and canonical-versus-adaptive-plan comparisons, and observations-as-context/action-only loss. Its8B/two-GPU infrastructure, plain-self-training control and broad program requirements are not imported into this bounded4B study. No new literature/model acquisition is needed.

Source pins read for this memo:

- Completed success-SFT72 report: SHA256 `d17a1cbb64b82b96bc64a440b01df7b8c839ad0edd5f60d1ce2e0c0834401bff`.
- Completed ledger16 report: `b79913417b991037aa9fc4c09515601aa67682f2d2edd11400cd7fe02cf3dd36`.
- Complete-success EPISODES: `c0f40ff19c8a6f906b551202ddc733488300a3e752a97098e316fe7e17f81259`.
- `sidecars/root-interface-sft-v1/study.py`: `f8bd237f15498544af8ec72fb9442e503a5fc4b4d1ec5ff98058f2c19ece4ba4`; inspect `prompt`, `question`, `training_row`, and fixed partition/plan.
- `sidecars/root-success-trajectory-sft-v1/train.py`: qualified complete-pass/root-action CE/checkpoint seam; changing selected-turn denominators is explicit in B.
- Bootstrap adaptive program: `133a041c617b82d0d285ad0a907a5c5a0cd4fdb94540f05a79b781129a250293`; its handoff and integration philosophy were read as inspiration only.

MAIN chooses one option and binds exact seeds/source/target counts before CPU implementation. Coverage48 terminal audit takes priority if triggered.
