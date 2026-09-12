---
title: A larger update learns answer delivery; test fresh contexts before claiming transfer
date: 2026-09-12
cutoff_utc: '2026-09-12T23:37:00Z'
status: exploratory_followups_active
question_ids: [rl-effective-feedback, decomposition-stability]
---

## Decision, not just another score

The same original training batch now distinguishes an ineffective update from
training the wrong skill. Exact training outcomes are 7/32 before RL, 17/32 at
LR1e-5, and24/32 atLR1e-4. All17 larger-update gains preserve retrieval programs
and observations and repair edge whitespace. Clean retrieval stays24/32. The two
uniformly wrong selector contexts remain0/4 each. Thus local learning is real,
but final-answer-only training has not taught information acquisition.

On the exposed held16×2 panel,25→28/32 means5wins2losses. All5wins preserve the
program/observation:4edge whitespace,1other copying correction. One regression
produces no usable action; another changes the program and generates an incorrect
10820-character answer after a clean target. Clean observations30→29; output
20739→23618tokens. These are provisional delivery gains with behavioral risk,
not improved retrieval. Fixed originalcp32 versus fixedLR1e-4 on32unused balanced
four-needle contexts is the next test, both arms regardless score. No further
optimizer dose is authorized by this note.

The one-step nominalLR-only recipe differs in backward arithmetic: preclip norms
24.309086 and24.299284. ActualdeltaL2 .0404606563→.4046062082. Prestep logprobs
are byte-identical; do not claim bitwise identical gradients or full-trajectory RL.
Objective uses12credited final actions/5056tokens with20zero-advantage examples
retained in denominator32, capped detached token importance weights (biased).

## Do not confuse list ordering with eligibility

IDs-only24 versus qualified fullreports: strict exact2→4,valid22→18. All6invalid
ID lists are known unique IDs in nonlexicographic order. The separately labeled
inert unordered-set diagnostic is2→6 exact,40/64→44/64 eligible-ID recall,
40/42→44/46 precision. Removing only ordering at host combination still0/32
global solutions. Four root units, dependent alternative combinations, not32IID.
This is evidence to try smaller helper scope, not a successful architecture yet.
Fixed1/2/4 fanout126calls on9fresh stages is active under MAIN's explicitflock.

## Additional family and operational limits

FinQA16paired32 finished65.703s, allavailable/runtimequalified. Direct0/16target
matches, allvalid; DSL0/16, allinvalid. Initial native inspection shows literal
`#i` references, inventedoperations and excesssteps. Actual basecheckpoint/LoRA
disabled confirmed by CPU agent; allnormalstops, max361/384. Independent native
and source-target audit ongoing. No semantic failure rate claimed from supplied
targets. Consider synthetic worked examples only after distinguishing prompt/
interface misunderstanding from scoring defects; never fix using held answers.

GPU allocation5801 endsSep15 17:30UTC. Sharedquota27% at23:29:26UTC;next23:44.
Winddown optionalfanout at20%,pause discretionarygeneration15%,reserve10%.
Ready preparation lag after IDs and FinQA left avoidable idle intervals; these
are operations costs, not GPU science. Next tasks overlap CPUprep with126calls.
Last verifiedremotes RLM763a190/notebook8135449@22:56; newevidence notpushedyet.

## Main evidence pointers

- `openai-mrcr-fresh8-rloo-dose10-paired-2026-09-12/readout-001.{json,md}`
- `b05-eligible-ids-independent-2026-09-12/RESULTS.json`
- `b05-eligible-ids-independent-2026-09-12/ORDER_DIAGNOSTIC.json`
- `../operations/2026-09-12-b05-width-queue/START.json`
- `../sidecars/finqa-scalar-vs-dsl-v1/outputs/attempt-001/RESULT.json`
