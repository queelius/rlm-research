# Decisions from the completed instruction-by-weights comparison

Decision time: September 9, 2026, approximately04:47 UTC. This is an exploratory
research update, not a revision of frozen experiment inputs or promotion to a
confirmatory claim.

## The new evidence

Original root: ordinary instructions6/24, return-type reminder9/24. Trained root:
ordinary20/24, reminder14/24. The reminder's trained-root effect is negative in
four source contexts and tied in two; the trained-weight advantage survives
both prompt conditions. All96 episodes are observed. The full report and raw
audit are in [the instruction study](../analyses/root-contract-factorial-live-2026-09-09/REPORT.md).
This is fresh evaluation sampling, not a second training seed or new contexts.

The reminder does not establish a current string/list bug repair: direct extension
of .answer text was rare, and trained-root first tool requests were structured
in24/24 cases in both arms. The negative trained effect therefore cannot simply
be described as more first-tool JSON failures. Do not infer internal mechanisms
from these aggregate observations.

## Decisions now

1. Keep ordinary instructions for the existing trained checkpoint. Do not turn
   the reminder into a default. The accepted independent-seed recipe stays frozen;
   its preparer did not read these results.
2. Finish the queued grammar/B/placeholder controls before another ID-target SFT
   run. B already matched that specialized training in the earlier HF readout.
3. Run the prepared independent root training seed from original step0. This
   tests a different uncertainty: whether the learning gain repeats, rather than
   whether one checkpoint produces similar gains under new sampling seeds.

## Ranked follow-ups after those jobs

| Question | Smallest informative comparison | Compute shape | Decision rule |
| --- | --- | --- | --- |
| Does the reminder's weight-dependent effect persist on new contexts? | Freeze new source-group-disjoint contexts and balanced original/trained × ordinary/reminder runs; include all cases without posthoc exclusion. | One4B service per weight, about96–128 episodes, roughly20–40 minutes of one A100 including startup; bounded before launch. | Pursue if the direction recurs across context groups; narrow or retire if it disappears. Report actual tokens and failures, not just final accuracy. |
| What observable behavior accompanies the trained model's regressions? | CPU-only posthoc trace screen for requested chunk sizes, helper output format, parse-error handling and coverage on paired regressions. | Existing raw traces; zero GPU. | Use concrete recurring patterns to design one intervention. Marker counts alone do not prove a mechanism. Do not delay a ready GPU run for this screen. |
| Does a source-bound helper result improve complete RLM answers? | Pair the current string-return interface with an optional validated record-map interface that reports missing/duplicate IDs without revealing correct labels; keep weights/tasks/budgets fixed. | One4B RLM, initially32–64 paired episodes with rootless execution; estimate20–40 minutes after a tiny integration check. | Promote only if final answer accuracy or cost improves, not just parsing or item accuracy. Retain raw returns and errors; never silently repair them. |
| Can training make interface changes less brittle? | After at least one independent seed succeeds, compare fixed-interface training with a matched curriculum varying truthful return instructions; evaluate both on held-out interface variants. | Two separately budgeted4B LoRA RLVR runs, approximately100 minutes each under current8-update recipe. | Require cross-interface robustness beyond the training prompt, with training/call/token costs and repeated seeds. If only one prompt benefits, narrow the claim. |

These are ranked proposals, not accepted runs. Source-group availability, precise
episode caps and frozen metrics must be resolved before launch. Generic numbering,
RLM RLVR and harness–weight adaptation are already prior work; see the
[publication-positioning review](../analyses/publication-positioning-2026-09-09/REVIEW.md).
The possible contribution is a careful account of capability surviving—or failing
at—the interfaces between a model, its tools and smaller model calls.
