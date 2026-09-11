# What changed in the first request after root training?

Completed posthoc screen, September 9, 2026. This supplements, rather than rewrites,
the [sealed root-training result](../root-continuation-live-2026-09-09/REPORT.md).
It examines the same 48 evaluation episodes. It is not another training run or
an independent replication.

## The clearest observation is better request formatting

The runtime could use 13/24 first tool requests from the original root and 22/24
from the trained root. Decoding the actual recorded response tokens explains the
difference: every closed, valid JSON tool-call object became a structured tool
call, while malformed or unfinished objects did not.

| First-response observation | Original root | Trained root |
|---|---:|---:|
| Valid JSON tool request, accepted as one structured call | 13/24 | 22/24 |
| Closed tool-call block containing invalid JSON | 10/24 | 1/24 |
| Unfinished tool-call block | 1/24 | 1/24 |

The ten original invalid objects comprise two invalid backslash escapes and eight
delimiter errors. The trained root has one delimiter error. All closed malformed
objects ended with a normal provider stop; only the unfinished block in each arm
hit the 2,048-token limit. Thus these failures were mostly not a shortage of output
tokens, and the empty structured messages did not mean the model generated nothing.
For example, one original response incorrectly escaped an apostrophe inside JSON.
Strict JSON decoding rejected it, as it should. No response repair was attempted.

The first-action tool prefix was already supplied by the shared native setup.
Consequently this does **not** show that training taught the model to freely choose
to use Python. It shows that its first generated request more often satisfied the
existing interface.

## Formatting is part of the story, not the whole explanation

Of the 13 paired final-answer gains, eight occurred where the original first request
was unusable and the trained request was usable. Five gains and both losses occurred
where both first requests were usable.

| Paired first-request status | Cases | Original final answers correct | Trained final answers correct |
|---|---:|---:|---:|
| Both usable | 12 | 5 | 8 |
| Original unusable, trained usable | 10 | 0 | 8 |
| Original usable, trained unusable | 1 | 0 | 0 |
| Neither usable | 1 | 0 | 0 |

These are descriptive subgroups defined after seeing both responses. They do not
estimate how much of the training effect was caused by JSON correctness. We did
not repair an original response and replay it, nor hold its program fixed while
changing only serialization.

The code text also became more consistent with small batches: a literal
`batch_size = 5` appears in five original first requests and eighteen trained
requests. The trained arm additionally has two literal size-four assignments and
one size-fifty assignment. Other implementations are not recognized by this narrow
text check. A `json.loads(...)` call appears in all thirteen usable original first
requests and twenty of the twenty-two trained ones. These are lexical observations,
not an audit of executed batch sizes, item coverage or correct aggregation.

In particular, this does not establish that reward training fixed the
[separate string/list misuse example](../root-consumption-example-2026-09-09/REPORT.md).
The clearer-return-type experiment is a prospective interface test, not a repair
of a demonstrated universal failure in this transfer comparison.

## The saved wire responses also recover missing cache accounting

The higher-level native usage objects omit cache counts on all 553 successful
calls. Their saved provider responses nevertheless contain cache counts on all
553. The input and completion totals reconcile exactly with the native objects
and exported role evidence.

| Transfer accounting | Original | Trained |
|---|---:|---:|
| Successful model calls | 152 | 401 |
| Logical input tokens | 214,103 | 366,845 |
| Provider-reported cached input tokens | 190,384 | 341,856 |
| Input tokens minus reported cached tokens | 23,719 | 24,989 |
| Completion tokens | 49,457 | 28,964 |

This refines the earlier report's missing-cache qualification: cache counts are
missing from the adapter-level metrics, but recoverable from the preserved wire
responses. The subtraction is an accounting remainder, not measured physical GPU
work. Original-first service order, concurrency and cache state were not controlled.
Do not turn the shorter trained-arm wall time into a hardware-efficiency claim.

## Evidence and limits

[SCREEN.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SCREEN.json") contains all 48 first-action rows, 553 per-call usage
rows and 559 source hashes. The script verifies the referenced role-audit hashes,
uses the local pinned tokenizer, and compares raw-wire input/output counts with
both native usage and exported turn usage. All 48 syntax classifications agree
with the observed presence or absence of a structured first tool call. Three
focused tests cover valid input, an invalid escape, and incomplete/ambiguous blocks.

See [the method and prior exposure disclosure](METHOD.md), [analysis script](../../../../ARTIFACTS.md#unpublished-files "Not published: screen.py")
and [tests](../../../../ARTIFACTS.md#unpublished-files "Not published: test_screen.py"). No generated code was executed, no model was called,
and no runtime, training checkpoint or original experiment artifact was changed.
The original comparison's six context groups and other limitations still apply.

Next question: does training improve execution beyond making requests valid?
An interface intervention and a fresh-seed comparison can help, but isolating a
particular mechanism would require an additional controlled comparison.
