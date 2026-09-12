# MRCR V7 outcome addendum

V7 finally exercised the model cleanly, but it did **not** demonstrate successful MRCR retrieval.
The owner completed and released in 368.389 seconds. All 32 episode records and all 67 native
start/result pairs are present; every native result is `status=returned`. Exact reconstruction maps
all 67 responses one-to-one to trace calls: 27 episodes used two root turns, four used three, one
used one, and there were no child turns or recursive invocations.

The frozen gate says eligible because 7/8 G4 groups have different continuous scores and the mean
score among the 31 scored episodes is 0.05845. This is a weak learning signal, not evidence of a
correct procedure: **0/32 answers exactly match gold**. Twenty-six contain the 12-character marker,
25 begin with it, and 26 receive positive SequenceMatcher overlap. Thus all seven mixed groups vary
only among wrong answers. A root update could optimize overlap or marker-bearing generic text without
learning the requested retrieval.

One episode (`bc030f...`, q3-o0 repeat 1) is unavailable under the frozen scorer. It has one exactly
mapped returned root action (192 tokens, finish reason `stop`) but the assistant content and root
reply are blank. There are no trace/native errors. This is an authenticated model-produced invalid
terminal, but this report preserves it as unavailable rather than silently dropping it or changing
V7's reward to zero.

The original `real_external_inspection` flag also needs care. It is true for 31 episodes, while only
19 have a nonempty tool observation without exception text; three have exception-bearing tool
observations and ten have no nonempty tool observation. None of the tool observations contains the
exact gold answer. These counts distinguish an attempted `/context.txt` inspection from successful,
correct evidence recovery.

Decision: do not promote controller RL from V7's mixed-score gate alone. The repaired short32 V2
campaign is a better next diagnostic because it retains exact original JSON documents across eight
distinct training contexts and now has exact causal accounting. Report exact answers, marker-valid
wrong answers, unavailable outcomes, and continuous overlap separately. If short32 also yields zero
exact answers, retire continuous-overlap mixedness as sufficient training evidence and move to an
exact-verifier task/interface or a simpler input/ledger comparison.

The original watcher failed only during additive report generation because a nested reused-core
`REPORT.json` already existed. It did not affect the immutable V7 run. Machine-readable evidence is
in `REPORT_ADDENDUM_V2.json`.
