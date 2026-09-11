---
title: Separate planning credit from child errors, and selection from repair quality
date: 2026-09-10
status: result_informed_research_queue
author: MAIN
gpu_authorized: false
priority: after_sparse_recovery_fixed_readout_and_ready_child_harness_jobs
local_evidence:
  - ../analyses/root-question-sensitive-terminal-rlvr3-live-2026-09-10/AUDIT.json
  - ../analyses/root-lambda-supplied-plan-ceiling-live-2026-09-10/REPORT.md
  - ../analyses/root-supplied-plan-selective-recheck-live-2026-09-10/REPORT.md
sources:
  - url: https://arxiv.org/html/2603.13853v3
    version: v3
    revision_date: 2026-05-26
    read_depth: abstract_and_sections_2_1_to_2_2_1
  - url: https://arxiv.org/html/2605.27788v1
    version: v1
    revision_date: 2026-05-27
    read_depth: abstract_method_sections_3_1_to_3_4_and_compute_warmup_tables
  - url: https://arxiv.org/abs/2605.24613v1
    version: v1
    revision_date: 2026-05-23
    read_depth: abstract_only
retrieved: 2026-09-10
assets_downloaded: false
novelty_established: false
---

# Why these questions now?

The root can execute the requested calculation yet receive a wrong final-answer
reward because the child supplied wrong labels. Conversely, a coincidentally
correct zero can reward an unfaithful calculation. One RL update did not improve
the protected readout, but that is far too little training to declare terminal
RL ineffective. First finish the exact long-trace recovery and fixed readout.

Separately, confidence-directed rechecking found errors but also broke31 correct
labels. Selection and repair quality are distinct: spending review effort in
the right place does not guarantee that the replacement is better.

# Primary literature: useful distinctions, not claims of replication

[APEX-Searcher](https://arxiv.org/html/2603.13853v3) separates planner RL from
executor SFT. Its plan reward matches generated subquestions to annotated
decompositions using semantic similarity and bipartite matching. This is relevant
to root/child credit entanglement, but it requires reference decompositions and
does not verify arbitrary Python execution. We should not call a plan-similarity
reward objective semantic correctness, nor claim that we reproduce this method.

[CARL](https://arxiv.org/html/2605.27788v1) assigns separate advantages around
tool invocation, evidence assimilation and final commitment using a learned
critic. Its method includes substantial critic warm-up, and reported experiments
use eight H100s. The useful lesson here is to separate acquisition from evidence
use; a full CARL reproduction is not the smallest experiment on our one A100.
Its shared-backbone critic and training cost also differ from our present setup.

[GuardedRepair](https://arxiv.org/abs/2605.24613v1) explicitly distinguishes
generating a candidate from deciding to replace an existing answer, and reports
both fixed and broken answers. It uses deterministic checks in mathematical
reasoning. Our two-sample label agreement is not such a verifier: correlated
wrong answers can agree. We borrow the evaluation distinction, not a guarantee.

An additional OpenReview search result, `nv1jzr0FaZ`, describes harm-aware
selective runtime verification and a small oracle-verifier pilot. Direct access
was blocked by browser verification, so this is an unreviewed prior-art lead,
not an inspected paper or a basis for a novelty claim. No access control was bypassed.

# Ranked follow-ups

1. **Ready design: targeting × replacement quality.** The existing48-call
   design compares confidence with confidence×public-calculation sensitivity,
   and unconditional replacement with two-sample agreement-abstention. Its
   selections overlap51.25%, so it can distinguish the targets without tuning
   on gold. Single uses one sample; agreement uses two and must pay that cost.
   One A100, expected a few minutes,1200-second cap. Keep its frozen downstream
   gate; failure should redirect us toward a stronger verifier or representation.

2. **Candidate: training with reliable versus noisy child evidence.** From the
   same root checkpoint, compare a short terminal-RL continuation with the fixed
   actual child against one with reference child labels during training only.
   Evaluate both with the actual child and identical held-out requests. This
   asks whether child error masks a learnable planning signal, not whether oracle
   evidence improves test answers. Before implementation, establish an exact,
   narrow binding between genuine child requests and source records; arbitrary
   prompts cannot be silently replaced by gold. Record exposed labels and every
   intervention. Start with one paired collection window to measure reward/group
   support; run equal planned windows, retain actual/no-op update counts, and
   checkpoint every update. A provisional2-hour one-A100 cap must be calibrated
   from the current long-trace recovery. Do not fabricate equal optimizer doses
   by rerolling homogeneous groups.

3. **Candidate: reward correct use of the evidence actually received.** A
   root-only reward based on the final answer implied by a genuine complete child
   map could separate execution skill from classification skill. But final-value
   agreement alone can reward accidental zeros or invented maps. Do not launch
   this until a bounded, independently validated execution-evidence criterion
   exists. Manual test-set path labels are analysis-only, not training targets.
   Never execute downloaded or sampled code merely to audit it. This remains
   lower-readiness than the noisy-versus-reference-child diagnostic.

# Decision discipline

Do not infer a credit-assignment mechanism from one weak RL dose. Promote a
training direction only after the actual child readout improves without losing
grounded execution; replicate promising effects with new contexts/training seeds.
If better selection and safer replacement improve labels but still not final
answers, investigate sensitivity of the task and child competence before adding
another layer of controller complexity. These questions are exploratory and may
be revised in response to the next completed runs.
