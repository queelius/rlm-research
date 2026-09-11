---
id: mnli-field-order-replication96
status: completed_exploratory_gate_miss
question: Does label-first selectively reduce misleading-reference interference on 16 fresh contexts?
evidence: AUDIT.json
contexts: 16
planned_calls: 96
available_calls: 96
primary_did: 0.09765625
gate_passed: false
claim_level: directional_fresh_context_replication_below_frozen_magnitude_gate
---

# The selective label-first effect replicated directionally but missed the 10-point gate

On 16 fresh paired contexts, label-first improved the misleading-reference arm from 302/768
(39.32%) to 369/768 (48.05%), a gain of 67 labels or 8.72 percentage points. The aligned arm moved
from 639/768 (83.20%) to 631/768 (82.16%), a loss of 8 labels or 1.04 points. The prespecified primary
difference in differences is therefore +75/768, or **+9.77 percentage points**.

The interaction was positive in 14/16 contexts, negative in one, and tied in one. Availability and
contract validity were 16/16 in every arm. The frozen replication gate required at least +10 points,
at least 12/16 positive contexts, and no availability loss. The sign and availability conditions pass,
but the magnitude condition misses: an integer numerator of at least 77/768 was required, versus 75.
Thus the replication is strong directional evidence consistent with the eight-context pilot (+11.72
points), but it does not formally promote the claim under the prespecified rule.

| Visible reference | Tag first | Label first | Label-first change |
| --- | ---: | ---: | ---: |
| Names another record | 302/768 (39.32%) | 369/768 (48.05%) | +67 (+8.72 pp) |
| Unrelated identifier | 646/768 (84.11%) | 607/768 (79.04%) | -39 (-5.08 pp) |
| Aligned identifier | 639/768 (83.20%) | 631/768 (82.16%) | -8 (-1.04 pp) |

Against the unrelated-identifier arm, the order interaction is +106/768 (+13.80 points), positive in
15/16 contexts. The primary aligned-controlled interaction is the prespecified decision quantity;
the unrelated comparison is supporting evidence only.

## Sixteen paired context effects

Values are label-first minus tag-first in labels out of 48. The primary column subtracts the aligned
change from the misleading change.

| Context | Genre | Misleading | Unrelated | Aligned | Primary DID |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0 | government | +2 | -2 | -1 | +3 |
| 1 | government | +6 | 0 | -1 | +7 |
| 2 | government | +5 | -2 | -1 | +6 |
| 3 | government | +3 | -4 | -3 | +6 |
| 4 | slate | -4 | -3 | 0 | -4 |
| 5 | slate | +6 | -1 | 0 | +6 |
| 6 | slate | 0 | -2 | -1 | +1 |
| 7 | slate | +6 | -3 | 0 | +6 |
| 8 | telephone | 0 | -1 | -2 | +2 |
| 9 | telephone | +8 | +1 | 0 | +8 |
| 10 | telephone | +6 | 0 | +1 | +5 |
| 11 | telephone | +8 | -8 | -1 | +9 |
| 12 | travel | +13 | -4 | +1 | +12 |
| 13 | travel | -1 | -5 | -1 | 0 |
| 14 | travel | +5 | -1 | +1 | +4 |
| 15 | travel | +4 | -4 | 0 | +4 |

On the 515 positions per misleading arm where displayed-record and named-record gold labels differ,
tag-first produced the named record's label 359 times, the displayed record's label 91 times, and the
third label 65 times. Label-first changed this to 242 named, 187 displayed, and 86 third-label outputs.
This conditional diagnostic is consistent with reduced wrong-record capture, but records and premises
are not independent observational units and it is not a decoding-mechanism proof.

## Native availability, cost, and authentication

The independent format-aware reader authenticated all 96 request wires, saved prompt IDs, completion
IDs, model identity, response bodies, usage identities, and the released-base service configuration
before scoring. All calls were physical, returned one HTTP choice, ended with `stop`, and passed the
whole output contract. There were no NULL endpoints, unexpected call directories, or disagreements
with producer core scores. `OUTCOME_PINS.json` contains 321 retained producer files.

Known usage was 362,826 input tokens and 92,196 output tokens, with zero cached tokens and no unknown
usage fields. Provider billing and active GPU seconds were not measured. Owner wall time was 580.148
seconds and parent wall time was 582.967 seconds; neither is an active-GPU measurement.

Before any outcome read, the audit authenticated owner terminal SHA-256
`5ae0124eb74fc4c13cbaf668310f47375f93b3fae258f289c4d89e54fda7fc80` as complete, released, and
error-free. Parent EXIT SHA-256 `952b39317f1a1d559712ee216dbac35014c9328831ace770f2917828bc4baf86`
reported exit 0, no timeout, no remaining GPU PIDs, and the exact matching completion marker.

## Limits

The parser derives tag-first versus label-first grammar from each arm and treats authenticated grammar
failures as observed zero rather than NULL. All responses happened to be contract-valid. These are 16
fresh context clusters with one paired seed each; 768 labels per arm are not 768 independent samples.
Field order changes the instruction/schema package and generation history, not an isolated attention
mechanism. The recovered launch reused exactly the originally sealed scientific inputs after a
prelaunch wrapper failure that produced no scientific outcome.
