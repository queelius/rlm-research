---
id: selection-rules-or-record-identities
status: proposed_after_first_selection_readout
phase: exploratory
created_utc: 2026-09-13T00:31:00Z
question_family: rl_selection_transfer
priority: high_if_local_selection_gain_is_verified
gpu_admitted: false
---

# Did training learn an eligibility rule or particular record IDs?

The first selection-focused update appears to remove five false-positive
selections on its training stages, with no aggregate loss of true positives.
It has not improved the nine fresh stages. These are collector summaries pending
the saved-native audit. One training reply per model is not a valid ID set, so
the valid-case denominators and whether that is the same coordinate matter.

A plausible explanation is that credit on opaque ID strings teaches particular
IDs to include or avoid, rather than the underlying policy. An alternative is
that one small update only weakly learns a transferable decision. Increasing the
update size can probe the latter but will not distinguish rule learning from
memorization on its own.

The cleanest next diagnostic may be a public, reversible renaming of every
implementation ID in the training problems. Replace IDs consistently in all
public implementation/change/check records using a fixed outcome-blind mapping;
keep all numeric values, policies, check results and substantive structure the
same. Transform host labels separately for scoring, never for constructing the
public mapping. Evaluate both released base and the fixed learned checkpoint,
with the same paired seeds and output allowance. Preserve both directions of
the mapping and all exact prompt hashes. Do not rename only errors or only
rewarded candidates.

Start with the nine original local training stages and two paired decodes per
model,36 new calls. Compare against the original paired readout descriptively
and keep native service/precision settings identical where possible. Fresh
controls may be required if runtime drift obscures the contrast. Changed
tokenization and stochastic generation are caveats; one failed renaming probe
would not by itself prove memorization.

If the trained advantage survives unrelated identities, test new policies and
histories next. If it disappears while the base model stays stable, investigate
representations and training diversity before another learning-rate sweep. A
future split should group by underlying instance and by identity remapping, so
different names for one problem never masquerade as independent new problems.

This is a proposed mechanism test, not an admitted GPU run or established result.
