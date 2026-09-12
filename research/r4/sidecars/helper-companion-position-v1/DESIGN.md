# Companion identity versus record order:64 fresh helper calls

Status: design only, MAIN review required; no implementation or GPU launch authorized here. Preserve all existing queued/live sources. Proposed next sidecar: `helper-companion-position-v1`.

## Question and fixed arms

The independently audited size experiment is dataset-opposite: TREC117/119/120 but news115/112/109 correct at16/4/1. Does changing companion records while retaining each record's numbered slot change full-category predictions? Separately, does reversing the order within unchanged groups change predictions?

Use exactly the frozen256 public records from `helper-unseen-generalization-panel-v1`,128 per dataset. Reshape each existing dataset order into eight rows of16 record slots. Four arms each require eight calls per dataset: original groups, each original group reversed, neighbor regroupingA, neighbor regroupingB. Total64 physical calls,1024 label slots,256 unique records with four related predictions each. Fresh original control is mandatory; no previous service outputs are reused.

Original: unchanged eight groups. Reverse: same companions in each group, slot `j` becomes `15-j`. This changes ordering and relative presentation, not an isolated absolute-position intervention.

NeighborA/B: for each dataset, arm and column `j=0..15`, independently shuffle row indices0..7. Output row`b`,column`j` receives input row`permutation[j][b]`,column`j`. Every record occurs exactly once per neighbor arm and retains its original numbered slot. Companion identities and preceding text lengths can change; absolute token offsets are not preserved. Keep fixed points rather than rejection-sampling advantageous rearrangements. Freeze per-record old/new group, slot and companion-overlap inventories. No gold is read by permutation generation.

## Fixed schedule, prompts and seeds

Model/native sampling seeds: TREC202609120930 and news202609120931, temperature0, unchanged c32/tokenizer/full category definitions, ordered keyed schemas, max1024 output tokens,8192 context. Each arm uses the same dataset model seed.

For each dataset/neighbor-arm/column, seed `random.Random` with the integer SHA256 of the UTF-8 string `helper-companion-position-v1|202609120932|<dataset>|<neighbor_A_or_B>|<column>`, then shuffle the initial row list0..7 once. Pin the Python version. Freeze all64 bodies and exact wire-order schemas before any scoring.

For block0..7 alternate dataset order (TREC then news on even indices, reversed on odd); rotate the arm list `[original, reverse, neighbor_A, neighbor_B]` by `(block + dataset_index) mod4`. This spreads order/cache exposure without outcome adaptation. Neighbor pairing is by immutable record ID, not same request block. Evaluate all arms regardless of results.

Use the sealed size-study public prompt builder for arbitrary selected records and the same sealed native v4 batch-invariant service. One fresh shared service; require engine pre-exec attestation and actual final EngineCore batch-invariant trace. Freeze source/model/tokenizer/runtime/exposure closure. No flag-off pooling or gold in requests.

## Endpoints and interpretation

Report correct/wrong/unavailable out of128 per dataset/arm, label confusion, paired per-record wins/losses versus fresh original, and prediction-label changes. For each neighbor arm, report original-versus-neighbor disagreement at the same numbered slot; compare the two predeclared neighbor rearrangements without selecting a winner. Reverse-versus-original disagreement tests whole-group reversal sensitivity, not a clean causal separation of position from order. Companion-overlap inventories are descriptive, not an outcome-selected subgroup.

Record actual physical input/output/cache tokens and request/startup/owner time. Errors, invalid outputs and unattempted slots remain separate; no hidden retries or zero-cost interpretation of missing usage. Count1024 prediction slots as related outputs on256 records, with eight request clusters per dataset/arm—not1024 independent trials.

Decision: any verified same-slot disagreement establishes presentation-context sensitivity on that record under these frozen conditions, not an attention mechanism or adaptive-policy benefit. A same-direction accuracy shift in both neighbor arms motivates an independent-panel replication of companion effects; mixed/no shifts remain informative stability evidence. No data-driven selection of a regrouping, training examples, or claimed general recursion improvement. Dataset-specific interpretation is necessary given the existing opposite size trends.

## Bounds and implementation seam

Proposed owner900seconds and external1000seconds under MAIN's shared GPU flock. At observed roughly9seconds per targeted16-record request,64 calls plus service startup can fit this exploratory cap, but full-label request timing may differ. Preserve caps after launch; incomplete output is explicitly partial and cannot establish full-panel effects. Save exact request/response wire, token/schema/ID/finish audits and atomic progress after every call; cleanly release on success, exception or signal.

Thin implementation would reuse native lifecycle/credential seams and frozen builder only, with an independent64/1024 schedule and summary. Focused CPU tests: each ID exactly once per arm; reverse preserves companion set; both neighbor arms preserve each record's original slot while changing companions overall; exact ordered schemas; input+1024 context bound; hand-scored paired predictions including missing calls. MAIN approves design before implementation and independently approves READY before launch.
