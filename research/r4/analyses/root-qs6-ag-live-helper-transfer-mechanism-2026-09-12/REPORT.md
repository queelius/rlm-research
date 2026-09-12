# Whole-RLM AG transfer: static mechanism audit

## Result

The helper update changed the leaf classifier, but the unchanged QS6 root did not convert that
change into additional endpoint correctness. The c32 and RL8 arms were both **3/16 correct** and
all 16 paired root outcomes tied. The helper result is real but smaller after deduplicating reused
maps: c32 was **103/128** correct unique record labels and RL8 was **108/128**. The reported
180/224 versus 188/224 totals count the same context map again when it is used by the second query;
they are useful workload totals, not 224 independent decisions.

Across the 128 unique records, only seven labels changed: six c32 errors became correct and one
c32-correct `World` label became an incorrect `Sci/Tech` label. The 14 available query-level map
aggregates improved from 5 exact to 6 exact. Six numeric aggregates changed and all six moved closer
to gold, but the only newly exact aggregate—context 04's `World` count, 4→3 with gold 3—came from
the **correct→wrong** label change. Local label accuracy fell 11/16→10/16 there. This is error
cancellation, not a faithful-map improvement.

The other aggregate changes were still inexact: context 01 Business weight 17→12 (gold 3), context
02 Sci/Tech weight 5→8 (gold 16), context 05 Business weight 16→9 (gold 6), and context 06 Business
count 6→5 (gold 3) plus Sci/Tech weight 10→14 (gold 21). Context 03's corrected label did not affect
its observed World-weight question; its Sci/Tech-count episode had no helper map. Thus “larger helper
signal” and “correct downstream answer” remain different claims.

## The empty observation channel is a concrete controller defect

Four root episodes—context 01 count and context 04 count in both helper arms—ended their reducer
cell with an assignment and no `print`. All three Python tool observations in each episode were empty:
the records load, the assigned helper call/map parse, and the final scalar assignment. The subsequent
root answer was `Answer: 2` in all four cases.

The auditor parsed those code strings as inert AST and recomputed only recognized count/weight
expressions with an explicit trusted host reducer; it never executed generated code. For context 01,
the full helper-map count was 3 in both arms, while the root said 2. For context 04, the generated code
also incorrectly restricted the supposedly global count to users `u0,u1`: its host value was 2 under
c32 and 1 under RL8, while the root said 2 in both. The RL8 case therefore cannot be a readout of the
runtime scalar. More carefully: the blank observations establish that no scalar returned through the
tool channel; they do not identify which latent heuristic produced the final token.

This is not evidence that the root always ignores helper outputs. In 20/20 episodes where the static
reducer was supported and a nonempty scalar observation returned, the final root answer matched the
host-recomputed generated-scope value. Several printed weight/count results changed with the helper
map and the root answer followed them. Two additional supported reducers exhausted the horizon before
returning an observation, and six episodes had no supported final reducer or no reducer at all.

## Was silent assignment taught by QS6 SFT?

No, not in the authenticated QS6 corpus. The exact 72 training episodes underlying checkpoint 6
contain 144 authored Python actions: 72 helper-producing actions and 72 reducers. **All 144 include a
`print`; zero use silent assignment.** All 72 terminal targets are `Answer: N`. The frozen protocol
source also constructs every reducer with `print(result)`. The live silent-assignment behavior is
therefore an out-of-distribution execution mistake or failed retention/generalization, not a target
present in those 72 demonstrations.

## Error decomposition

- **Unobserved result:** four silent reducers returned empty observations; two more supported reducers
  hit the finite horizon before a result returned.
- **Wrong aggregation:** context 04's count code changed the requested all-record scope to `u0,u1` in
  both arms. Context 05 likewise wrote an `u1,u2` restriction before failing to finish.
- **Helper error:** most complete maps remained imperfect. RL8's sole new exact aggregate was caused by
  cancellation, although six unique wrong labels were genuinely corrected elsewhere.
- **Endpoint bottleneck:** improved helper labels and smaller numeric aggregate error yielded no paired
  root win because some changed aggregates remained wrong, one exact count was not observed, and two
  relevant episodes produced no final answer.

## Evidence boundary

The source panel was prospectively frozen from public AG test records and excluded documented local
training/evaluation exposures, but it is now research-exposed and says nothing about base-model
pretraining exposure. There are eight context clusters, not 128 independent contexts. Static
recognition is deliberately conservative; unsupported generated programs remain unknown. No article
text is reproduced here.

Machine-readable paths, record IDs, source hashes, every static reducer result, and the 72-example
training audit are in `REPORT.json`.

