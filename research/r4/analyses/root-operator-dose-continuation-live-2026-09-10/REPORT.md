# Exact operator SFT dose: independent audit

## Bottom line

Continuing the same 72-trajectory operator SFT from Adam 6 to fixed Adam 24 produced a large,
mechanistically grounded change on this small paired panel. SFT6 was available on 31/48 full
endpoints and strictly correct on 5/48 (3 zero, 2 nonzero); SFT24 was available on 38/48 and correct
on 29/48 (1 zero, 28 nonzero). SFT24 beat SFT6 in 19 jointly available pairs and lost one, with 3
both correct and 4 both wrong. Twenty-one pairs contain at least one NULL. Even the conservative
unpaired planned-denominator bounds are SFT6 5--22 versus SFT24 29--39, so the direction does not
depend on treating missing responses as wrong.

This is not merely a shift toward a lucky constant. On the 24 source-prepared `root_new` endpoints,
SFT24 achieved 13 strict answers (12 nonzero), versus 3 for SFT6; on the 24 exposed-repeatability
endpoints it achieved 16 (all nonzero), versus 2. The frozen best constants score 8 and 5 in those
strata. The 48 endpoints comprise only 12 context clusters (4 source-prepared and 8 previously
exposed), so endpoints are not independent replications and `root_new` is not globally unseen.

## What actually changed

SFT24 attempted a real c32 child acquisition in every 48/48 planned endpoint (75 physical child
calls total), compared with 1/48 endpoints and 2 calls for SFT6. Among SFT24's 38 authentic finals,
35 had a complete observed child-label map. In 34/35, the final equals an independent reduction of
those actually returned labels; all 29 strict successes are in this group and also displayed the
computed scalar in an executed tool observation before stopping. Five additional finals faithfully
reduced imperfect child predictions to a wrong host answer. One complete-map trace made a reduction
error, and three available wrong traces had only partial or unparsed map evidence. Thus the gain is
evidence of actual acquisition, returned-label use, scoped computation and stop—not just scalar
agreement or memorized zero answers.

The study does not establish robust multi-batch accumulation. Most successful traces requested all
16 or 32 records in one child call. The one completed four-call trace repeatedly overwrote its
`child_answer` variable, then recovered the correct answer through literal inspection of the last
batch. That is authentic task success and error recovery, but not the intended live-map merge.
Another long four-call trace acquired all labels but never produced a final. No sampled code was
reexecuted or repaired in this audit.

The first-action diagnostic is directionally consistent but weaker: all 24 probes were native
available; syntactic `await rlm(...)` intent rose from 0/12 at SFT6 to 5/12 at SFT24, spanning all
three operators and both authored capture-width strata. These programs were never executed. Capture
width is not an exposed user constraint, so variation in their chosen slice sizes is descriptive,
not instruction noncompliance.

## Availability, pairing, and cost

SFT6 retained 45 RESULT files: 31 authentic finals, 14 unfinished native branches, and 3 unrun slots.
SFT24 retained 42: 38 authentic finals, 4 unfinished branches, and 6 unrun slots. Owner completion
does not turn these 23 model-specific/unrun slots into zeros. SFT6 was served first and SFT24 second,
so policy is confounded with phase time despite identical paired coordinates and seeds.

The full readout made 609 physical requests: SFT6 218 (216 root, 2 child) and SFT24 391 (316 root,
75 child). Returned native completions were 215 and 385; 3 and 6 attempts lack confirmed responses.
Known full-readout usage totals 1,790,151 input, 103,915 output, and 1,675,744 cached tokens; usage is
unknown for nine attempts. The 24 probes add 25,790 input, 6,191 output, and 22,336 cached tokens.
SFT6 and SFT24 phases took 651.58 and 689.93 seconds; owner elapsed was 1,353.33 seconds. Billing was
not measured.

## Training integrity and interpretation

The training phase passed the independent 504-moment/RNG/checkpoint/exposure audit with no errors.
Eighteen real updates replayed the same corpus for 411,246 masked target-token exposures. Pre-update
weighted teacher CE fell from 0.46536 at step 7 to 0.08875 at step 24; separate post-checkpoint
first-producer NLL fell 0.96133 to 0.19485 and corrective NLL 0.38998 to 0.05396. Optimizer plus
checkpoint time was 3,658.48 seconds; diagnostic forwards were 10.50 and 10.05 seconds. The plot
keeps these fit measures separate from free correctness and acquisition.

This result supports a dose-dependent reachability effect for this exact model, corpus and interface.
It does not isolate which update between 6 and 24 crossed the threshold, test data breadth, or prove
generic operator learning. The independent method was frozen postlaunch and after MAIN disclosed
checkpoint 7 existed, but before checkpoint contents/readout outcomes. The stricter dataflow parser
was written post-outcome and aggregate-aware; it is diagnostic only and did not alter scoring.

## Decision

Do not immediately add more passes over the same 72 trajectories. First, read fixed intermediate
checkpoints on a small precommitted subset to locate the behavioral transition, then replicate SFT24
on genuinely new context clusters. If the remaining failures persist, add targeted training diversity
for stable stopping/error recovery and real multi-batch map accumulation, rather than ceremonial
child calls. Keep child semantic error separate: five wrong SFT24 finals were faithful reductions of
wrong child maps and cannot be repaired by teaching the root to ignore its observed inputs.

Artifacts: `METHOD_READY.json`, `READOUT_METHOD_READY.json`, `TRAINING_AUDIT.json`,
`READOUT_AUDIT.json`, `DATAFLOW_AUDIT.json`, `TRAINING_REPORT.md`, and
`operator-dose-fit-vs-behavior.svg` in this directory.
