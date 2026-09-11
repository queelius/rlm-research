# Post-SFT controls: audited exploratory results

The strongest result is a correspondence/selection limitation, not merely invalid JSON. Local16 substantially outperforms requesting16 while showing64, including with original weights; explicit indexed outputs also outperform anonymous64 arrays with the old trained child. Thus leaf SFT is **not the sole cause** of selection failure and improves these scores overall. Training A/B improves some constrained-array semantics but does not reliably teach exact free-output cardinality. These are small, adaptively inspected sets, not broad benchmark or attention-mechanism claims.

## Denominators and provenance

The completed suite contains **600 actual HTTP calls**: representation24 + rotation32 + SST-2 transfer480 (120 per weight) + optional free/schema TREC64 (16 per weight). This reconciles MANIFEST's536 primary +64 optional; both stages completed in488.20s. Every raw response score was recomputed from saved content and host gold and matched the recorded score. Every saved request/coordinate/response alias passed the frozen-body identity checks. No reruns or live endpoint calls were used for this audit.

TREC representation, rotation, mixed-schema and scope use the same four inspected validation contexts/256 distinct question groups. Each arm repeats these questions at two seeds: typically512 assignments, **not512 independent questions**. SST uses four different contexts/256 distinct binary SST-2 validation sentence groups, also repeated twice. `natural5` means batches of five (12×5 + one×4 per64-record context), not the five-class SST-5 dataset. Template12 uses six already-inspected source-test compositions/384 question groups, paired by two tool-serialization templates; it is not twelve independent documents. The saved256 validation and384 template question-group sets have zero intersection; this is not a claim about all historical use or base-model pretraining.

The four weights are exact original converted step0, old selected c32de checkpoint128, and fixed final A/B epoch2 checkpoints206/204. A/B were not chosen using these transfer outcomes. Disk descriptors and launch/live-alias preflights are retained, but they are not an attestation of live GPU-memory contents. All HTTP experiments use the qualified reconstructed first-leaf ChatCompletions proxy, not recursive native-Train trajectories. No tools are executed. T=.5, top_p=1, top_k=-1, min_p=0; output cap1024 except all three representation arms use3072. Template12 is separate greedy BF16-base/FP32-adapter HF generation, cap1024.

## Main counts

| Comparison | Original | Old selected | A final | B final |
|---|---:|---:|---:|---:|
| SST-2 natural5 correct /512 planned |462|459|470|470|
| SST-2 schema64 correct /512 aligned |318|308|326|324|
| SST-2 free64 valid arrays /8 |0|0|1|1|
| TREC schema64 correct /512 aligned |135|179|219|241|
| TREC free64 valid arrays /8 |0|0|1|0|

All constrained64 arrays are valid. Old SST natural5 has102/104 valid small-array calls and502 aligned assignments:459/502 among aligned, versus459/512 planned. The other weights have104/104 valid calls and512 aligned assignments. Missing/malformed arrays are not evidence of512 incorrect semantic decisions. The single valid free64 array gives A30/64 correct on TREC and A48/64, B44/64 on SST; these are selected valid subsets, not comparable full-set semantic accuracies.

Old-child representation is anonymous181, indexed405, echo419 correct, each /512 with8/8 valid outputs. Anonymous input-position quartiles are98/32/28/23 correct (each /128); indexed93/96/111/105 and echo97/97/114/111. Indexed output uses5,584 completion tokens versus anonymous1,783; echo uses15,009. Output identity scaffolding helps here but costs more and changes more than one representation property.

Rotation offsets0/16/32/48 score181/189/201/190 per512. The high-accuracy quarter moves with **visible input position**: first input quartile scores98/97/110/104 per128, while final input quartile scores21/25/22/27. This weakens an explanation based only on which questions originally occupy the first block; it does not establish a particular internal attention mechanism. Representation anonymous181 and rotation offset0's181 are separate calls; mixed-schema old179 is another same-question measurement, not a contradictory denominator.

## Scope72 and unchanged replay

| Old-child arm | First correct /512 | Unchanged replay /512 | Valid calls each run | First-run logical input / completion tokens |
|---|---:|---:|---:|---:|
| All64 visible → all64 output |145|143|8/8|23,384 /1,683|
| All64 visible → target16 output |153|153|32/32|82,784 /1,957|
| Only target16 visible → target16 output |348|349|32/32|42,392 /1,952|

First/replay elapsed21.21/21.27s. All72 requests and physical prompt-token sequences are exactly equal between runs. Raw output text is identical in3/8,30/32,25/32 calls respectively; prediction agreement is480/512,508/512,500/512. These are unchanged-weight trajectory/output variations, not learning. Repeated full prefixes are fully charged: full16 uses3.54× the logical input of all64 and1.95× local16.

For full16 target offsets16/32/48, the **posthoc** diagnostic finds only71/384 labels correct for the requested records, but176/384 agree with the first visible16 records' gold (replay175). Predictions match the all64 arm's first16 predictions291/384 times (replay286). This supports requested-ID neglect as a follow-up hypothesis; it is not a corrected score, a repair, or proof of the exact computation being performed.

The full64 visible-record block is byte-identical in all64/full16. Full16/local16 have identical instructions and requested IDs, with only non-target records removed. Thus the latter comparison isolates extra visible records conditional on this requested-target protocol. All64→full16 also changes output selection burden and cannot isolate output-chain length alone.

Aggregate counts remain weak even with local16. In the first run, local16 exactly counts human-being0/8 and numeric-value2/8 complete64 contexts; corresponding target16 endpoints are7/32 and16/32. Some correct counts cancel false positives and negatives (including3/7 exact full16 numeric target-count cases), so use aligned semantic scores as primary.

The subsequent **original-weight72 contrast completed** in35.60s: all64 scores111/512 (8/8 valid); full16 scores105/512 (32/32 valid); local16 scores192/512 planned,192/480 aligned (30/32 valid). All72 bodies differ from the old-child run only in model; all72 physical prompt sequences are exactly equal across weights. The two invalid local16 responses are model output-budget failures, not missing calls: context1/offset32 and context0/offset48 at seed981261602 each emit15 labels, then4,615/4,632 trailing whitespace characters, exhausting the1024-token cap without a completed array. Neither contains a tool call or infrastructure error. No partial labels were scored or repaired.

Original weights therefore also have a local-input advantage, and old SFT improves all three conditions. The original later-target diagnostic is weaker:69/384 correct requested labels versus89/384 matches to first-visible16 gold. The current evidence supports a shared protocol/selection limitation, with a stronger first-visible-label pattern after old SFT—not a claim that SFT created the problem.

## Why the CPU prompt-match flags are zero

This is a **real token-order difference**, not an absent hash field, a digest-serialization mismatch, or missing questions. On all336 calls with frozen CPU hashes (120 TREC suite +216 scope), reconstructing the raw-request HF template reproduces the stored CPU hash exactly, but none equals the captured live sequence. On all816 HTTP calls, rendering the **typed vLLM tool objects** reproduces the captured physical token sequence exactly. Token lengths, all text outside `<tools>`, tool JSON values and complete system/user message contents match in every case; physical lengths match reported prompt usage.

The source path is vLLM `online_renderer.py:180` (`tool.model_dump()` before templating). Its typed tool model emits `type,function`; its FunctionDefinition emits `name,description,parameters`. Frozen raw JSON instead orders `function,type` and `description,name,parameters`. CPU qualification validates a deepcopy but then templates the original raw dict; it therefore froze the wrong **physical serialization**, despite equivalent tool values. Original flags and captured IDs are preserved. Runtime input-isolation conclusions here rely on the audited physical sequences and exact message comparisons, not a waived flag.

An initial analysis itself passed raw request dictionaries into Pydantic, whose validator inserts `tool_choice=auto` in memory; that produced a spurious36/72 replay-request equality count. `AUDIT_V2.json` reruns using copies and establishes72/72; raw files were never modified. `AUDIT.json` and its manifest are retained as superseded analysis evidence. All scientific scores and prompt-serialization findings are unchanged.

## Template12 and cost

B's probe and training templates both produce **0/6 valid64 arrays**, without truncation. Probe lengths60/58/62/57/62/58; training60/58/61/57/62/58. Replaying the original training tool-key order therefore does not rescue cardinality on these six contexts. This isolated HF comparison is not identical to the service's broader typed-tool reserialization.

Suite600 totals:660,734 logical prompt tokens,572,208 reported cached tokens,88,526 uncached and84,612 completion tokens. Every scope72 run uses148,560 logical and105,264 cached prompt tokens; old first/replay/original completions5,592/5,588/10,521. All816 HTTP calls total1,106,414 logical prompt,888,000 cached and106,313 completion tokens. Template12 separately totals16,114 logical prompt and2,992 completion tokens,132.26s including model loading; batch wall time is shared, not additive per row. These are observed logical/accounting costs, not precise FLOPs or uncached-prefill GPU time.

## Action

The original-weight contrast has answered the immediate question: failure predates old SFT. Prioritize a small paired requested-ID/indexed-output comparison (same target16/full64 versus local16, same representation) or supervised requested-ID routing over further free-array cardinality-only fixes. Keep coverage, aligned semantics, count cancellation and repeated-question structure separate. Do not extrapolate these inspected validation effects to novel long-context tasks.

Authoritative machine evidence: `AUDIT_V2.json` and `INPUT_MANIFEST_V2.json` (826 read inputs, raw scores/requests/physical hashes and per-coordinate posthoc checks), plus `SUPPLEMENT.json` and `SUPPLEMENT_INPUT_MANIFEST.json` for original72, source locations, exact four-adapter disk checks and question-group overlap. Original runs, old flags and scores remain untouched. The systematic-debugging workflow mattered here: it located actual tool serialization drift and an in-memory analysis mutation instead of simply repairing false flags.
