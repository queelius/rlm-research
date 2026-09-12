---
schema: research-idea-v1
id: controller-transfer-is-not-dataset-transfer-20260912
status: literature_informed_conditional_proposal
retrieved_date: 2026-09-12
primary_source: https://arxiv.org/html/2607.23771v1
source_version: arXiv:2607.23771v1
source_date: 2026-07-26
local_source: /project/alex_phd/research-cache/literature/calm-2607.23771v1/paper.html
source_sha256: 4e4fd07075c9291030f50a10abd8f71e27a600d2a26834198523758ff858073f
source_license: arXiv perpetual non-exclusive distribution license; no code license established
review_scope: Sections 2-4 and 6, Tables 1-3, Appendix C; not a reproduction
code_acquired_or_executed: false
GPU_admission: none
---

# Learning a task and learning to work in different procedures are different tests

## Primary-source finding relevant to us

CALM trains a shared Llama-3.2-3B model with several controller programs. It
separates new arrangements of familiar roles from new role interfaces and
new math datasets. Its rewards include format penalties, not just final
correctness. The reported improvements depend on the training variant and
evaluation condition; no variant wins everywhere. Role-specific loss weights
do not supply new causal credit: turns still share the trajectory advantage.
Its turn-averaged clipped ratios differ from our full-trajectory importance
correction. Training uses 2,048 examples and 192 updates; an unstable baseline
uses its best validation checkpoint. These are useful design distinctions,
not a recipe directly reproduced by our eight-update helper experiment.
[Primary paper](https://arxiv.org/html/2607.23771v1).

## Our inference and proposed small experiment

The new helper-RL gain may depend on the four-record interface used in training.
Testing another dataset with exactly that interface does not establish that
the model can work under a different procedure. Conversely, changing the
interface on old examples is not evidence about new content. Keep these axes
separate in our result catalog.

First finish the already prepared training-seed replication and skill-retention
checks. Then test the unchanged and fixed trained helper on the same article
IDs under four-record and single-record requests. Keep the instruction wording,
category meanings and keyed returns unchanged except for the necessary number
of records. Measure paired label changes, final accuracy, malformed/missing
returns and actual token cost. A fixed outcome-blind 128-record subset is enough
for an exploratory screen; do not choose the articles RL just corrected.

If the gain survives, the cheaper next direction is testing a second source
dataset, not introducing controller training without a failure to explain.
If the gain disappears or reverses under the other input size, a later
matched-example comparison can train one fixed input size versus a mix of
sizes, holding sampled record exposure and update opportunities explicit.
Even that would demonstrate request-shape robustness, not learned recursion.

At the controller level, the same distinction applies to our supplied-operator
SFT result and budgeted evidence API. Learning one interface may not teach
when to invoke it. A future pair would teach the same primitive calls in either
one fixed order or several short orders, then test unseen compositions on new
contexts. The host must not choose the decomposition for the model. Count
intermediate correctness, decision quality and final answer separately.

## Shape, decision, and limits

The helper screen would use one A100 with sequential adapters, 32 four-record
requests plus128 single-record requests per model. Use measured existing
singleton/B4 runtimes to freeze a cap before launch; expected minutes rather
than another training run. The two request shapes use different computation,
so report both quality and cost without claiming equal-budget superiority.
Keep full raw requests/responses and the original record/prompt/model hashes.
No new optimizer, router or role-weighting machinery is justified yet.

Any novel contribution would need the actual tested RLM mechanism and a
clear transfer boundary. Multi-controller training and role-weighted objectives
are already prior art; the goal is to discover what matters for our scaffold,
not rename those techniques.
