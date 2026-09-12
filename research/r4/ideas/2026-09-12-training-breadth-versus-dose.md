---
schema: research-idea-v1
id: training-breadth-versus-dose-20260912
status: proposed_after_seed_replication
created_utc: 2026-09-12T14:18:00Z
priority: conditional_after_replication_and_retention
question: Does distinct training material matter beyond taking more updates?
source_result: helper-agnews-fresh512-interpretation-2026-09-12/FINDINGS.json
source_result_sha256: d7aa44557ee02d8d26435f9cfcbee67ac7337e039f2d61c0db5436efa936a736
GPU_admission: none
---

# Was the gain caused by more examples, more updates, or both?

The completed eight-update news experiment improved 422 to 437 correct on
512 test articles. Earlier single-update experiments barely changed answers.
That comparison changes distinct training material and update count together.
It cannot establish that adding training variety, by itself, caused the gain.

The immediate priority is repeating the successful recipe with a different
seed. If it holds, a small mechanism comparison is more informative than
another arbitrary learning-rate or temperature sweep.

## Smallest proposed comparison

Keep the original c32 starting helper, eight updates, four-article requests,
four samples per request, sampling settings, rewards, optimizer and exact
probability checks. Compare the existing broader recipe's eight different
128-article blocks with a new recipe that presents the first frozen block
eight times. Use fresh generation seeds on every update in both recipes.
Choose the repeated block by the original fixed order, not its observed
reward, loss, category errors or apparent learnability.

The planned optimization opportunities and sampled label decisions match;
the number of distinct articles differs. Both contain the same four categories
in the same proportions. Request lengths and actual rollout time can still
differ and must be reported. A later run with another label-blind repeated
block would be needed before generalizing beyond that block's difficulty.

Keep the same fixed final 512 test for this exploratory mechanism comparison.
It is now research-exposed, not another independently unseen test. Do not
select intermediate checkpoints. Use the separate TREC retention probe to
check whether the update damages a previously learned skill, not as a new
training-selection objective.

## What would change our mind?

- If repeated material learns as well, more updates may be sufficient for
  this task; broader data would not yet have an isolated benefit.
- If the repeated material quickly loses better-versus-worse reward contrast,
  while distinct blocks preserve it, that motivates adaptive training-example
  selection. Report the actual saturation and partial dose; do not silently
  count a stopped run as a completed eight-update accuracy comparison.
- If both complete and only the broader recipe improves, test whether that
  difference repeats across seeds or repeated blocks before attributing it
  generally to training variety.
- If the current positive recipe does not replicate, do not automatically
  spend another full dose on this explanation. First inspect the changed
  labels and variability between completed runs.

## Cost, stopping, and records

The observed broader owner took about35 minutes; a new eight-update arm has
the inherited5000-second owner/5200-second external caps, not a promise of
35 minutes. This proposal does not authorize a launch. Preserve every sampled
answer, unchanged host score, probability check, adapter/Adam/RNG checkpoint,
and fixed request manifest. Reuse only fully qualified baseline measurements
with exactly matching runtime and requests. Stop on the inherited no-signal
or probability gates; no outcome-driven recollection or checkpoint rescue.

This is a mechanism question, not a claim that repeated-versus-varied training
is itself novel. A publication would need a clear RLM-specific consequence,
such as robust helper decisions across input groupings or a better learned
delegation procedure, and evidence beyond this one article classification task.
