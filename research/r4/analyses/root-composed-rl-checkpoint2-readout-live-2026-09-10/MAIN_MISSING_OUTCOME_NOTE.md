---
date: 2026-09-10
status: additive_post_audit_analysis
claim_scope: fixed_exposed_panel
---
# What the missing outcomes can and cannot explain

Checkpoint2 has47 verified correct answers and5 missing outcomes; checkpoint1
has53 correct and1 missing. Even assigning all missing outcomes in checkpoint2's
favor leaves it behind. Its change is bounded by **−7 to−1 correct answers out
of72**, and **−8 to−2 on the48 composed tasks**. Relative to the starting policy,
the bounds are **−9 to−3**, overall and on composed tasks. Primitive tasks give
+1 versus checkpoint1 and no change versus the start.

These are exact binary missing-outcome bounds for this fixed panel, **not
confidence intervals**, population estimates, or proof that RL generally harms
reasoning. They preserve each known side of a partly missing pair. The original
report's known-pair difference plus/minus the number of incomplete pairs is
valid but unnecessarily loose; its positive upper endpoint should not be read
as a possible aggregate gain given the known one-sided outcomes.

The complete source is [main_missing_outcome_bounds.py](../../../../ARTIFACTS.md#unpublished-files "Not published: main_missing_outcome_bounds.py"),
which authenticates the adopted audit and checks all9 binary/NULL combinations.
[Machine-readable bounds](../../../../ARTIFACTS.md#unpublished-files "Not published: MAIN_MISSING_OUTCOME_BOUNDS.json") retain its hash.

Of43 observable composed executions,32 perform the requested calculation on a
complete observed child-label map;27 are also strictly correct. Five use the
right calculation but wrong child labels. Eleven have operator or execution
failures. One of28 strict successes is an incorrect calculation that happens
to return the correct zero. MAIN inspected all11 failures, all5 faithful
wrong-child cases, and one additional zero case; the assisting agent reviewed
all43. Neither review is human annotation.

Observed-path faithfulness is narrower than a generally valid program. Case21
contains an undefined name inside an empty generator, which is never evaluated
on that execution. Case38 has a class dictionary that may fail on other child
outputs. Preserve these qualifications when reusing the semantic labels.

The current continuation proceeds through the still-unrun fixed training
schedule, not through batches selected for improving this readout. The next
independent RL comparison lowers the learning rate from5e-5 to1e-5 from the
original SFT start with a fresh optimizer. Its motivation is exploratory;
neither a benefit nor an explanation is assumed.
