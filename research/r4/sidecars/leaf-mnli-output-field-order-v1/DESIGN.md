---
id: mnli-output-field-order
status: exploratory_preparation
question: Does emitting a label before its requested identifier reduce misleading-reference interference?
created_utc: 2026-09-10T16:50:00Z
parent_question: visible-reference-interference
---

# Answer first, identifier second

The completed wording control left an approximately42-percentage-point penalty
when an output identifier also named another visible record. One possible
mechanism is that writing that identifier immediately before the label primes
the wrong record. We will swap the order of the two output fields.

Reuse the exact eight contexts from the wording control, explicitly exposed
to this research. Do not select contexts by individual outcomes. Run all
three visible-reference conditions (misleading, unrelated, aligned) under
both output orders (tag then label; label then tag), all with explicit
same-record instructions. This is48 fresh calls, not reuse of historical
baseline responses. The input objects, texts, order, requested tags and label
definitions are unchanged. Only the natural instruction naming field order
and the output grammar's property/required order change within each pair.

Fixed released Qwen3-4B Instruct2507, no adapter, no tools or thinking, native
template, temperature0.5/top_p1, max3072 generated tokens, context8192,
four workers,90-second per-call cap. Seed982626101+context index, one paired
seed per context. Rotate six-arm dispatch ordering by context. Prefix cache
disabled. Checkpoint every actual request/response/result; retain all48
slots, transport failures as NULL and authenticated malformed answers as0.
No retries, output repair, reordered parsing, or context/seed replacement.
One1440-second parent envelope includes1320work/180startup and90release.

Primary: the label-first improvement in the misleading arm minus the
label-first improvement in the aligned arm, using eight context-level
differences. Positive values mean a selectively reduced penalty. Also report
each arm's strict correctness, exact contract availability and all paired
context differences. Unrelated-reference interaction and wrong-record versus
displayed-record predictions are diagnostics. Practical follow-up signal:
at least10percentage-point reduction of the misleading-versus-aligned gap,
positive in at least6/8 contexts, without lower availability. This is a
pilot prioritization rule, not a significance or publication threshold.

A positive result motivates a fresh-context replication and an answer-only
output plus host-side identifier join. A near-zero result shifts priority
toward removing redundant visible identifiers or changing the input layout.
Any effect remains a formatting/instruction package, not proof of attention
or decoding causality. Previous output tags from earlier array items remain
visible even in the label-first condition.

MAIN prepares and reviews this sidecar locally because subagent calls hit
usage limits. Existing frozen source, data, failures and reports stay intact.
