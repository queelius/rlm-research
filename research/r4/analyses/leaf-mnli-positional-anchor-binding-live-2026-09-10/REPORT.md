---
title: Positional-anchor MNLI96 independent audit
status: complete_raw_native_audit
date: 2026-09-10
study: leaf-mnli-positional-anchor-binding-v1
attempt: 002
planned_endpoints: 96
available_endpoints: 96
---

# Positional-anchor MNLI96 audit

## Result

The frozen output-only promotion criterion did not pass. With no row field in
the input, row-first output improved late-position (17–48) correctness by only
**16/768 labels, +2.08 percentage points**. Context differences were
`+14,+5,+1,+1,-4,-6,-2,+7`: five of eight were positive, below the required
six, and the effect was below the required 10 points. Availability was 24/24
calls for each output form, so missingness does not explain the result.

The full factorial reveals a much stronger package interaction. With explicit
row fields also present on every input record, row-first output improved late
accuracy from **292/768 to 620/768**, or **+42.71 points**. Across all 48
positions it improved from 590/1,152 to 933/1,152 (+29.77 points). By contrast,
adding input rows to labels-only output changed total correctness by just
7/1,152 (+0.61 points), and row-first output without input rows changed total
correctness by -11/1,152 (-0.95 points). The input-row by output-row interaction
is therefore +354/1,152 overall and +312/768 late.

This supports a matched input/output positional-address follow-up. It does not
support an output-only row token as specified by the original gate. Because
the manipulation bundles prompt wording, input fields, output schema, and
generated row tokens—and a row token can steer the following label—it is not a
pure attention or isolated binding mechanism result.

## Reference conditions and position

The matched input/output package was large in every reference condition:

| Visible reference | Labels-only present-row | Row-first present-row | Gain |
| --- | ---: | ---: | ---: |
| Wrong visible record | 194/384 | 313/384 | +31.0 points |
| Unrelated alien ID | 201/384 | 313/384 | +29.2 points |
| Aligned ID | 195/384 | 307/384 | +29.2 points |

Most of the gain is late: +115, +104, and +109 correct late labels out of 256
for wrong, alien, and aligned references. Early gains were only +4, +8, and +3
out of 128. This pattern is consistent with positional markers helping retain
place deeper in a long array, but it does not establish why.

Without input rows, row-first output effects were heterogeneous: wrong +7,
alien -3, and aligned +12 late labels out of 256. The wrong-versus-aligned late
interaction was -1.95 points without input rows and +2.34 points with them.
Thus this pilot does not show that ordinal markers specifically eliminate the
penalty from a misleading visible-record referent.

## Native validity and cost

All 96 planned endpoints have a request, HTTP 200 response, unique
choice-bearing native completion, authenticated final, and exact whole-contract
output. All finished by `stop`; there are zero NULLs, malformed outputs,
wrong-row contracts, or length caps. Recorded request bytes, prompt token IDs,
model identity, response JSON, completion token/logprob rendering, usage, and
the frozen scorer all reconcile exactly.

The physical union contains 96 requests and 96 completions. Known usage is
378,192 input tokens, 32,233 output tokens, and zero cached tokens, with no
unknown usage fields. Provider billing was not measured. The attempt-002 owner
completed in 239.262 seconds with clean release and no active service or error;
the parent exited 0 after 241.881 seconds with an empty GPU process inventory.

## Method and limitations

The original method was frozen after attempt 001 launched but before its
terminal content or outcomes were read; attempt 001 made no scientific calls.
The additive attempt-002 binding was written post-terminal after MAIN disclosed
96/96 availability, without changing metrics. The reviewer authored the study
implementation, so this is reproducible and raw-native but not author-
independent.

The eight source contexts and late-position split are research-exposed, each
context supplies one paired seed, and labels and arms within a context are
dependent. The result is exploratory. A direct follow-up should retain the
matched row fields while separating instruction wording or generated-token
effects, preferably on newly frozen contexts; simply repeating an output-only
row field is not promoted by this gate.
