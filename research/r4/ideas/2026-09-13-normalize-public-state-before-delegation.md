---
id: normalize-public-state-before-delegation
status: cpu_preparation_authorized
phase: exploratory
created_utc: 2026-09-13T00:18:00Z
question_family: harness_information_representation
owner: MAIN
gpu_owner: MAIN_only
comparison: released_base_raw_vs_mechanically_normalized
planned_calls: 36
context_units: 9
---

# Can Python do the bookkeeping before the model makes the decision?

Our current helper must combine records, apply updates, identify the latest
certification checks, and decide which implementations meet a policy. Merely
splitting those records across more helpers did not reliably improve the selected
set. The four-helper condition traded higher precision for lower recall and used
42% more input tokens. Reward training now targets selection directly, but there
is a separate harness question: are mechanical joins an unnecessary obstacle?

## Smallest informative comparison

Use the nine held-out local stages already frozen before selection training,
with their two fixed decoding seeds: 18 answers per condition, 36 physical calls.
Both conditions use the released 4B model, no adapter, the same candidate IDs,
policy, task, temperature0.5, and384-token ID-list output allowance. Run both raw
controls and normalized inputs afresh; do not select the favorable old controls.

The normalizer reads public records only. It applies numeric changes whose
status is `applied`, updates feature sets, and finds the latest row for each
required check. It retains every candidate and reports its effective values and
latest check results, including missing checks. It does **not** evaluate the
eligibility inequalities, filter candidates, compute an eligibility flag, consult
the answer key, or choose a final pipeline. The model still makes the eligibility
decisions. Preserve the transform and exact raw-to-normalized input hashes.

This is an intentionally hand-designed representation intervention: Python
offloads bookkeeping. It is not learned decomposition, autonomous tool choice,
or a claim that the model has learned the operations Python performs.

## Metrics and decisions

Report correct selected sets ignoring order as the semantic primary, balanced
accuracy over present classes, precision/recall, and strict output-format
correctness separately. Preserve all18 planned answers per condition; missing
outcomes are not wrong answers. Record input/output tokens and wall time. Repeated
decodes of one stage do not create additional independent problem units.

A useful gain would motivate testing different update histories and a second
task family, and separating data shortening from the removal of arithmetic and
joins. A flat result would redirect effort toward policy interpretation or
training, rather than adding more helpers. A loss would require checking whether
normalization discarded necessary public information before changing the model.
Do not tune the transformation after seeing these18 outcomes and call it a fresh
test. This nine-stage panel becomes exposed once these comparisons are read.

CPU preparation should reuse the existing native collector and single-model
service. Check the actual HTTP/decode/grading path and a few material transform
cases (draft versus applied updates, latest check, missing check, all IDs kept).
Avoid a new framework. Target one A100, science600s/owner700s/external800s, with
every native call saved. MAIN admission requires the frozen ready receipt.

This is a locally motivated experiment, not a novelty claim. B05 remains a
candidate generated benchmark with a fixed three-stage decomposition. Its public
semantics are in the pinned `structured-decomposition-benchmark` B05 family;
host normalization follows those semantics without using private targets.
