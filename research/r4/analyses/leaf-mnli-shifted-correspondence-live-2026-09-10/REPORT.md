# Shifted requested-tag MNLI32 — independent audit

**Matching scores621/768 strict displayed labels (80.86%); shift17 scores0/768 because every shifted output fails the requested-tag contract.** All32 native outputs are available and complete shape-valid. The preregistered whole-contract-gated named-record diagnostic has **zero eligible endpoints/items** and therefore undefined accuracy—not0/522. This experiment exposes difficulty executing arbitrary requested-tag correspondence, but does not pass its gated mechanistic test.

## Primary and availability

|Arm|Available|Shape valid|Whole-contract valid|Strict correct /768|Shape-positional correct /768|Requested tags correct /768|
|---|---:|---:|---:|---:|---:|---:|
|Matching|16/16|16/16|16/16|621 (80.86%)|621 (80.86%)|768 (100%)|
|Shift17|16/16|16/16|0/16|0|277 (36.07%)|452 (58.85%)|

All32 HTTP200/native assistant branches authenticate, finish stop, no tools, no truncation or transport NULL. Planned-denominator, available-denominator and native bounds coincide. No batch has all48 labels correct. Primary requires the whole48-object array, unique object keys, exact tag then label fields, canonical strings and all requested tags in displayed order before counting displayed-record label correctness. No ID repair, permutation reversal, subset extraction or named-label score substitution.

All shifted outputs have missing/duplicate source IDs, although all emitted IDs belong to the context's source domain. None of768 shifted tags equals its displayed record's own ID;452 equal the requested tag and316 name some other source position. Thus this is not simply ignoring requested_tag and copying the own-ID field. Eight of16 shifted outputs correctly copy the first31 requested IDs; some then fail at the shift wraparound, others later. Telephone errors begin earlier. Per-position emitted source indices, expected tags and exact missing/duplicate lists are retained in DIAGNOSTICS.json.

## Paired eight-context results

Each table cell has96 planned items (48×two paired seeds). These are eight repeated-measure context clusters, not1536 independent item treatments or32 independent worlds.

|Context / genre|Matching strict|Shift strict|Shift shape-positional|Shift requested tags|
|---|---:|---:|---:|---:|
|0 government|80|0|36|62|
|1 government|80|0|40|86|
|2 slate|76|0|33|50|
|3 slate|70|0|41|62|
|4 telephone|72|0|36|30|
|5 telephone|71|0|33|10|
|6 travel|92|0|36|64|
|7 travel|80|0|22|88|

Matching−shift mean context strict difference+80.86points; positive8/8 contexts and16/16 repeated seed pairs. Shape-positional difference+44.79points, also positive8/8. Those descriptive contrasts do not identify why arbitrary remapping fails. Only two contexts/genre, no population genre claims.

## Named-record diagnostic: gate preserved

Data-only differing-gold subset: displayed label differs from label of record named by the **requested** tag. Counts per unique context34,29,30,34,34,34,31,35:261 unique positions,522 across two seeds. This subset froze before response inspection. Because all16 shift outputs fail the whole requested-tag contract, **all522 planned diagnostic items are excluded by the predeclared gate**; this is contract failure, not missing transport. Gated displayed/named/third-label fractions are undefined, and the producer's zero numerator/zero denominator is not zero accuracy.

Separately labeled **post-hoc, ungated shape-only exploration** on those same522 positions:305 predictions match the requested-named record label (58.43%),111 match the displayed record label (21.26%),106 match the third label (20.31%). No answer or output is changed. These counts are not the predeclared gated diagnostic and must not be promoted as its successful result. They suggest label/name interference worth isolating, but entail simultaneous tag-contract failures; they do not prove an internal mechanism or determine which record a malformed output actually intended to classify.

## Exact source, timing and native controls

Auditor did not implement question_cards' shifted study. Method froze1789002283.371114,177.976s after command1789002105.394874, with24 result files already present and no response content read by this auditor. Parser sealed1789002499.752998 **after terminal notification**, with all32 results present, still before response inspection. Honest description: method/parser were outcome-blind to auditor, not pre-generation; parser preparation was post-terminal. Four focused fixtures verify displayed versus named scoring, whole-tag gate and no partial-array rescue. Frozen method/parser and source pins remain unchanged.

Authoritative READY_V2 SHA`bdbd0bb85ea46dda085912131b285c4e939de48e09cd147594f7eb2a6db9ef4b`; first READY was superseded for wrapper binding before model work, and remains preserved. V2 changes the qualified service namespace, not scientific inputs/scoring. All32 actual ordered request bodies and hashes equal frozen inputs; native prompt IDs independently re-render, completion tokens exactly decode to actual final text, and usage lengths match. Actual model/service/preflight agree: released Qwen3-4B-Instruct-2507 revision`cdbee75f17c01a7cc42f958dc650907174af0554`, no adapter/LoRA,BF16,8192ctx,prefix-cache off,four sequences,vLLM0.28.0. Sampling3072 cap,.5/top-p1,no thinking,no tools; fresh paired seeds981532101–116. All producer primary, shape, tag and gated-diagnostic scores agree with the independent checker.

The new common prompt explicitly says to classify the displayed hypothesis/premise and copy requested_tag. Matching uses own ID; shift17 uses ID[(i+17)%48]. Independently verified complete texts/order/domain and identical tag multiset, common prompt/envelope/grammar; only requested_tag values differ within a pair. Generic grammar enforces48 objects, fields and label vocabulary with generic m+12hex tags, never source IDs or gold. Initial token totals are equal across arms in this panel; this does not establish equal FLOPs. The requested_tag field/common prompt is new relative to MNLI80, so that historical result is not a contemporary control.

The eight contexts are **already research-exposed MNLI80 inputs**, not fresh source replication. The previous independent cached-parquet/source audit was reexecuted: exact revision`da70db2af9d09693783c3320c4249840212ee221`, parquet SHA`350c26950b55f460b50d36c76aef87d64b49c78812d7abf7bf97e5fede10f186`, numeric mapping0 entailment/1 neutral/2 contradiction,384 full pairs/128 disjoint premises, public text-derived IDs, hidden original IDs/genre/gold/parses. Prior115-input exact-text receipt and mixed/OANC licensing scope remain disclosed; neither implies global/pretraining unseen data. No source selection or resampling after outcomes.

## Cost and decision

|Arm|Attempts / returned|Observed input|Observed output|
|---|---:|---:|---:|
|Matching|16/16|60,644|15,340|
|Shift17|16/16|60,644|15,331|
|Total|32/32|121,288|30,671|

All usage known; cache0/uncached121,288. No retries/tools/acquisitions or hypothetical costs. Billing unknown/not measured. Collector181.3923s,owner218.8389s,outer221.6524s,exit0/no timeout/released/GPU PID inventory empty. Host native preparation is separately pinned in CPU_NATIVE.json, not model work. Owner SHA`6d7cb2d3fdf5dc9caca4378cde789ab549f6c9f274f922dfaceb794ae3fe0659`.

The smallest useful follow-up would isolate whether the conflict comes from a requested tag naming **another visible source record**, versus arbitrary unique labels not naming any record, while keeping the common displayed-label contract and full correspondence checks. Alternatively test a shorter remapping task before interpreting labels under failed48-item correspondence. This is a design suggestion, not authorization to implement or relax existing scores. Avoid declaring the same-diversity experiment a clean successful named-record mechanism test; its predeclared gate never opens.

AUDIT.json preserves strict scores; DIAGNOSTICS.json explicitly labels post-hoc ungated exploration and per-position mappings; INVENTORY.tsv/OUTCOME_PINS.json/FINAL.json retain every coordinate, source and cost. No original source, campaign, reward or historical seal changed.
