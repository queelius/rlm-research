---
schema_version: rlm-question-card-v1
id: "rq:public-state-and-decision-accounting"
title: "What should Python organize, and what should the model decide?"
status: fresh_same_family_harness_signal_followups_proposed
updated_utc: "2026-09-13T01:00:00Z"
evidence_cutoff: "2026-09-13T01:00:00Z"
phase: exploratory
publication_readiness: mechanism_lead_not_methods_claim
related_questions: ["rq:rl-effective-feedback", "rq:adaptive-decomposition"]
gpu_status: completed_and_released
new_jobs_admitted: false
reports:
  - "../analyses/b05-public-normalization-independent-2026-09-13/outcome-001/FINDINGS.md"
  - "../analyses/b05-public-normalization-fresh12-independent-2026-09-13/outcome-001/FINDINGS.md"
  - "../analyses/b05-flat-selection-rl-dose10-independent-2026-09-13/FINDINGS.md"
  - "../analyses/b05-selection-id-renaming-audit-2026-09-13/REPORT.md"
---

# What should Python organize, and what should the model decide?

## Evidence and current interpretation

Python combines public changes and latest checks but retains every candidate
and never computes eligibility. This improved complete candidate selections
from 0/18 to 4/18 initially, then 1/24 to 9/24 on twelve new cases answered twice.
Fresh gains occur in five cases, all with six candidates. Larger cases improve
partially but remain incomplete. Input tokens fall 52%; list-order failures
remain separate. Different histories occur on different instances, so history
length is not isolated. Both tests use one generated task family.

Two limitations motivate a different next comparison. Many remaining wrong
selections visibly violate explicit failed checks. Other answers contain only
good candidates but omit required ones. Separately, consistently renaming IDs
changes the model's selections strongly, and larger selection-RL updates trade
away recall. More bookkeeping alone, more helper calls, or a higher reward score
cannot be assumed to solve these problems.

## Ranked, falsifiable follow-ups

1. **Explicit decision accounting.** On twelve new frozen cases, compare the
   same organized input with either a selected-ID list or one yes/no decision
   per candidate in fixed public order. Two paired seeds gives 48 calls on the
   released 4B model. Score complete sets, missed good and included bad records,
   output validity, calls and tokens. Do not infer missing decisions or repair
   answers. A useful signal is better complete sets without hiding recall loss;
   retire the interface if it merely moves errors into positions or formatting.
   Expected one A100, under ten minutes including startup; 600-second science
   cap and per-call saved outputs proposed, not yet implemented or admitted.

2. **Separate resolved facts from shorter presentation.** Compare raw tables,
   compact unresolved records, and resolved records on the same new cases.
   Preserve every public field needed by the task. Report actual length, wording
   changes and truncation; do not call this perfectly token-matched unless it is.
   Twelve cases × two seeds × three views = 72 calls, one A100, proposed
   900-second cap. Promote only if the contrast identifies more than a generic
   prompt-length benefit. Keep the first interface experiment independent.

3. **Train varied candidate decisions.** If decision accounting helps, sample
   new policies, applied histories, candidate permutations and class balances.
   First inspect whether sampled alternatives differ meaningfully in reward.
   Train decisions with a declared false-positive/false-negative tradeoff and
   evaluate complete answers as well as the reward. Freeze case-level and
   structural holdouts before recipe selection; do not reuse today's exposed
   held panel as an untouched test. A small multi-batch pilot with frequent
   optimizer/RNG checkpoints precedes any longer campaign. Its exact data,
   seed, optimizer and cap require a new ready manifest; it is not run-ready.

4. **Choose when to split or recurse.** After the above, compare a learned or
   explicit error-based chooser with fixed keep-together/organize/split rules.
   Count all child calls and repeated context tokens. Escalate depth only when
   an observable unresolved subproblem predicts benefit; a post-hoc best chooser
   is a diagnostic upper bound, not a learned policy. Validate on another task
   family before claiming general decomposition. No recursive pilot prepared.

## Publication path and stopping rules

The prospective contribution is a measured allocation of work between mechanical
state preparation and learned decisions, possibly with a cost-aware choice of
view or depth. A hand-designed task-specific transform alone does not establish
novelty. Compare relevant preprocessing/tool-use methods and demonstrate broader
transfer before a methods paper claim. Negative mechanisms can support a careful
diagnostic study, but need replication beyond this small setting.

Do not continue fixed-batch learning-rate sweeps after the observed local-fit/
recall tradeoff. Do not increase helper counts just to occupy the GPU. Retain
every outcome, immutable input, split lineage, model/adapter/template revision,
reward/decoding settings, output mask, cost, and checkpoint path. Report source
sorting constraints separately from semantic set correctness.

Open uncertainty for later discussion: should task success require exhaustive
recall at nearly any cost, or allow a precision/recall tradeoff? For now the
declared task requires every qualifying candidate, so complete-set correctness
remains essential even when a graded training reward rises.
