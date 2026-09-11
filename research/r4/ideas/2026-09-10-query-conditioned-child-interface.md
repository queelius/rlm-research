---
id: query-conditioned-child-label-space
status: ranked_candidate_not_gpu_ready
created_utc: 2026-09-10T18:50:55Z
related_questions:
  - rq:sufficient-interface
  - rq:reduction
motivation:
  - claims/child-adaptation-transfers-to-official-test.md
  - claims/question-sensitive-executed-composition.md
rank: after_current_recoveries_and_queued_scale_rlvr_controls
outcomes_for_this_hypothesis: none
---

# Ask the child only for distinctions the current question needs

The trained root now often performs the correct computation, but wrong child
labels still spoil answers. The child adapter improves six-class labeling on
optimizer-disjoint data, yet its error rate is not negligible. A useful harness
question is whether each child should solve the entire classification problem,
or only the distinctions that matter to its parent's current question.

For example, a root may need to find users with an entity question and sum the
weights of their location questions. It does not need to distinguish human-being
from numeric-value questions: both are irrelevant to that calculation. Could a
child asked for entity/location/other make fewer task-relevant mistakes?

## Smallest informative comparison

Use eight16-record batches, selected by a frozen hash over the official-test
record IDs without consulting model outcomes. Reuse the established typed-ID
map interface and the released4B base and fixedc32 adapter. For each batch use
six predeclared cyclic category pairs, covering every category twice. Compare
all-six-category output with A/B/other output, while both prompts state the same
requested pair and all category definitions. Freeze a fresh paired seed per
batch/pair; all8×6×2weights×2interfaces=192 calls remain in the inventory.

Score both outputs in the identical A/B/other space; the full-category result is
projected by an explicitly declared analysis mapping, not silently repaired.
Measure target-specific false positives and false negatives, whole-batch
task-relevant exactness, native availability, generated tokens and wall time.
Keep contexts and paired seeds as dependence units. All-zero target batches and
malformed observed outputs stay in the denominator. No root result is implied.

OneA10040GB can use the existing dual-adapter/base service; a provisional1800-
second outer cap should be ample based on the completed148-call comparison.
Every response is an incremental checkpoint. Prepare exact source hashes,
fresh-seed inventory, masks/schema, request bodies, private projected gold and
CPU actual-service/collector integration checks before accepting the job.

## What changes our mind

A gain of at least five percentage points in target-relevant accuracy or a clear
whole-batch exactness gain, without lost native availability, promotes a paired
root-level test. A base-only gain suggests the fixed six-class training format
limits interface flexibility; that motivates matched interface-specific SFT,
not a claim that either model is universally better. A null or negative effect
deprioritizes this reduction of the child label space and favors improved child
weights, selective verification or better batching.

This is a candidate design, not a novelty claim. Query-conditioned sufficient
representations and task-conditioned classification have extensive prior work;
review primary literature specifically before any publication claim. Changes
to instructions and label vocabulary are a bundle, not an isolated explanation
of model internals. Do not let preparing this candidate delay the current ready
GPU queue or the failed-run corrections.
