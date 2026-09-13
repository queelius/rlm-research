---
question: Can a model choose useful splitting from task structure rather than input length alone?
status: exploratory_hypothesis_from_small_fixed_fanout_screen
created_utc: '2026-09-12T23:59:00Z'
evidence: '../analyses/b05-helper-width-independent-2026-09-12/readout-001.json'
evidence_sha256: 1fd4008bebab107b0224f8c5ddf2d6fa1c92e1e4dabd33c526b0064da6b4329b
GPU_followup: not_admitted_before_selection_competency
---

## The concrete observation

On the order-insensitive diagnostic, flat and four-way splitting each solved
2/18 stage attempts, but on different stage cases. Both successful cases had
exactly six candidates. For root_04e8ad75e03277, flat succeeded on both samples
and four helpers failed on both. For root_8ede992f33e6e9, four helpers succeeded
on both and flat failed on both. Two helpers succeeded nowhere. Thus a fixed
threshold based solely on candidate count cannot select the successful arm in
both observed cases. Other input structure, stage identity or a lucky partition
could explain this; it is not evidence that a learned router would generalize.

A post-hoc chooser with access to the correct outcomes could obtain4/18 instead
of2/18. That is an oracle upper bound on these recorded outputs, not an executed
model or prospective selection policy. There are only two successful stage cases,
and both repeat samples share the original case. Do not train and evaluate a
chooser on these same labels and call the improvement transfer.

## What this suggests

First learn to identify eligible records at all. The fixed splitting results do
not justify a broad fan-out sweep: four helpers cost42% more input tokens and
trade higher precision for lower recall. The current selection-RL pilot addresses
whether partial credit can improve those choices; all-or-nothing rewards had no
contrast across the nine flat training pairs.

If that succeeds, the next meaningful adaptive experiment should vary candidate
count and relational difficulty independently. Compare flat, always-split and a
prospectively frozen task-sensitive chooser on new generator seeds, retaining all
answers and measuring correct complete results per token/call. A shallow policy
must first beat both fixed choices, not merely beat a deliberately bad threshold.
Only then consider another recursion level, with a separate budget and stopping
decision. No learned recursion or publication-ready routing result exists yet.
