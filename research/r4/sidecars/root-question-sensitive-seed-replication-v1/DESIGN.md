---
question: Does the question-sensitive SFT gain survive a fresh rollout seed?
status: prospective-exploratory
date: 2026-09-10
unit: eight reused protected contexts, with nine paired questions each
---

The first SFT readout improved strict correctness from28/72 to57/72, with
program fidelity still under manual review. This follow-up measures sampling
stability, not new-context generalization or an independent training replicate.
Both the fixed24 starting checkpoint and exact question-sensitive checkpoint6
receive72 fresh rollouts on all original protected questions. No selection by
success, no replacement of original missing outcomes, no dev/test pooling.

Use new paired seeds987621001+i in original dispatch order, fresh episode IDs
and native context IDs, but identical record files, question text, token prefixes,
root2048/context8192 caps, temperature.5, four workers and fixed c32 child.
Run new SFT6 first, then fixed24, reversing original serial policy order. This
does not isolate order/cache effects, and seed changes affect both root and child.

Primary is strict correct/72, paired NULL bounds and eight context differences.
Report composed48 and primitive24 separately, zero/nonzero targets, actual
program fidelity and physical usage. Keep fully authenticated empty finals as
observed0 under the original QS rule; missing RESULT staysNULL. Do not promote
producer summaries to independently audited claims. No generated code is run
by the analyst. Retain every actual request/response/trace, missing-slot inventory,
stage receipt and owner release. No training, checkpoint selection or rerolls.

A positive paired lower bound and positive context differences in at least6/8
contexts warrant a genuinely new-task generalization study; absence narrows the
initial effect to one sampling realization. This is a practical follow-up rule,
not a significance test. Each model service gets1800seconds including startup
and cleanup; outer3900, owned3870, shared work3750. Existing fixed checkpoints
are pinned; each episode is an incremental checkpoint. MAIN authors and reviews
this exploratory sidecar; independent analysis is desirable before publication.
