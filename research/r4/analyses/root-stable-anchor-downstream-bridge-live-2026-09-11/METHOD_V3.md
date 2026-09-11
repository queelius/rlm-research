---
date: 2026-09-11
status: prospective_outcome_unread
producer_ready_sha256: 18505cc54f140ee8f2e5653dfe6f07b203951c6884d9bd19c36db6644321a9aa
producer_identity: 10d9b734f229d9f250678d1348be3f9b6e8c0720c654b703624d4984f5803b8d
planned_leaf_calls: 24
planned_root_episodes: 96
clustered_units: 8
---

# Prospective V3 audit method

This method supersedes only the 16-leaf/64-root counts in the preserved producer `METHOD.md`.
The producer V3 adds `labels_only`, uses the released base model for all leaf arms, and retains the
same exact eight-context panel. No output directory existed when this method was frozen.

## Admission and native evidence

Read outcomes only after MAIN relays the exact SHA-256 of `OWNER_TERMINAL.json` and parent `EXIT.json`
and authenticates release (no active service/GPU PIDs). Analyze a bounded failed terminal too, but
call it failure-diagnostic rather than a completed scientific run. Preserve all 24 planned leaf and
96 planned root cells; authenticated malformed responses are observed-invalid strict zero, whereas
unattempted or unauthenticated endpoints are NULL with unknown score.

For every leaf call, require the frozen `REQUEST.json` to precede the HTTP receipt; recompute its
body hash; match the exact request body and prompt IDs in `inputs-v3`; require raw response model to
equal the released base path and raw `prompt_token_ids` to equal the frozen IDs. Authenticate the
single assistant branch, completion IDs, decoded content, finish reason, log-probability alignment, and
usage. Reparse labels-only positionally and keyed arms by their exact grammar. Never use producer
scores as evidence. Preserve the full raw response pin.

For roots, authenticate the QS6 alias, initial prompt IDs, every physical root request/response,
tool branch, graph parentage, final branch, usage, and service descriptor/binding. A written helper
log is not itself semantic use. Physical cost is the union of 24 leaf acquisitions plus every root
turn exactly once; each leaf map is shared by four root episodes and is not charged four times.
Report input/output/cached/uncached known totals, unknown fields, elapsed owner/parent/service phases,
and billing/FLOPs as unknown unless actually measured.

## Stage-separated scoring

For each context and encoding report leaf whole-contract validity, all-48 and late-16 label accuracy,
and canonical public-map completeness. For each root report `classify_all()` invocation, full map
delivery, map retention in actual state, query-relevant IDs read, actual scalar-producing operation,
host reduction over the delivered predicted map, strict `Answer: N`, final agreement with the last
observed scalar, gold correctness, and correct AND faithfully performed.

Manually inspect actual root programs and their parent/tool observations. Do not execute sampled
programs. Mark the requested operator, relation, user scope, and weight/count semantics separately.
A correct constant guess, direct answer without the required supplied-plan computation, map read
without query-relevant consumption, or computation over a different map is not faithful. Diagnose
program behavior from the trace and trusted frozen host reducer only; this is not fresh human review
of MNLI labels.

## Frozen contrasts and clustered bounds

Keep count and weight, supplied and free, separate. The two correspondence contrasts answer
different questions and must both be shown:

1. `opaque - labels_only`: whether the winning correspondence package improves the leaf and survives
   to host predicted-map exactness and correct-and-performed root success.
2. `opaque - sequential_numeric`: whether opaque stable keys add anything beyond an already strong
   ordinary keyed interface.

Also report `sequential_numeric - labels_only`, supplied-minus-free within each encoding, and the
plan-by-encoding interactions. For each endpoint contrast provide the 16 paired context-question
differences, then eight context-cluster net effects; do not call 96 episodes independent. Missing
left/right cells contribute the worst/best paired difference `[-1,+1]`; known pairs contribute their
observed `right-left` difference. Sum bounds over the fixed denominator and report availability by
arm before any complete-case view.

The pre-output V3 estimand amendment transfers the already-written numerical gates, without changing
their values, to the primary `opaque - labels_only` comparison: leaf accuracy gain at least 10
percentage points, positive in at least 6/8 contexts and no validity/availability disadvantage;
predicted-map exact-answer gain at least 3/16, represented in both operators with at most one loss;
supplied-root correct-and-performed gain at least 3/16, positive net effect in at least 5/8 context
clusters and no availability disadvantage; and free-root gain at least 3/16 with a positive lower
NULL bound. `opaque - sequential_numeric` is secondary equivalence/descriptive evidence and has no
promotion gate. This changes the contrast receiving the gates, not their numeric thresholds or any
fixed input.

## Operational scheduling checks after LR

- Use only `READY_V3.json` SHA `18505cc5…`; V1 and the failed owner-import V2 are preserved but must
  not be launched. The command is `owner_v2.py run --output outputs/attempt-002`.
- Confirm `outputs/attempt-002` is absent immediately before launch. No retry namespace is implied.
- Confirm `runtime-v2/inputs` resolves exactly to `inputs-v3`; the reused root collector reads that
  proxy path even though the owner and source live one directory above.
- `/v1/models` must expose the exact released base path as well as the two adapter aliases. The leaf
  request must name the base path, never the c32 alias. Stop before science if it is absent.
- Keep startup, all 120 minimum calls, and release within 2,400/2,370/2,250 seconds. The 96 root
  episodes may entail multiple physical turns, so “120” is a minimum model-call count, not total
  physical cost.
- A leaf invalid/NULL stops roots under the current collector; retain that bounded attempt and do not
  silently fall back. Verify request receipts exist before any leaf HTTP response.

No GPU, service, request, or outcome was used to prepare this audit method.
