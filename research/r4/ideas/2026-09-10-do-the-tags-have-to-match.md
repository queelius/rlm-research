---
id: rq-matching-tag-identity-versus-format
created_utc: 2026-09-10T23:39:00Z
status: proposed_not_ready
phase: exploratory
question: Do identical tags on input and output help beyond adding structure on both sides?
priority: after_whole_task_bridge_and_second_model
depends_on:
  - leaf-mnli-stable-anchor-vs-sequence-counting-live-2026-09-10
model: Qwen/Qwen3-4B-Instruct-2507
model_revision: cdbee75f17c01a7cc42f958dc650907174af0554
gpu_shape: one_A100_40GB
proposed_gpu_cap_seconds: 1800
proposed_new_calls: 192
evidence_status: no_model_outputs_for_this_comparison
---

# Do the input and answer tags actually have to match?

## Why this question is now worth asking

Our completed test found 84.9% later-record accuracy with arbitrary matching tags,
85.4% with row numbers, and 34.2% without matching keys. It shows that ordinary
counting order is not necessary. It does not show that literal matching is the
only useful part of the interface. Adding distinct fields on both sides may help
the model keep track of records even when the tag values do not match.

This distinction matters for the paper's explanation. We should describe the
successful package accurately now and test the explanation, not promote the
word “matching” from an intervention description into an established mechanism.

## A small, balanced comparison

Reuse the fixed sixteen-context stable-tag panel without choosing inputs based
on results. Construct two disjoint sets of arbitrary tags, called A and B, before
any new model output. Both sets have 48 unique tags per context. Test four versions:

| Input tags | Forced answer tags | Do the tags match? |
|---|---|---|
| A | A | Yes |
| A | B | No |
| B | A | No |
| B | B | Yes |

Keep the text, record order, label choices, answer schema shape, sampling settings,
and display-order instruction fixed. Each tag set appears equally often on each
side, so an effect of a particular set's spelling or length is not automatically
an effect of matching. Keep both sets disjoint from public record identifiers.
Cross the four versions with the existing three public-identifier conditions:
16 contexts × 4 versions × 3 conditions = 192 new calls. Do not reuse historical
matching calls as half of this balanced experiment.

Important design issue: the prompt must unambiguously ask for labels in display
order and say that supplied answer tags are bookkeeping, not instructions to
answer another record. Otherwise a mismatched tag may create contradictory
directions, and “wrong by position” may actually be correct by key. Freeze the
exact prompt and both intended-position and named-record diagnostic scorers
before launch. The four-arm comparison should be rejected or redesigned if a
careful reader cannot say which answer the task requests.

## What to measure and how to decide

Primary: within-context difference between the mean later-label accuracy of the
two matching versions and the two nonmatching versions. Show each of the four
conditions too. Use contexts, not the repeated labels, as paired units. Report
observed wrong answers separately from missing or unauthenticated responses.
Count prompt and answer tokens, wall time, and contract failures for each version.

If matching wins consistently, this supports an additional benefit of shared
tag values beyond these particular input/output formats. If nonmatching tags
work about as well, revise the explanation toward structured record separation;
do not call that a failed practical method. If results depend on which tag set
is used, investigate token/string sensitivity before claiming a general rule.
None of these outcomes identifies an internal attention mechanism by itself.

Use a fixed final 192-call inventory, a predeclared seed, an 1800-second inclusive
cap, and per-call immutable request/response receipts. No model-weight checkpoint
is needed because this is inference-only. Exact inputs and final promotion
criteria are not yet frozen: this document is an idea, not READY authorization.

## Connection to prior work

Indexed input/output batching is already in
[Cheng, Kasai, and Yu's Batch Prompting](https://aclanthology.org/2023.emnlp-industry.74/).
The proposed contribution is a discriminating test of what makes the interface
helpful, not the invention of tagging records.

[Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning](https://arxiv.org/abs/2305.13971)
shows the usefulness of input-dependent output grammars. Our interpretation
must therefore treat the grammar as part of the intervention, not mere parsing.
This paper was revisited in a targeted primary-source search on September 10;
the proposed four-way test is our inference from current results, not a reported
result of that paper.

## Evidence to keep connected

Completed source: `analyses/leaf-mnli-stable-anchor-vs-sequence-counting-live-2026-09-10/`.
FINAL_SEAL SHA256: `f3923f17e472b4ca1051e2448c7175de21f844832c5a822a323b980730c99430`.
This idea should not delay the already prepared whole-task and cross-model tests.
