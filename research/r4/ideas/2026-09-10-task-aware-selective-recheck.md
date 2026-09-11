---
title: Task-aware selective label verification
date: 2026-09-10
status: prospective_design_only
gpu_authorized: false
priority: after_confidence_vs_uniform_recheck
---

# Question

At a fixed 25% child-label review budget, does combining native label confidence with a record's
local influence on the public J1 reducer improve final answers more than confidence alone?

This is the next comparison, not a replacement for the already-designed confidence-versus-uniform
study. The ceiling produced complete maps at 88.20% label accuracy but all eight nonzero J1 answers
were wrong, while the oracle-label public reducer was 8/8. The confidence audit separately found
that the lowest-confidence quarter captured 64.0–69.0% of c32 errors. Together they motivate asking
which likely errors matter to the downstream computation.

# Minimal 24-call comparison

Use the same immutable eight exposed ceiling episodes, original predicted maps and per-label mean
chosen-token log probabilities. Freeze two arms before new model calls:

1. **Confidence:** exactly the existing lowest-confidence `size/4` selection.
2. **Confidence × local J1 influence:** for every record `i`, enumerate its five alternative legal
   labels in the *public* `reduce_j1(records, labels, spec)`. Define
   `I_i = max_alt |F(map[i←alt]) - F(map)|`. Rank within episode by
   `(descending uncertainty-percentile × I_i, descending I_i, ascending confidence,
   fixed SHA tie-break)` and select the same 16/64 records.

`I_i` is a finite one-label counterfactual sensitivity, not a derivative, causal influence, error
probability, or expected value of information. It uses the predicted map and public records/spec
only. It never uses host labels, gold answers, known error identities, or oracle contributions.
Qualifying-user-set changes and contribution-vector changes are frozen diagnostics, not selection
terms. This keeps the primary intervention legible despite J1's threshold-like interactions.

Each arm repacks selected records exactly as the existing study: one 16-record call for each
size-64 episode and two 32-record calls for each size-256 episode, hence 12 calls and 320 reviewed
labels per arm, 24 calls total. Use the same c32 model, full six class definitions, exact output
contract, temperature 0.5/top-p 1, four workers and 90-second request cap. Pair newly catalog-checked
seeds by episode/repack index. Prompts contain only selected public records and definitions—not old
labels, confidence, influence, gold, or J1 internals. Valid batches overwrite every selected label;
invalid observed batches invalidate that episode and unavailable batches are NULL. There is no
partial salvage, answer fallback, retry, or reroll.

Before launch, publish selection overlap by episode. If the two arms select more than 90% of the
same records overall, retain the frozen design but do not spend GPU: the panel cannot discriminate
the policies. Do not tune the formula or cutoff using gold to force separation.

# Measures and decision

Primary: paired change in absolute J1 error relative to the immutable baseline, task-aware minus
confidence, over all eight planned episodes. Also report exact J1 repairs/regressions, wins/losses/
ties/NULLs, selected initial-error recall, corrections and regressions, merged-map accuracy,
qualifying-user error, contribution error, selection overlap, and results separately at sizes64 and
256. Gold is analysis-only after both selections are sealed.

Promote to genuinely new source clusters only if at least 11/12 calls and 7/8 episodes are valid per
arm, task-aware has lower absolute J1 error in at least 6/8 episodes, yields at least two more exact
J1 repairs than confidence, and has no material availability or token-cost disadvantage. Revise if
task-aware finds high-influence errors but rechecks regress; retire this local worst-case score if it
mostly selects correct labels, misses jointly influential errors, or loses to confidence in at least
half the episodes. These are practical small-panel gates, not evidence of equivalence or absence.

One released c32/Qwen3-4B service, 24 calls, expected roughly 2–5 minutes from the completed
40-call ceiling, with a conservative 1,200-second inclusive cap. The frozen ceiling calls are shared
historical acquisition cost and counted once; all new physical calls, native IDs, request hashes,
input/output/cache tokens and unknown usage fields are retained. The same four nested clusters are
research- and optimizer-exposed, so a pass is exploratory mechanism evidence only.

# Prior art and caution

- [Utility-Directed Conformal Prediction](https://arxiv.org/abs/2410.01767), v2 2025-02-28,
  demonstrates the broader principle that uncertainty representations should incorporate downstream
  costs, including nonseparable costs. It supplies motivation, not our selection formula or a
  coverage guarantee here.
- [Active Learning with Expected Error Reduction](https://arxiv.org/abs/2211.09283), 2022-11-17,
  formalizes selecting information by expected downstream error reduction, but its Bayesian
  retraining setting is materially different from one-pass LLM rechecks.
- [CoRefine](https://arxiv.org/abs/2602.08948), 2026-02-09, uses confidence as a control signal for
  adaptive refinement rather than a correctness guarantee. It is problem-level learned routing,
  not record influence under a deterministic reducer.
- [Inference Scaling Laws](https://arxiv.org/abs/2408.00724), v3 2025-03-03, supports measuring
  inference strategy by cost/performance tradeoffs; it does not address downstream-aware record
  verification.

Read depth on 2026-09-10: complete local ceiling and confidence reports, complete existing selective
recheck design plus no-fallback amendment, complete public J1 reducer source; Utility-Directed
Conformal Prediction abstract/introduction/problem formulation/method through nonseparable-loss
construction; abstracts and metadata for the other three papers. No repository clone or download.
This combination is not claimed novel.

# Local pins

- ceiling report: `4ccb7a60082d0bc76e8de88f5500514efca7ba61cf4afd42931a6c7ec04f892e`
- confidence report: `4cd2686d57c4d67dd938fa1fc912b7eba741d45aeddfa7ac8cc159c85c161431`
- confidence-versus-uniform design: `cfbeba041ed5353dc2eaaf97ae574eb1ee2bc0ff0ce2e10c56dfa7f0c9f436ec`
- public J1 protocol: `248a78f6e3a3adf7068a194bcaa40e56abdfe95de9a5f1e640f52a4dae15032c`
