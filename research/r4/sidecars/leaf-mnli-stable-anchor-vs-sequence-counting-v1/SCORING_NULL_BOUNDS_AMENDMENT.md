# Missing-outcome scoring amendment

Independent prelaunch review found that the first scoring revision used zero in the gain calculation
when either member of a context/relation pair was unavailable. Because the frozen gate permits one
unavailable call in a cell, this could turn a missing baseline into an apparent treatment gain or a
missing treatment into an apparent loss.

The additive revision does not change contexts, requests, seeds, order, model, decoder, or GPU
limits. It reports an estimate only over pairs for which both late-position scores are known, plus
worst/best missing-outcome bounds over the fixed planned denominator. These bounds are identification
bounds, not confidence intervals. Promotion now requires the lower bound to clear the 25-point own
gain threshold and the lower bound of the direct treatment-minus-sequential comparison to clear
-10 points. A context counts positive only when its lower bound is above zero. The existing cell
availability and contract-disadvantage requirements remain in force.

Direct treatment-minus-sequential bounds cancel a missing shared labels-only baseline rather than
double-counting its uncertainty. Focused fixtures cover both a missing labels-only baseline and a
missing keyed treatment.

A second prelaunch consistency check distinguished authenticated whole-contract-invalid outcomes
from unavailable outcomes. An observed malformed or key-invalid answer has known zero early and
late correctness under whole-contract scoring; only an unreturned or unauthenticated endpoint has
unknown `[0, 32]` late correctness. A focused fixture locks this distinction.
