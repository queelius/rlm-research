# Broader training often gets closer, but the remaining failures differ

September 9, 2026. This is an explicitly post-hoc diagnostic of the completed
broader campaign, not a replacement for its prespecified exact-answer result.
The [primary audit](../root-broad-equality-continuation-live-2026-09-09/REPORT.md)
remains13/48→16/48, with the64-record composition comparison flat at5/24.

## A secondary signal worth testing prospectively

Among the24 paired cases where **both** models returned a parseable numeric final
answer, average absolute count error fell from4.625 to0.875. Nine pairs got closer,
thirteen had the same error and two got farther away. These24 cases were selected
by the two observed response formats; they are not a random subset or a causal
effect estimate for all48 cases. Cases and targets also share context groups.

Across all48 planned cases per model,20 original and33 final responses contained
a count within one of the correct value. This secondary count includes exact
answers, retains the full planned denominator and requires a numeric terminal;
it does not relabel a wrong answer as correct. Numeric coverage itself changed
from31/48 to38/48. In particular, the two numeric final responses among the four
256-record cases were each off by one; the other two had no parseable numeric
terminal. Exact accuracy there remains0/4.

| Prespecified stratum | Both-numeric pairs / all pairs | Mean absolute error, original→final, on those pairs |
|---|---:|---:|
| Composition64, trained targets | 4/12 | 8.00→2.75 |
| Composition64, reserved targets | 6/12 | 1.33→0.83 |
| Leaf-test-exposed32 | 9/12 | 0.44→0.22 |
| Length128 | 3/8 | 10.67→0.33 |
| Length256 | 2/4 | 17.50→1.00 |

This suggests that “no broad exact-answer improvement” and “no useful change at
all” are different conclusions. It does not establish correct item labels,
proper coverage or general adaptive planning. Error cancellation can make a count
close or correct even if multiple item labels are wrong. We should retain this
signal and preregister numeric distance alongside exact accuracy in a future
comparison, not retrospectively promote it to the primary outcome.

## Four illustrative paired traces

Selection was outcome-informed: smallest pair_id within one256-record case, one
128-record gain, one trained-target composition loss and one composition gain.
[SELECTION.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SELECTION.json") records all exact IDs, paths and source hashes.
The four selected pairs are not a prevalence sample. Main read their root actions
and observed tool returns statically; none of their Python was executed on the host.

| Case | What the saved actions and observations show | Interpretation limit |
|---|---|---|
| Composition64 gain, human category, gold10 | Original asks one child to classify all64 records, receives a JSON parsing error, then catches another parsing error and substitutes empty labels, producing0. Final uses batches of4, decodes the results and reports the observed count10. | This is consistent with avoiding an output-format/batch-size failure. One trace does not identify a causal fraction of training gains. |
| Composition64 regression, numeric category, gold10 | Original uses batches of5 and reports observed10. Final samples484 tokens of a tool-call-shaped response with invalid outer JSON; no structured tool is invoked and the parsed final answer is empty. | Empty parsed output does not mean the model generated nothing. This is still a sampled policy-format failure, not a failed HTTP request or an output-budget exhaustion. |
| Length128 gain, human category, gold36 | Original samples498 tokens but ends an invalid/unfinished tool request and produces no usable final answer. Final first makes two Python syntax errors, then repairs the program, uses batches of4 and reports observed36. | The success includes recovery, not perfect first-try code. It does not show that the repaired program's individual labels were all correct. |
| Length256 failure, human category, gold59 | Original first fails to decode a large batch, then uses batches of10 and reports observed60. Final uses batches of5, checks that256 labels were collected and also reports observed60. | The final program runs and its length assertion passes, but count correctness does not. This does not prove exactly one item was mislabeled, only that the aggregate differs by one. |

Relevant native request IDs include final composition-loss
4ad786f73da146528ebb90952e96f49b and original128-gain
69ebda2afe79491a9154a810abdc5a20. Their physical source SHA256 values are
69e8d3a7e719ff4c3a28de7141dc2fa92682a6a6d4cb26bf3b32f7c96cc9bbf2 and
96ca4fee8bb748dd0a503b42af106477cb0971191a423875835212ba5c4d80c0.
Both returned HTTP200 with normal provider stop, not length termination.
Strict JSON decoding of their sampled tool blocks reports a missing delimiter;
no response repair or re-execution was performed. The remaining selected root
message indices and exact raw paths are recoverable from SELECTION.

## What this changes next

Separate three questions: can the root produce an executable request; can the
helper return a usable result; and can the complete computation yield the exact
answer? The examples support keeping all three measurements rather than making
one generic “reasoning failure” label.

The active helper/interface sequence tests the second boundary. If reliable
helper returns expose consistent near-misses, investigate semantic errors and
targeted rechecking before assuming more root updates solve them. A graded
count-distance training reward is only a possible future comparison: it could
encourage guessing common counts, so it requires content-sensitive controls and
must not silently replace the current exact-answer objective.

## Reproducible scope and analysis correction

[COUNT_SCREEN.json](../../../../ARTIFACTS.md#unpublished-files "Not published: COUNT_SCREEN.json"), SHA256
1b561315c7f0fa0a310ac82f0cab2df208755c0afd64bec2027720dd403a8b3f,
contains all96 rows,48 paired error differences, per-stratum coverage and106
source hashes. Four focused tests pass; the successful scan took0.17CPU seconds.
It authenticates the existing seals and raw episode hashes but does not rerun
native graph/optimizer admission or claim an independent full campaign audit.

The first diagnostic incorrectly assumed the entire response was one Answer
line. A comparison with the frozen primary caught a valid explanatory response
whose last line was Answer: 0. The failed source is preserved; an added regression
failed before the numeric parser was corrected to match the actual inherited
final-nonblank-line contract. [COUNT_PARSER_AMENDMENT.md](COUNT_PARSER_AMENDMENT.md)
documents this analysis-only change. Original scientific scores are unchanged.

An independent [prefill correction](../root-first-action-screen-2026-09-09/PREFILL_CORRECTION.md)
also clarifies earlier prose: tool-call openers were sampled, not supplied. The
task provided instructions and a worked example. Valid-serialization gains remain
real, but both historical models already attempted a tool-shaped first response.
