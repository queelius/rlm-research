---
schema: openai-mrcr-short-root-shaped-rl-design-v1
status: DESIGN_ONLY_MAIN_REVIEW_REQUIRED
gpu_launch_authority: MAIN_ONLY
optimizer_steps_authorized: 0
---

# One saved-batch shaped-reward root update

## Question

Can an authenticated root-only policy-gradient update use the observed *correct retrieval but raw
copy failure* signal, or does character overlap merely reinforce wrong passages?

The training reward is frozen as

`R = 0.5 * I(raw official similarity >= 0.90) + 0.5 * I(raw exact)`.

Neither the model output nor the official scorer is normalized or repaired. Raw exact, raw official
similarity, marker adherence, and the shaped reward are all retained separately. A near-exact
transport failure gets 0.5, raw exact gets 1.0, and the observed exact wrong-turn copies at
0.386555 get 0.0.

## Smallest informative branch

Use the already collected 32 explicitly training-only trajectories from eight contexts in
`openai-mrcr-short32-base-calibration-v1/outputs/attempt-002`. This is an exploratory reward-design
study, not heldout reuse. Exclude an entire four-rollout group if any rollout is scientifically
unavailable; preserve it in an exclusion receipt and never relabel it as reward zero. The resulting
frozen batch has six complete groups, 24 episodes, 74 authenticated root turns and 15,602 root
action tokens. Exactly two complete groups are mixed under the shaped reward. All six complete
groups remain in the denominator, including four zero-advantage groups; outcome does not select
individual trajectories.

This saved-batch choice is deliberate. Collecting 16 contexts x G4 before the first update would
double native collection and root replay cost without first establishing that the new reward can
produce an admissible update. The first 16 records in the pre-existing outcome-blind training rank
are frozen as the only candidate pool for a later fresh second update, but they receive no query in
this initial branch. The existing disjoint 16-record heldout split remains evaluation-only.

## Reused admitted implementation

Thinly adapt `mrcr-root-hf-one-update-preflight-v1`:

- reuse its reviewed causal `WireTrace`/native-result extractor;
- require an exact one-to-one match of prompt IDs, sampled suffix IDs, processed behavior
  log-probabilities, provider request IDs and usage for every admitted turn;
- create a fresh zero-effect rank-8 root LoRA on the unadapted Qwen3-4B checkpoint;
- keep the base child fixed, with child and tool-observation tokens masked (the saved batch happens
  to contain zero child actions, so this is a root-procedure—not recursion—update);
- credit every sampled depth-0 action suffix, including tool calls and terminal text;
- use temperature 0.5 in native behavior and HF target likelihoods;
- compute one detached, unclipped, non-self-normalized full-root-trajectory importance ratio per
  episode; require finite support, ESS >= 19.2/24 and max normalized weight <= 0.10;
- use within-question G4 RLOO advantages, root-token sequence SUM per episode, then divide once by
  the fixed 24 admitted episodes; LR 1e-5, AdamW, zero decay, clip norm 1, dropout disabled;
- require the differentiable replay to match the no-grad qualification at 1e-5/token and
  1e-4/root-turn before exactly one optimizer step.

Any group-inventory, causal mapping, importance, replay, finite-gradient, or checkpoint-integrity
failure produces an explicit zero-update result. There is no retry, reward fallback, clipping,
newline normalization, teacher answer, or SFT stage.

## Evaluation and decision

Evaluate the unchanged base root and updated root on all 16 frozen heldout contexts, one paired
rollout each with identical fresh seeds, temperature 0.5, the same six-total-root/child-turn cap,
base child, external JSON representation, and raw official scorer. A model/context overflow is
unavailable, not wrong. Primary comparison is paired raw exact; official similarity and the shaped
band are diagnostics only.

An exploratory positive endpoint requires at least two updated-over-base raw-exact wins and no
raw-exact losses, with all 32 paired endpoints available and authentic. Anything weaker retires
this *checkpoint as a positive endpoint*, not the shaped-reward direction. The checkpoint must also
report the likelihood shift, gradient norm, adapter delta, reward support, importance diagnostics
and replay diagnostics: a clean but tiny update can justify a separately frozen fixed-dose or fresh
training comparison without selecting this checkpoint. Even a positive result is over a 16-context
local heldout split, not broad MRCR generalization.

## Time feasibility

The source short32 owner took 434.64 seconds for 32 episodes. The admitted saved batch removes a new
collection stage and is smaller than the existing 32-episode/96-turn HF preflight design (24
episodes/74 turns here), whose cap is 900 seconds. Two 16-episode evaluation arms should fit in
roughly one source collection duration plus service transitions. One update plus paired evaluation
is therefore plausibly bounded near 25–35 minutes with a 2,200-second aggregate stop.

Two to four *fresh* updates are not credibly <=40 minutes: every later update needs a new native
collection under its current checkpoint plus another full HF qualification/backward pass. Do not
represent this one saved-batch update as a 2–4 step campaign. A second update is a separately
reviewed follow-on only if the first heldout readout is useful.
