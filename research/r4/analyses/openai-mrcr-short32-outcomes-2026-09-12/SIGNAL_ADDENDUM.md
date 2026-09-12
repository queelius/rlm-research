---
schema: openai-mrcr-short32-signal-addendum-v1
status: COMPLETE_CPU_ONLY
source_report: REPORT_V2.json
---

# Short32 near-success and failure-mechanism addendum

## The four high scores are correct retrieval with transport errors

All four official scores at or above 0.90 select the exact target assistant turn after one explicit
diagnostic transformation: each raw final contains the two characters `\n` wherever the source
has an actual newline. This transformation is **not** applied to the frozen scorer or exact metric.
Two repeats from one context additionally append `**`; one result from another context appends a
double quote; the fourth has no trailing addition. The four episodes span three contexts and score
0.987677 twice, 0.983624, and 0.979250. They are content-correct selections but raw-copy failures,
not wrong retrieved passages.

Two other episodes are a useful negative control: after the same newline diagnostic, each exactly
copies a *different* assistant turn rather than the requested turn. Both score 0.386555. Thus the
official continuous score contains useful ranking signal here, but it is not a pure indicator of
correct retrieval.

## All 32 outcomes

- Correct target with newline/terminal transport error: **4**
- Exact copy of the wrong assistant turn: **2**
- Nonempty procedure failure, marker present: **13**
- Nonempty procedure failure, marker absent: **4**
- Empty invalid terminal: **6**
- Six-turn finite-horizon stop without a final: **1**
- Provider context overflow: **2**

The two unavailable episodes are authenticated 400 responses for prompts of 8,409 and 9,633
tokens against the 8,192-token limit; they are capacity mismatches, not hardware failures. Of the
32 episodes, 26 use Python and 24 encounter at least one tool exception. All four correct-target
episodes recover after a tool exception, so an initial procedure error does not imply retrieval is
impossible. The remaining nonempty low-score finals do not exactly match the target or another full
assistant turn after the diagnostic transformation; examples include copying a long demonstration
passage after printing the wrong part of the list and returning short error/status fragments.

## Learning implication

The original raw-exact reward remains **0/30 available** and must not be rewritten. However, a
blanket conclusion that the trajectories contain no useful overlap is too strong. A prospectively
defined >=0.90 success band would identify four content-correct-but-mis-serialized trajectories
across three contexts. Two complete four-rollout groups each contain one such success and failures;
one partial group contains two successes, one failure, and one unavailable rollout.

This is post-hoc evidence, not permission to optimize this panel. The smallest defensible root-RL
qualification is to freeze the >=0.90 band before collecting fresh independent training contexts,
audit every band success for correct target selection, and require at least two complete mixed
four-rollout groups. Train only after that qualification; keep raw exact as the primary metric on
disjoint evaluation contexts. Continuous official reward is a secondary alternative, but its
0.386555 reward for exact wrong-turn copies must be treated as a known shaping defect. A learned
gain would mean more raw-exact heldout answers, not merely higher character similarity.

No generated code was executed in this analysis. Row-level episode/source hashes and transport
diagnostics are in `SIGNAL_ADDENDUM.json`; raw task text is not duplicated here.
