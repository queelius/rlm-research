# Operator-diverse SFT: independent audit of original attempt

Status: sealed original-attempt audit; the trained comparison was not run.

## Answer

This attempt does **not** estimate an SFT effect. It produced a complete, internally consistent
72-trajectory training corpus and an unchanged-policy readout, but the trainer lost GPU visibility
before loading a model, evaluating the gate, or taking an optimizer step. Consequently every one of
the 24 planned SFT6 endpoints is an infrastructure NULL. Treating them as failures, zeros, or a
negative SFT result would be wrong.

The narrow completion recovery is scientifically defensible only as completion of the frozen arm:
reuse the immutable corpus and original start, seed, gate, six passes, learning rate, and 24 SFT6
coordinates; retain this attempt's baseline without rerunning it. Recovery evidence must be reported
as a separate attempt joined to this frozen baseline.

## Capture evidence

- 72/72 planned teacher trajectories exist; the independent parser found no coordinate, child-count,
  prefix-ID, cumulative-map, independent-scalar, action-mask, or span-partition discrepancies.
- The captures contain 324 current-action root turns and 22,847 supervised target tokens.
- All 180 planned real c32 child requests returned. Their known usage is 175,104 prompt and 18,173
  completion tokens; cache accounting is unavailable.
- Child fallibility was preserved: 82/1,152 child labels were wrong, affecting 46/72 trajectories.
  The scalar computed from executed child outputs disagreed with host gold in 14/72. These were not
  repaired. Thus the corpus trains the frozen routine on authentic observations rather than hidden
  truth, while also embedding real child error.

## Training and readout

The corrected training interpreter had the required PEFT stack, but the inherited command launcher
removed `CUDA_VISIBLE_DEVICES`. Training exited after 5.57 seconds with `ValueError: MAIN must
assign exactly one GPU`. There is no gate receipt, optimizer state, checkpoint, or selected adapter.
This is a pre-training infrastructure failure.

The unchanged arm completed 22 authentic native finals among 24 planned endpoints. It scored 2/24
on the planned denominator (8.33%), or 2/22 conditional on availability (9.09%); treating its two
NULLs as either wrong or correct gives bounds of 2/24 to 4/24. Both correct answers were nonzero.
Trace inspection found direct file inspection and handwritten keyword heuristics, with no child
calls or live accumulator. They are genuine task successes, but not evidence of the intended
acquire-accumulate-reduce mechanism.

The frozen inventory is therefore:

| arm | planned | RESULT files | native available | strict correct | NULL |
|---|---:|---:|---:|---:|---:|
| unchanged | 24 | 23 | 22 | 2 | 2 |
| SFT6 | 24 | 0 | 0 | 0 observed | 24 |

All 24 pairs are unavailable for a treatment comparison. “0 observed” in the SFT6 row is not a
zero score: nothing was sampled.

## Cost and timing

The owner ran 1,630.103 seconds. Capture took 1,298.155 seconds; the failed training stage took
6.516 seconds wall-clock including orchestration; unchanged service/readout took 321.899 seconds.
The retained cost ledger has 259 physical attempts and 258 returns: 314,898 known input tokens,
38,624 known output tokens, one response with output usage unavailable, and no reliable cache-token
accounting. This includes 180 capture child calls, 24 baseline child calls, and 55 baseline root
calls. The 324 authored teacher actions are offline trajectory turns, not additional provider calls.
Provider billing was not measured.

The owner terminal is incomplete but cleanly released: no active unreleased service remained. The
parent job exited normally from the scheduler's perspective after 1,630.556 seconds with exit code 1.

## Interpretation and next comparison

The reusable finding is that a diverse, execution-grounded 72-trajectory corpus was successfully
captured with honest child mistakes and correctly targeted action masks. Whether six updates from the
857 reference improve held-out operator behavior remains unanswered. The smallest valid next step is
the approved isolated recovery, followed by an exact paired comparison to the retained unchanged
coordinates. Even a score gain should be separated from mechanism: audit child acquisition,
cumulative state, scoped reduction, and stopping rather than inferring the routine from final scalar
accuracy.

## Audit provenance

The method was frozen before scientific outputs existed. The runtime amendment was added before
launch after MAIN found the original environment error. This auditor had previously audited the
warm-start reference and recommended 857 as the least-assumption common start; that decision did not
establish superiority. The auditor did not author this implementation. Machine-readable recounts are
in `AUDIT.json`; method and source pins are adjacent. No sampled code was re-executed and no response
was repaired.
