---
id: mnli-output-field-order48
status: completed_exploratory
question: Does label-first output selectively reduce misleading-reference interference?
evidence: AUDIT.json
contexts: 8
planned_calls: 48
available_calls: 48
claim_level: exposed_context_pilot_signal_requires_fresh_context_replication
---

# Label-first passed the pilot gate on these eight exposed contexts

Writing the label before its output tag improved the misleading-reference arm
from 152/384 (39.6%) to 182/384 (47.4%), a gain of 30 labels or 7.81 percentage
points. The aligned arm moved from 317/384 (82.6%) to 302/384 (78.6%), a loss of
15 labels or 3.91 points. The prespecified difference in differences was therefore
+45/384, or +11.72 percentage points.

The interaction was positive in 6/8 contexts, negative in 2/8, and tied in none.
Every arm had 8/8 available, contract-valid responses. Thus the predeclared pilot
rule passed: at least a 10-point selective reduction, positive in at least six
contexts, without lower availability. This is a prioritization signal for a
fresh-context replication, not a significance threshold or population claim.

| Visible reference | Tag first | Label first | Label-first change |
| --- | ---: | ---: | ---: |
| Names another record | 152/384 (39.6%) | 182/384 (47.4%) | +30 (+7.81 pp) |
| Unrelated identifier | 309/384 (80.5%) | 296/384 (77.1%) | -13 (-3.39 pp) |
| Aligned identifier | 317/384 (82.6%) | 302/384 (78.6%) | -15 (-3.91 pp) |

The misleading-versus-aligned penalty shrank from 165/384 (42.97 points) with
tag-first to 120/384 (31.25 points) with label-first. Against the unrelated arm,
the corresponding order interaction was +43/384 (+11.20 points).

## Eight paired context effects

Changes below are label-first minus tag-first, in labels out of 48. The primary
column subtracts the aligned change from the misleading change. `AUDIT.json`
retains all nine prespecified simple and interaction contrasts, exact bounds, and
the normalized values for every context.

| Context | Genre | Misleading | Unrelated | Aligned | Primary DID |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0 | government | +1 | +3 | +2 | -1 |
| 1 | government | -3 | -1 | 0 | -3 |
| 2 | slate | +1 | -3 | -2 | +3 |
| 3 | slate | +11 | +1 | -2 | +13 |
| 4 | telephone | +13 | -3 | -4 | +17 |
| 5 | telephone | +3 | -4 | -4 | +7 |
| 6 | travel | -1 | -2 | -3 | +2 |
| 7 | travel | +5 | -4 | -2 | +7 |

On the 258 positions where the displayed record and the record named by its
required tag had different gold labels, tag-first produced the named record's
label 174 times, the displayed record's label 46 times, and the third label 38
times. Label-first shifted that partition to 126 named, 96 displayed, and 36
third-label outputs. This is a conditional diagnostic consistent with reduced
wrong-record capture; it is not independent-item evidence or causal proof.

## Native admission, availability, and cost

An independent parser authenticated the actual request wire and saved native
prompt IDs, decoded native completion IDs, exact model alias, usage identities,
HTTP response, service configuration, and complete output grammar before scoring.
All 48 calls were physical, returned HTTP choice payloads, ended with `stop`, and
passed native and whole-contract checks. There were no NULL endpoints, length
caps, unexpected call directories, or disagreements with the producer's reported
core score fields. The 177 producer-side files were pinned in `OUTCOME_PINS.json`.

Known usage was 183,516 input tokens and 46,047 output tokens, with zero cached
tokens and no unknown usage fields. Provider billing and active GPU seconds were
not measured. Owner wall time was 305.125 seconds and outer-parent wall time was
307.735 seconds; neither is an optimizer-time or active-GPU-time measurement. No
training occurred.

The exact terminal records were checked before outcomes: owner SHA-256
`e8103c0ea28f964fd1111acd49d7a4448c62d20ee0bb24645262dea1bcf759af`
was complete and released, and parent EXIT SHA-256
`c45482318fce12e82ee37218ee48b62ca05a524d52d3d89d0cf58d172ffcf781`
reported exit 0, no timeout, no remaining GPU PIDs, and the matching owner marker.
The service release separately proved all captured process identities exited and
ports were free.

## Parser correction and limitations

The earlier generic reader assumed every object was tag-first. This audit's
format-aware scorer instead derives the contract from each arm: tag-first objects
must preserve `tag,label`; label-first objects must preserve `label,tag`; and the
same parser also handles a labels-only array as 48 positional label strings with
no invented tag or field-order evidence. Focused red/green tests cover all three
formats, wrong-order authenticated zeroes, labels-only/object separation,
duplicate keys, the eight-context interaction, and the authorization gate.

These are exactly the eight contexts already exposed by the wording-control
study, selected without ranking individual outcomes but not held out from prior
analysis. There is one paired seed per context. Multiple records share premises,
so 384 labels are not 384 independent units. Field order changed both natural
instructions and structured-output property/required order; previous objects'
tags remained visible during generation. The result therefore identifies a
format/instruction package, not an attention mechanism or decoding cause. A
fresh-context replication and the already planned labels-only/host-side join are
the comparisons that can promote or revise this signal.

The reviewer used prior independent-audit architecture and had authored
predecessor readers, but did not author this producer study. The scientific score
was recomputed from raw/native artifacts without importing producer scoring.
