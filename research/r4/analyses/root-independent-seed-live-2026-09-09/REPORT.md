# Independent root seed: original attempt terminal audit

The attempt made six genuine, contiguous root-only updates, then stopped on a **process-inspection race during service startup**, not a model response or numerical failure. It did not reach checkpoint selection or paired transfer, so this attempt cannot establish replication of the earlier transfer gain. Its completed validation scores are2/8,2/8 and1/8 at steps0,2 and4.

Scope is only `root-rlvr-independent-seed-v1/outputs/attempt-001`, stopped05:58:19.753 UTC on2026-09-09. The separately launched continuation is not included. The [method](METHOD.md) was frozen before this analyst read attempt artifacts and explicitly records the parent's already disclosed interim scores and terminal metadata.

## Actual learning and coverage

The campaign starts from exact original adapter857a7ce6… at step0 with null optimizer/RNG/state identity, not inherited step3. The288 unique rollout seeds are disjoint from the original campaign's seed set; fixed c32de129… child, task compositions and mathematical recipe remain unchanged. Six committed generations bind their own fresh32 coordinates, current preceding root and exact exported group. Original Adam is newly constructed; saved Adam cursors are independently1–6 across504 parameter states, with unchanged parameter ordering and authenticated RNG files.

| Update | Training exact /32 | Mixed-group episodes | Root target tokens | Gradient norm | Recomputed weight delta L2 |
|---|---:|---:|---:|---:|---:|
| 1 | 11 | 24 | 20,189 | 0.1330 | 0.14749 |
| 2 | 13 | 24 | 15,042 | 0.4493 | 0.14164 |
| 3 | 9 | 28 | 25,210 | 0.2073 | 0.11754 |
| 4 | 12 | 20 | 14,822 | 0.1421 | 0.10566 |
| 5 | 16 | 28 | 18,837 | 0.2425 | 0.09571 |
| 6 | 18 | 28 | 15,050 | 0.0931 | 0.08685 |

All504 tensors in each saved adapter were finite FP32; independently computed successive tensor deltas agree with the saved training metrics. All six correction diagnostics passed their frozen health guards. The saved training data comprise152 selected episodes,342 root turns and109,150 root action targets. Child action targets and observation targets are zero: exact root suffix masks, labels, physical IDs/logprobs and trusted role/weight evidence were checked. Child actions remain recorded evidence and may enter masked root context; they are not optimized as labels. Saved native replay identities are retained separately; this audit does not claim a second complete causal-graph reconstruction.

All192 collected training episodes and24 collected validation episodes were complete, observable and admitted. There were no null endpoint outcomes, exclusions, overflow reclassifications or budget-censored coordinates in those nine completed stages. Forty valid training episodes belonged to homogeneous reward groups and did not enter the mixed-group update. Strict rewards are aggregate task answers, not proof of intermediate leaf classification correctness.

Validation0 and2 had the same eight binary outcomes, not merely equal totals. Validation4 had one paired improvement and two regressions relative to0. These are repeated development coordinates on two contexts, not independent confirmation. Training counts fluctuate over fresh seeds on the same task groups; their later increase is not a held-out learning estimate.

Of344 planned collections,216 exist. Round7 has only a generation manifest; no round7 collection or training was started. Round8, validation6/8 and both24-coordinate transfer conditions are unavailable, not128 fabricated failures. `FINAL.json` and `SELECTION.json` are absent. The final committed root is checkpoint6:

`53e822f25323040463ebf4e10f73ea69b4c68b00f612b8bc8de4b89c4b5cf3bb`

Its adapter/config/Adam/RNG/state and all six COMMIT/INPUTS/correction captures remain authenticated and preserved. Missing later presentation files do not erase these updates.

## Failure and timing

The exact STOP traceback follows `start_service → claim_service → snapshot_descendants → observe → process_identity → os.getpgid`, ending in `ProcessLookupError: [Errno3] No such process`. This is consistent with a child exiting between the `/proc` existence/read checks and group lookup. Step6 had a service start record but no `SERVER_READY`, validation6 or inference collection. The owned release record confirms all captured process identities exited and ports were free. No observed task response caused this stop.

Campaign wall time was3,432.94 seconds (57.22 minutes); the accepted child exited1 after3,436.00 seconds, without timeout. Parent session exit0 is merely the coordinator wrapper's status, not experiment success. Final owned release was05:58:17.620 UTC and accepted-job exit05:58:20.274, a2.65-second post-release tail. This is distinct from the much longer CPU tail in the separate root96 experiment; no such long tail is claimed here.

Recorded collection-stage wall times total2,426.72 seconds; six successful service start-to-ready intervals total253.65 seconds, and the failed step6 start-to-release interval54.73 seconds. Saved optimization time totals288.20 seconds. These clocks have different boundaries and are not an exhaustive additive decomposition of GPU use. This attempt stopped before its5880-second work/6000-second exception budgets; it was not budget-exhausted.

## Costs and evidence limits

All2,203 retained calls returned:480 root and1,723 child. Request/result filenames match across all nine routing directories, with no request-only artifacts. Recorded wire/native accounting gives:

- 2,384,966 logical prompt tokens;
- 2,158,784 cached tokens, a subset of prompt tokens;
- 226,182 uncached prompt tokens;
- 353,213 sampled action tokens, including nonselected episodes and validation.

Cache counts are known for all calls. Per-call latency was not correctly projected by the initial audit's `wall_seconds` lookup; the nine empty-sum zeros were explicitly corrected to null before publication. No zero-compute claim is made. [ADDENDUM.json](../../../../ARTIFACTS.md#unpublished-files "Not published: ADDENDUM.json") records this analysis-only correction, original/corrected metric hashes and exact operation sources. No outcome, token, checkpoint or raw artifact changed, and no raw scoring pass was repeated.

The one-pass audit took15.90 seconds, checked27,439 assertions and cached2,713 immutable evidence paths, each physically read once by that pass. [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") records hashes and filesystem fingerprints; closures were authenticated once, never inside an episode loop. Metadata stability is not protection against adversarial same-size/same-timestamp replacement. Three focused helper tests pass. No GPU queries, model calls, signals, scheduler/lifecycle locks or experiment-source edits were performed.

## What this changes

The run proves that fresh original-start root-only updates occurred, not that their task benefit replicated. The operational interruption leaves the frozen selection/transfer question unanswered. The already parent-launched additive continuation may answer it using the same saved lineage and unused coordinates; its extra wall budget and eventual outcomes must be reported separately, then linked—not silently relabeled as completion of this original attempt. Preserve the original STOP and these six checkpoints. Detailed per-stage, per-episode, per-call and checkpoint evidence is in [METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json").
