---
status: prospective_frozen_before_outcomes
date: 2026-09-11
study: leaf-mnli-balanced-tag-match-v2
run: outputs/attempt-001
planned_endpoints: 192
contexts: 16
relations: 3
cells: 4
---

# Prospective independent balanced-tag-match audit

Do not inspect the output tree until MAIN supplies the exact `OWNER_TERMINAL.json` and parent
`EXIT.json`. Before reading scientific outcomes, require the exact hashes, owner complete and
released with no error or active service, parent exit zero without timeout, empty post-exit GPU
inventory, and an EXIT completion marker equal to the owner-terminal hash. Process completion does
not imply that all endpoints are observed.

This method binds only corrected V2, READY SHA-256
`0cca08fb3289774e28bb01f91a59a088320b55afa98f5f363bb2ec9f091129c9`, identity
`c1fc3dd78c072a0c67d2b2dc1d215c993bd3054b6e6e95e4b8bbb0a02b1cacc7`. V1 was never launched.
MAIN found before outcomes that V1 omitted `requested_tag`, making its three relation conditions
inert. V2 restores the rotated public `requested_tag`, corrects the named-record diagnostic, and
rotates cell order. It does not change the 16 contexts, seeds, four tag cells, primary estimand, or
192-call inventory.

The fixed design is 16 contexts × three visible-ID relations (`wrong`, `alien`, `aligned`) × four
tag-set cells (`AA`, `AB`, `BA`, `BB`). AA and BB use the same opaque tag set at input and output;
AB and BA use disjoint sets. All cells retain displayed record order, the same semantic task, one
paired seed per context, and grammar-forced output tags. Independently rerender all 192 frozen
bodies and require every displayed row to include `requested_tag`, all matched/mismatched tag-set
relations to hold, and three distinct visible-ID sequences per context.

For every planned endpoint, authenticate the exact coordinate and serialized request, expected
native prompt-token IDs, Qwen3-4B-Instruct-2507 base-model alias and revision, one unique response,
native completion token/text identity, finish branch, and usage. Reparse the exact 48-object
`answer_tag`/`label` contract. A returned authenticated malformed, incomplete, wrong-route, or
wrong-tag response is an observed invalid zero. An undispatched, unreturned, non-200, or
unauthenticated endpoint is NULL. Never repair, retry, or recover labels from prose.

The primary outcome is late-position accuracy (positions 17–48): mean(AA, BB) minus mean(AB, BA),
pooled over relations with context as the paired unit. Report complete-context effects and all 16
context coordinates, but apply the promotion rule to the planned-denominator lower bound: at least
10 percentage points, positive fully observed effects in at least 12/16 contexts, and at least
15/16 available calls in every relation-by-cell. Missing-outcome ranges are identification bounds,
not confidence intervals; a favorable complete-case estimate cannot override an unfavorable lower
bound.

Also report all 12 relation-by-cell tables, early and total accuracy, contract validity, and the
three relation-specific matched-minus-mismatched diagnostics. For non-alien relations, construct a
map from each actually displayed `id` to that displayed record's gold label, then look up each
row's `requested_tag`. This yields the visible-named-record diagnostic in the correct direction:
aligned equals the intended displayed record, wrong points to the rotated target, and alien has no
named score. This is secondary and cannot replace intended-position accuracy.

Count the union of all request, response, and result directories, including unexpected directories.
Report physical attempts, returned responses, native-authenticated finals, available and invalid
answers, NULLs, unique provider IDs, and known/unknown input, output, and cached-token usage.
Provider billing is not inferred.

The intervention is a representational package. Structured decoding supplies every answer tag and
fixes output order; tag fidelity is not evidence of freely learned copying. A matched-tag effect
could reflect repeated strings, prompt regularity, attention, or another use of shared tokens. The
16 contexts are research-exposed and clustered; 48 labels and 12 calls within a context are not
independent. No internal mechanism, new-corpus replication, or end-to-end root benefit is claimed.

The auditor did not author V1 or V2. The auditor did prepare this method and reader after MAIN
identified V1's pre-output defect and after V2 was sealed, but before any V2 model outcomes.
