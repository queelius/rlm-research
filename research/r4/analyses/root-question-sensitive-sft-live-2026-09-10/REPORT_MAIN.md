---
id: question-sensitive-sft 72
status: completed_exploratory_analysis
date: 2026-09-10
question: Can demonstrations of varied questions teach a small model to perform the requested calculation rather than repeat one familiar routine?
training_trajectories: 72
training_root_actions: 216
updates: 6
protected_contexts: 8
protected_tasks_per_policy: 72
planned_readouts: 160
native_available_readouts: 149
manual_program_paths_reviewed: 149
claim_level: strong_local_training_effect_requires_transfer_and_training_replication
primary_artifact: CONTINUATION_AUDIT.json
mechanism_artifact: SEMANTIC_AUDIT_ALL.json
training_artifact: TRAINING_CONTINUATION_AUDIT.json
---

# Varied demonstrations taught substantially more question-sensitive computation

The trained model answered 57 of 72 protected questions correctly, compared with 28
before training. More importantly, it actually performed the requested
calculation in 62 attempts, compared with 18 before training. Correct answers backed
by the requested calculation increased from 15 to 52. These gains occurred in all
eight contexts and remain positive under conservative treatment of missing
answers. This is a substantial local result, not evidence that general adaptive
decomposition is solved.

The strongest change was on questions combining operations. For example, the
model had to find users with one kind of record and then sum a different kind
of record belonging to those users. Before training, only 1 of 48 composed attempts
performed the full requested calculation. Afterwards,38 did;33 also gave the
correct answer. Earlier routine-training and primitive-only reward training had
not reliably produced this behavior.

## What changed, and what stayed fixed

We continued a previously trained Qwen 3-4B-Instruct-2507 root adapter with 72
demonstrations and six fixed full-corpus updates. Each demonstration had three
root actions: obtain labels through a real recursive model call, calculate from
the returned labels in Python, and return the printed answer. The demonstrations
varied categories, user scopes, thresholds and operations. The base model and
the c32 child adapter were fixed. Only the root adapter changed.

The data use public TREC questions, whose labels identify six question categories,
with synthetic record IDs, users and weights. These are not 72 raw text examples:
they are 72 complete tool-using trajectories, containing 216 root actions. The
128 training records form eight 16-record contexts. Four other contexts supplied
the development panel and eight others the protected panel. Contexts—not their
multiple questions—are the main clustering units.

Training/protected contexts were disjoint for this root-training process, but
the TREC records were exposed to child-model training and earlier prepared
catalogs. All operator families were represented in training; protected questions
changed parameters and combinations, including reversed category conditions and
new thresholds. This is not an unseen-operator or globally unseen-data test.

At evaluation the model received the ordinary Python/file environment and the
question, not the teacher's algorithm, an answer map, a calculation helper or a
task card. It chose its own code and recursive calls. Root actions had a 2048-token
cap, context 8192, temperature 0.5, fixed paired seeds and four concurrent workers.
The original policy was evaluated before the trained policy; serial order/cache
effects were not randomized. A fresh-seed check reverses that order separately.

## Results that distinguish answers from demonstrated computation

Every denominator below includes all planned protected questions. Unreturned or
unverified outcomes remainNULL in the underlying data; these counts are the
conservative observed-success view, not a claim thatNULLmeans known failure.

| Protected result | Before | After |
| --- | ---: | ---: |
| Native answers available | 64/72 | 71/72 |
| Correct answers | 28/72 | 57/72 |
| Requested calculation actually performed | 18/72 | 62/72 |
| Correct answer and requested calculation | 15/72 | 52/72 |
| Correct composed answers | 13/48 | 38/48 |
| Requested composed calculation performed | 1/48 | 38/48 |
| Correct answer and requested composed calculation | 1/48 | 33/48 |
| Correct primitive answers | 15/24 | 19/24 |

The paired gain in correct answers is bounded between 21 and 30 out of 72 when each
missing answer is allowed either result. The corresponding bounds are 36 to 45 for
faithful calculations and 29 to 38 for correct-and-faithful outcomes. Composed
correctness bounds are 22 to 26 out of 48, and composed correct-and-faithful bounds
are 29 to 33. These are missing-outcome bounds, not confidence intervals.

On the 63 jointly available protected pairs, correctness had 24 wins, zero losses,
27 both-correct and 12 both-wrong outcomes. Program fidelity had 37 wins and zero
losses. Correctness and correct-and-faithful counts improved in every context.
One context lost one available answer despite the overall availability gain.
The overall practical continuation screen passes; that individual loss remains
in the data and should not be hidden.

| Context | Correct before→after | Faithful calculation before→after |
| --- | ---: | ---: |
| 0 | 4→7 | 2→9 |
| 1 | 2→6 | 3→7 |
| 2 | 4→8 | 2→8 |
| 3 | 6→9 | 3→9 |
| 4 | 5→6 | 3→6 |
| 5 | 3→8 | 2→8 |
| 6 | 3→6 | 3→7 |
| 7 | 1→7 | 0→8 |

The nonzero-answer questions also improved:14→34 correct out of 46, with
13→42 faithful calculations. Thus the gain is not explained by always answering
zero. Still, zero is common:26 of 72 protected gold answers and 32 of 72 training gold
answers are zero. All were retained without outcome-based selection.

Development correctness stayed 3/8. Fidelity improved 1→6/8, but four trained
development calculations were wrong because of child labels, and one correct
answer used the wrong operation. This narrow maximum-only development panel is
reported separately and was never used to choose a checkpoint.

## One actual matched example

On protected context 5/J1, the question asks for the weight of description-category
records belonging to users who also have an entity-category record. Both policies
obtained **exactly the same 16-label child map**.

The earlier policy summed the entity records themselves and printed 14. The
trained policy first formed the set of users with entity records, then summed
description records belonging to those users and printed 21—the correct answer.
The raw programs and parent-linked observations are indices 56 and 128 in
SEMANTIC_PACK.json; both refer to coordinate
9353ced97a82745efee49b4d5c923aafe1e32df48e27212f7352dfa4c4a8feac.

This example separates the root calculation from child accuracy: the available
evidence was the same, but the trained root used it differently. It is an
illustration of the measured effect, not an additional independent experiment.

## What still fails

All 149 native-available readouts received manual review of actual sampled code
and tool observations joined by parent node and tool-call identity. No generated
code was reexecuted by the analysts. Trusted host calculations on the observed
labels were diagnostic checks, never replacements for missing model execution.
The final branch and actual child calls were checked against native-token proofs.

In the trained protected panel, ten wrong answers had the right calculation;
the actual child-label map explains every one without an arithmetic residual.
They span five contexts. Nine other available composed paths were unfaithful:
two empty final/unfinished paths, wrong scope or category filtering, incorrect
operators, and failed state recovery. Five of those nonetheless returned the
correct number. The before-training panel had 13 correct-but-unfaithful answers.

Successful recovery is not itself a failure: several trained paths repaired
Python errors and subsequently performed the correct operation. A baseline
primitive path decoded an actual child answer using copied literal IDs; that
special handling is flagged separately from fabricating labels. One development
baseline legitimately returned the defined zero after demonstrating the scoped
selection was empty; this limited case does not establish a general maximum routine.

The first delegated semantic summary accidentally omitted 12 authenticated empty
finals. MAIN's inventory check caught the mismatch; the additive V2 review restores
all 49 observed endpoints in that slice. The flawed V1 is preserved, and only V2
plus MAIN's 100 reviews are used in the combined 149-path result. All final semantic
diagnostic and native-binding checks report zero disagreements.

## Training and cost accounting

Training used rank 8LoRA, fresh Adam state, learning rate 0.0001 and six fixed
updates. The objective weighted acquisition/reduction/final actions 0.45/0.50/0.05.
Only current root-action tokens received loss; child outputs, observations and
earlier history were masked. Wrong child labels were preserved rather than
silently replaced with gold. Each full pass contained 16904 target tokens and 216
root turns; six passes exposed 101424 targets across 1296 root turns. The CPU audit
checked all six committed checkpoints,504Adam parameter states, update ordinals,
masks, RNG/corpus ancestry and the exact final selection.

The measured training/checkpoint interval was 738.78 seconds; the full training
phase including its entry/load/gate overhead was 776.73 seconds. Neither the entire
workflow nor every reserved-GPU second was optimizer work. Training loss fell
from 0.1893 to 0.04385; performance and program evidence, not loss alone, justify
the positive research conclusion.

| Physical model calls | Attempts | Known input tokens | Known output tokens |
| --- | ---: | ---: | ---: |
| Original65teacher acquisitions plus baseline | 977 | 2500952 | 100936 |
| Missing7teacher acquisitions | 7 | 8794 | 1737 |
| Trained development and protected readout | 406 | 778114 | 49494 |
| Total | 1390 | 3287860 | 152167 |

The 216 authored teacher actions are not sampled-model calls. Of 1390 physical
attempts,1382 returned HTTP 200 and 8 returned HTTP 400 with unknown token usage.
Known cached tokens total 3095248; the eight missing usage receipts are notzeros.
Evaluation calls fell 912→406, including 827→375 for protected readout. These are
workflow costs, not equal-FLOPs or provider-billing comparisons.

The original owner used 2159.55 seconds, a seven-capture recovery 215.92 seconds,
a failed pre-model GPU dispatch 38.69 seconds, and the successful train/readout
owner 1484.66 seconds:3898.82 active parent seconds in total. Originalcapture stopped
at 65 teachers. The recovery obtained the remaining seven but hit a duplicate
receipt write. The next attempt failed before loading a model because the
evaluation-client launcher hid CUDA from training. Both were fixed in additive
owners; no prior gradients or outcomes were overwritten. Completed corpus and
baseline artifacts were reused exactly once.

Separately, a session interruption consumed about 4 hours 23 minutes of idle reserved
GPU time; the dispatch-fix relaunch gap cost about 11 minutes 43 seconds. Other
intervening experiments are separate jobs, not QS training. These costs are
documented honestly in the operating ledger and are not scientific training time.

## Limits and next decisions

This is one training realization, one small model, eight protected contexts and
a structured synthetic-metadata task built on a public category dataset. There
were 160 planned readouts,150RESULT files and 149 native-available finals:10 missing
RESULTs and one unverified/unresolved result remainNULL. Sixteen authenticated
empty finals are observed policy failures under this study's prospective rule;
older experiments with different frozen rules are not retroactively rescored.

The curriculum combines varied tasks, parameter choices, genuine observations
and further training. It does not isolate parameter diversity, establish SFT
superiority over a matched RL method, demonstrate long-input transfer, or teach
new operators never shown in training. It strengthens the hypothesis that a
small model can learn to select and compose a useful routine from the question.

Three follow-ups are already underway or being prepared: a fresh-seed paired
readout, changed user names/weights/thresholds, and terminal-reward training on
composed training questions. Separate child-model validation addresses semantic
errors. New contexts, longer inputs, paraphrases and a fresh training seed remain
necessary before making a broader publication claim.

## Reproducibility map

Original immutable science: sidecars/root-question-sensitive-sft-v1, READY
92b950f663dbf76b96a4ca0e9d2e5841bb72d269b6d256f383a4e6521235fc07.
Recovered training/readout: sidecars/root-question-sensitive-sft-recovery-v1/
outputs/attempt-003. Exact final adapter:
4d8287537a9ff3d8e33bc0314f64315dee06e71b801257b389dab8b667e27aca.
Starting adapter:94022838a64a530e1abc8daf6cd43502d8aec7d549b6bfec10dd4928b0ca9006.
Child:c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3.

METHOD.md predates execution. CONTINUATION_AUDIT.json contains the unchanged
160-slot native reader routed across preserved owners. TRAINING_CONTINUATION_AUDIT.json
contains the six-checkpoint audit. SEMANTIC_AUDIT_ALL.json joins all149manual
reviews and diagnostic checks. FINAL_MAIN.json pins the report, analysis and
completed source/output artifacts. MAIN contributed recovery code, path routing
and most semantic reviews; independent readers reviewed the original new-study
design and a 49-endpoint semantic slice. This is not an independent replication.
