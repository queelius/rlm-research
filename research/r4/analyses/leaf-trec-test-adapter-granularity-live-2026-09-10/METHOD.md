---
status: prospective_independent_audit_method
date: 2026-09-10
study: leaf-trec-test-adapter-granularity-v1
planned_calls: 148
planned_source_rows_per_condition: 500
outcomes_read: false
---

# Official TREC-test base/c32 audit method

This method was frozen after MAIN accepted the study but before its GPU launch
or any science output. The analyst authored the evaluated sidecar, so source and
analysis overlap is explicit; MAIN independently reviewed the source and reran
its ten focused tests. No rollout output is read until MAIN relays terminal,
release, and exact parent EXIT evidence.

## Admission and scoring

Require the frozen READY identity and every source/input pin. After execution,
require `OWNER_TERMINAL.json`, clean release, no active service, and the exact
parent EXIT completion-marker hash; record nonzero exit or incomplete owner
honestly rather than requiring success to inspect retained outputs.

For every one of the 148 planned coordinates, join the frozen coordinate and
request body to actual REQUEST/RESPONSE/RESULT and native evidence. Require the
exact model dispatch: the pinned full base model for `base`, and the bound
checkpoint-0128 c32 adapter for `c32`; verify raw model equals body model,
exactly one choice, native completion-token/logprob lengths and finite values,
prompt/completion usage, request ID, finish branch, and renderer parse. A
verified native final is observed. A completed malformed, extra, duplicate,
noncanonical, or incomplete ID map is an observed policy failure: zero correct
for every requested record, with the invalid reason retained. A missing request,
non-200 response, missing/unverified native final, identity inconsistency, or
unverifiable tool route is NULL for every record in that call. Do not repair,
reorder, extract partial labels, retry, or replace a coordinate.

Reconstruct each model × width × seed condition over all 500 official source
IDs. Preserve the final four-record S16 chunk. Report planned-denominator
correct counts with NULL bounds and separately conditional observed-record
accuracy, exact-map availability, invalid calls, and call-correlated missingness.

## Comparisons

Primary comparisons are c32 minus base at W100 and S16, for each paired seed and
combined descriptively. Report the difference between those two adapter effects
as the width interaction. Pairing is by source ID and seed; do not treat 500
labels within a contextual batch as independent trials. Report wins/losses/ties
only among jointly observed record pairs, alongside operational planned counts
and missing-data bounds.

Stratify by the six coarse TREC classes. Also report the 11 normalized groups
that overlap the raw TREC train source separately from the 489 previously
research-evaluated groups. The 11 were excluded from c32 optimizer training and
the earlier selected-test evaluation; the 489 are research-exposed. Recompute
zero overlap against `trec-leaf-sft-v1/prepared-v1/data.json` actual `train`
group IDs rather than trusting only the proposed split receipt. Preserve all
500 official source lines; no deduplication or outcome selection.

## Native cost and interpretation

Audit the disk union of all prepared requests, responses, results, and provider
request IDs, including failed/orphan records. Report HTTP status, known and
unknown input/output/cache usage fields separately, owner and parent elapsed
time, release, and GPU-empty evidence. These are physical local-model costs,
not provider billing.

This study asks whether child classification accuracy transfers outside the
5,065-group optimizer corpus and whether contextual batch width modifies that
gain. It contains no root call, tool execution, aggregation target, or
end-to-end RLM measurement. The official test panel is partly research-exposed,
two seeds do not make records independent, near-duplicate dependence is not
excluded, and width changes call count and prompt/output length. The practical
five-point promotion threshold in DESIGN is a decision rule, not an equivalence
or significance test.
