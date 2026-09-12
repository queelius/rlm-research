---
title: Budgeted evidence screen interpretation correction
date: 2026-09-12
status: authoritative_additive_interpretation_no_gpu_admission
supersedes: DECISION_ADDENDUM.md next-experiment ranking
---

# Treat this first as an interface cold-start failure

There are 48 episode records, not 48 valid endpoints: only 11 contain a strict
`Answer:N` (6 eager, 5 budgeted), and only 9 are consistent with accepted finish
state (5 eager, 4 budgeted). Raw grading recovers 4/6 eager and 3/5 budgeted exact
finals, while 21/24 paired outcomes are unknown. The inherited exporter remains
all-unavailable because its frozen initial-prefix check correctly rejects the new
prompt condition; that reporting failure is retained separately and does not
justify a GPU rerun.

The root checkpoint was trained for the older `await rlm(...)` interaction, not
the new synchronous `classify(...)` / `finish(...)` interface. Both new arms show
roughly the same rejection burden (21 eager, 22 budgeted), and most episodes never
produce a strict final. A zero-shot interface swap therefore cannot distinguish a
bad evidence-selection policy from failure to use the action protocol. Architecture
promotion is not supported.

Budgeted callback access is logically smaller (28 saved labels versus 80), but this
is not physical helper compute: both arms make zero child-model calls. Budgeted is
also more expensive in observed root compute: 285,006 input and 46,839 output tokens
versus 196,835 and 38,824, with two budgeted coordinates carrying unknown usage.
One budgeted exact finish uses 12 labels rather than 16, but a single success amid
21 unknown pairs is not evidence of learned selective stopping.

## Cheapest next comparison, if this direction is revisited

Before adding a persistent ledger, compare the unchanged zero-shot budgeted prompt
against the same interface with one generic syntax-only usage example. The example
may show calling `classify([id])`, reading the returned dictionary, calling
`finish(integer, evidence_ids)`, and separately returning `Answer: N`; it must use
fictitious identifiers and must not supply a task operator, subset, real label,
gold answer, or stopping rule. Use fresh paired seeds and the same 24 train-context
tasks, weights, action limits, and generation cap. Charge extra example tokens.

The primary decision is protocol competence: more finish-consistent strict finals
and fewer rejected API actions without more wrong finals. Accuracy and evidence
counts are secondary while most pairs are ungradeable. If a syntax example does
not materially improve completion, retire zero-shot prompt adaptation and consider
a few explicitly train-only interface demonstrations or controller adaptation.
Only if protocol use becomes reliable but duplicate/pending-state errors remain
should the neutral cumulative ledger be tested. This ranking adds less architecture
than the ledger and directly targets the checkpoint/interface mismatch observed here.

