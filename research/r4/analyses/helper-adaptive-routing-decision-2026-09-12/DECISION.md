# Adaptive helper routing: decision after the fresh 128 panel

## Bottom line

Do **not** promote O/A disagreement → singleton as the default helper policy. It beats the
three-vote comparator on the preregistered screen, but that comparator itself is worse than the
one-call original policy. Across both datasets, original16 and selective are tied at **117/128**;
selective uses **38,623** observed tokens versus **14,518** for original16 (**2.66×**). Three-vote
is 115/128 at 43,539 tokens. Thus the selective screen answered a narrow cost question, not the
deployment question.

## What the route actually selected

O/A disagreed on only 12/128 records: 4 TREC and 8 AG News. The original prediction was already
correct on 8/12. On TREC, all four disagreements were `original correct / A wrong`; singleton kept
three correct and damaged one. On AG News, the disagreement set comprised four `original correct /
A wrong`, three `original wrong / A correct`, and one `both wrong with different labels`.
Singleton versus original had three wins, two losses, and three ties there. Overall, singleton
versus original was **3 wins / 3 losses / 6 ties** on routed records.

The apparent advantage over three-vote is mostly avoidance of a harmful third contextual map:
singleton versus the three-vote label was 3 wins / 1 loss / 8 ties. It does not show that
disagreement identifies original errors. Indeed, eight of twelve routed originals were correct.

The more important blind spot is correlated agreement. O and A agreed on 116 records, including
seven shared errors: 2 TREC and 5 AG News. Those errors include semantic boundary cases such as
`major fault line` (entity→location), `position ... play` (human→entity), Microsoft/Apple business
stories labeled Sci/Tech, and sports/world stories with salient business or hurricane language.
No disagreement-only policy can recover them.

## Ranked next experiments

1. **Recommended: fresh cross-solver verification pilot, not another contextual vote.** Freeze a
   new 128-record panel before scoring. Obtain one c32 original16 map and one unadapted-base4B map
   per block. For every cross-model disagreement, ask the unchanged QS6 root a singleton,
   gold-free arbitration question containing the raw record, label definitions, both candidate
   labels, and a stated default of c32 unless evidence supports switching. Also query an equal,
   SHA-selected set of model-agreement records as a matched verifier control. Report c32 original,
   base original, arbitration policy, an oracle best-of-two ceiling revealed only after commitment,
   correctness changes, and authentic component costs separately by dataset.

   This is decision-relevant because the intervention uses a genuinely different solver and can
   expose whether a learned verifier selects complementary expertise or merely perturbs answers.
   It is not a learned router or an RLM accuracy claim. Prior data warn that the task is hard:
   on the earlier fixed256 panel, c32/base disagreements were 37 records and favored c32 31-to-5
   (one both-wrong tie), driven by TREC. That makes `keep c32` the strong baseline and prevents a
   flattering comparison. Promote only if the arbiter beats c32 overall with **wins > losses in
   each dataset**, retains complete coverage, and its gain is larger on disagreement than on the
   matched agreement-control set. Retire semantic arbitration if best-of-two headroom is under
   3/128 or the arbiter does not recover at least half of that ceiling without net harm. Expected
   budget: 16 full-map calls plus at most 2×128 singleton arbitration calls; likely 10–20 minutes
   on one A100, hard cap to be set from measured prompt lengths before sealing.

2. **Calibration acquisition, then confidence routing.** A later panel could request explicit
   per-record class scores or full class log-probabilities and calibrate a threshold on a disjoint
   development split. Do not treat current processed grammar token log-probabilities as class
   margins: the saved native response exposes only chosen-token probabilities under ordered JSON
   grammar, with many forced tokens and no complete alternative-class distribution. A confidence
   router without a separate calibration split would be post-hoc threshold fitting.

3. **Retire immediate repeats of O/A/B contextual voting or singleton granularity.** The fresh
   experiment already shows correlated agreement errors, zero net gain over original, and 2.66×
   cost. Another same-family rerun has lower information value than changing the solver or
   uncertainty signal.

## AnomalyXL relevance

The independent AnomalyXL mini is not evidence for a routing reward yet. Direct answered 10/10
with mean official score 0.0916; Python scored 0 because eight first inspection generations hit
the 512-token cap mid-code and two later cases timed out after repair turns. It is an underbudgeted
interface result, not a meaningful direct-versus-Python comparison. Its exact partial scores could
eventually support route/depth learning, but only after a budget-shape control yields valid Python
episodes. Do not mix it with the classification routing conclusion or start RL from this result.

## Evidence boundary

Counts above were recomputed from the independently audited 152/152 raw responses and committed
O/A-only escalation. Logical policy costs reuse one shared physical collection and are not
counterfactual wall times. Items share batched calls, so no naive item-level significance claim is
made. “Fresh” means excluded from verified local helper optimization and prior panels, not unseen
in base-model pretraining.

