---
title: Task-aware recheck after confidence repaired labels but not J1
date: 2026-09-10
status: result_informed_design_brief
gpu_authorized: false
source_result_sha256: 8e7d00d18f2953f8cb8a5d7af24d3fe1469d8e1c4e2767461873082c569758e3
---

# What changed

The completed confidence-versus-uniform study establishes useful targeting but inadequate
verification quality. Confidence found 107/151 initial errors and produced 71 repairs versus 31
regressions (`+40` net); uniform produced 19 repairs versus 28 regressions (`-9`). Yet confidence
repaired only 1/8 exact J1 answers versus 0/8 for uniform. More confidence-only review is therefore
not the next discriminating experiment: label targeting improved strongly while downstream exactness
barely moved.

# Smallest joint test: target × verification policy from 48 physical calls

Keep all eight exposed ceiling episodes and the fixed 25% budget. Freeze two selections without
gold: (C) the existing lowest-confidence quarter and (R) confidence multiplied by local public-J1
one-label worst-case sensitivity, exactly as specified in the parent idea card. For each selection,
make two independently seeded but otherwise identical second-pass samples A and B using the same
12-call 16/32-record repacking. This is 2 selections × 2 samples × 12 = **48 physical calls**.

Derive two prespecified policies per selection from those calls:

- **single:** overwrite every selected label with sample A;
- **agreement-abstain:** overwrite only when A and B emit the same valid label; otherwise retain the
  immutable first-pass label for that record.

A/B sharing makes this an efficient paired policy comparison, not four independent arms. Retention
on disagreement is an explicit abstention rule, not hidden repair. Any unavailable or whole-batch
invalid A/B call makes that episode NULL for agreement-abstain; do not salvage partial batches.
Single remains scoreable only when all required A calls are valid. No gold, old label, confidence,
influence, or J1 contribution is shown in the child prompt.

This separates two intervention dimensions:

1. **Target:** R versus C at fixed verification policy asks whether likely errors with greater local
   downstream influence deserve priority.
2. **Verification quality:** agreement-abstain versus single at fixed selection asks whether a second
   independent observation reduces harmful overwrites enough to improve J1.

Primary is paired absolute-J1-error change over all eight planned episodes, with target and
verification simple effects and their descriptive interaction. Report exact repairs, label
repairs/regressions, abstentions, wrong-label agreements, qualifying-user and contribution errors,
selection overlap, sizes separately, NULL bounds, physical union and known/unknown usage. Local
sensitivity is neither a derivative nor VOI; two-sample agreement is not calibrated confidence and
correlated model errors may agree incorrectly.

Practical promotion requires at least 7/8 valid episodes per derived policy, R beating C on absolute
J1 error in at least 6/8 under agreement-abstain, agreement-abstain beating single in at least 6/8
for R, at least two additional exact J1 repairs over confidence-single, and no material availability
or token-cost imbalance. If targeting helps labels but consensus still does not move J1, prioritize
a different verifier or task representation rather than a larger confidence review. Forty-eight
calls should fit comfortably within a conservative 1,200-second single-A100 envelope based on the
completed 24-call study; all source clusters remain exposed and correlated.
