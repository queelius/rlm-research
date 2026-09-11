---
id: sft24-terminal-rlvr-warmstart-design-v1
status: prospective-design-only
date: 2026-09-10
recommended_variant: eight-window-three-hour
gpu: one-a100-40gb
---

# Can terminal reward refine an execution-capable SFT24 root?

## Recommendation

Run the **eight-window, three-hour** variant first. It is the smallest comparison that preserves all
six supported operator/scope cells, uses eight training contexts, can make at most eight fresh RL
Adam updates, and still protects the full 96-endpoint paired readout. Do not adaptively extend it to
12 windows. A separately frozen 12-window/four-hour run is justified only if eight windows produce
too few mixed groups to test learning—not because an interim checkpoint looks promising.

The falsifiable question is: starting from exact operator SFT24, does unchanged terminal-only RLVR
increase nonzero, freely executed primitive and composition success without sacrificing native
availability? The contrast is the whole RL package versus the identical SFT24 start, not “RL” in
general and not isolated reward shaping.

## Why this is different from the failed QSR campaign

The sealed QSR run made 10 real Adam updates but moved strict accuracy only from 2/48 to 4/48; all
four trained successes had gold zero, final child use was 0, and trained availability fell from
46/48 to 36/48. It therefore does not support repeating that exact low66c recipe unchanged. SFT24 is
a materially different reachability start: its prior fixed readout showed genuine child acquisition
throughout and 29/48 strict outcomes on returned evidence, though its availability and faithful
reduction remained imperfect. Terminal RL may now receive mixed reward on trajectories that actually
reach useful state. That is the uncertainty this pilot tests.

## Frozen training comparison

- Start from the exact SFT24 adapter `94022838…`, config `9cab9150…`, state `75b31388…`, over the
  same released Qwen3-4B base. Its LoRA rank 8, alpha 16, target modules, and base path match the
  qualified QSR trainer's adapter shape. Start a **fresh RL Adam0**; never load SFT optimizer state.
- Use QSR training contexts `training-00` through `training-07`, never any evaluation context. Each
  context contributes its three already-defined supported primitive tasks and eight fresh samples:
  8 windows × 3 task groups × 8 = **192 planned episodes**. This mechanically retains four task
  groups for each of the six supported cells. The frozen group truths contain 3 zero and 21 nonzero
  groups; report zero/best-constant support, but do not rebalance or reroll.
- Freeze new seeds before sampling (proposed master `981731001`, training
  `981731101`–`981731292`) and require a named-plan/reservation integer collision scan. Preserve the
  original task/context order or a predeclared hash order; never order from model outcomes.
- Keep c32 fixed, temperature .5, eight samples/task, root-only current-action masks, equal episode →
  turn → action-token weighting, PPO clip .2, TIS cap 2, LR 5e-5, weight decay 0, gradient clip 1,
  and the qualified processed-logprob guards. Child/actions/observations remain causal context but
  receive zero loss. Reward is exactly 1 for an authenticated native `Answer: N` equal to host gold,
  otherwise 0 for a completed wrong/malformed final. Missing/unverified endpoints are NULL, with a
  separate planned-as-zero sensitivity. No shaped process reward, forced recursion, repair, or refill.
- Admit an update only from a complete, integrity-clean 24-slot window with at least one qualified
  mixed task group. Homogeneous/no-admission windows advance only the candidate cursor. Record all
  192 endpoints, strict reward mass, endpoint availability, exclusion reasons, admitted groups and
  action tokens; a no-op is evidence, not a replacement opportunity.

## Interface identity

Do not silently restore the ambiguous old QSR wording. Training should compose the pinned QSR native
renderer/task wrapper (`qsr_native.py` SHA `02aea033…`) with the current explicit operator questions
(`od_protocol.py` SHA `1ee6f9c7…`), including “all records, regardless of which user owns them.”
Freeze the exact system/tool inventory, task files, first token IDs, role binding, c32 grammar, and
gold-mutation invariance. This is the same current file-only free interface used to train/read SFT24;
only the question/context naturally changes. Readout must use the already-frozen composition-study
prompts byte-for-byte.

## Mandatory readout and decision rule

Compare unchanged SFT24 against the **last committed** RL checkpoint on all 48 frozen
operator-composition-transfer questions (8 contexts × 3 primitive + 3 composition), using one new
paired seed per question (proposed `981732101`–`981732148`). This is a new stochastic repeat on an
already research-exposed panel, not confirmation or independent context evidence. Both policies get
identical task bodies and seeds.

Primary: planned-denominator strict accuracy, native availability/NULL bounds, paired wins/losses,
and nonzero-gold results, reported separately for 24 primitive and 24 composition coordinates.
Mechanism: actual authenticated child acquisition, map coverage/quality, faithful executed
operator/scope reduction, stopping, loops, and physical root/child/token cost. Child calls are not
mandatory for task correctness and ceremonial calls earn nothing. Contexts (8), not 96 endpoints,
are the highest independent units.

Promote only if the trained arm has paired **nonzero** wins plus authentic acquisition→reduction→stop
examples and no material availability regression. If updates occur but gains remain zero/constant
compatible or execution disappears, retire this terminal-only warm-start recipe. If fewer than three
mixed windows update, call the learning contrast weakly instantiated and prefer a separately frozen
12-window run or a balanced terminal-support study; do not reinterpret the unchanged readout as a
negative learning result.

## Compute and implementation boundary

Use one A100 40 GB and a 10,800-second inclusive envelope: 10,500 work, 10,680 owned, 120 outer
margin; reserve 5,100 seconds for two 2,550-second readout blocks and allow at most 5,400 seconds for
eight training windows. Old QSR's 12 windows + 96 readouts took 5,129 seconds, including 2,461 seconds
rollout and 376 seconds optimizer/checkpoint time, so this is conservative but not a guarantee.
A 12-window version would retain the old 14,400-second outer / 9,000 training / 5,100 readout shape.

Reuse the authenticated QSR exporter and numerical trainer, but write a narrow new starting-policy
binding: SFT step 24 and fresh RL step 0 must be separate fields. Do not clone the old owner unchanged;
its broad cleanup alarms and incomplete raw-cost union need the newer fixed-deadline cleanup and
REQUEST/RESPONSE/RESULT/FAILURE/physical ledger semantics. This document authorizes no implementation
or launch.

## Evidence read

- QSR audit report SHA `46ad5bba…`; owner terminal `30d2681d…`.
- QSR recipe SHA `860afe82…`, trainer `a5064c27…`, exporter `3b0e58ef…`.
- SFT24 operator audit report SHA `1933a578…`; exact adapter/config/state hashes above.
- Composition study is an exposed prospective readout source; no composition outcome was used to
  select tasks or this recommendation.
