# Released Qwen models: matching source IDs improve correspondence

The matching-tag representation beats the constant-tag representation in **all48 paired context/seed comparisons**, across both released models and all three tasks. All24 two-seed context means are positive. This effect is present without the research adapters; it is not unique to the learned c32de child. The result concerns the entire supplied instruction/schema/output-prefix package on12 exposed contexts, not an attention mechanism or an end-to-end RLM gain.

Both model stages completed and released their owned services. All144 planned calls are observable and physically authenticated; NULL0.143 responses satisfy the full primary schema, one is a real length-truncated invalid response scored0. No whole64 array is entirely correct. Independent endpoints agree with stored scores in all144 cases.

## Primary and secondary outcomes

Every table entry is correct displayed-position labels out of512 planned:8 calls, four context clusters with two paired seeds. M−C is the prespecified primary contrast. Plain labels are secondary. Invalid completed arrays contribute0 rather than being omitted.

| Released model | Task | Plain | Matching source ID | Constant tag | M−C | M−C percentage points |
|---|---|---:|---:|---:|---:|---:|
| Qwen3-4B-Instruct-2507 | TREC |198|406|223|+183|+35.74|
| Qwen3-4B-Instruct-2507 | SST-2 |318|480|315|+165|+32.23|
| Qwen3-4B-Instruct-2507 | AG News |196|423|163|+260|+50.78|
| Qwen3.5-4B | TREC |167|397|143|+254|+49.61|
| Qwen3.5-4B | SST-2 |318|485|329|+156|+30.47|
| Qwen3.5-4B | AG News |191|438|183|+255|+49.80|

All cells have8 valid arrays except Qwen3.5/TREC/constant, which has7. Its eighth response stops at3072 output tokens with an incomplete JSON array followed by whitespace. Coordinate `c1f8b0fe9af2b074a1d26f3dafb1b341f74bef583b91c9946f173907b20e2cf1` is context2, seed981302021. It remains observed0, not NULL; no closing bracket, prefix recovery or semantic repair is added. Excluding that pair only as a separately labeled descriptive check, matching still wins all7 jointly valid TREC pairs by213 correct labels over448 paired positions. The primary254/512 remains unchanged.

The frozen primary checks exact key sets, expected displayed tags and canonical labels, while insertion order is a separate diagnostic. All95 valid tagged arrays have `tag,label` order at every item; all48 plain arrays are valid. The invalid array has no full-order validity inference. All143 successful completions stop normally; the one invalid stops for length. There is no reported reasoning content, no positive reasoning-token count, and no tool-call response. Ordinary described tools were not executed.

Each model/task has8 wins,0 ties,0 losses. Two-seed mean gains per context, in correct labels per64, are:

| Model/task | Four context means |
|---|---|
| Qwen3 TREC |20,27.5,21,23|
| Qwen3 SST-2 |23,13,24,22.5|
| Qwen3 AG News |33,35.5,29.5,32|
| Qwen3.5 TREC |22.5,39,34.5,31|
| Qwen3.5 SST-2 |20,14.5,20.5,23|
| Qwen3.5 AG News |27.5,29.5,36.5,34|

Both seed-specific aggregate contrasts are positive in every model/task. The six frozen arm orders rotate across context/repeat exactly as declared; nominal order/seed cells and all individual pairs are included in METRICS, not used to select a result. Repeated seeds are nested observations, not independent source clusters. No p-value treating9216 labels as independent trials is reported.

Qwen3.5−Qwen3 differences in the matching arm are−9 TREC,+5 SST-2,+15 AG News labels/512. Differences of M−C are+71,−9,−5 respectively, with the TREC difference partly incorporating the declared invalid0. This small exposed comparison does not establish overall model superiority or explain differences by architecture, training data, model family or parameter-count naming.

## Position and histogram diagnostics

Matching remains strong late in the array, whereas plain and constant often degrade after the first16 records. These quartile counts have128 planned positions per column (including invalid-array zeros):

| Model/task | Matching positions1–16 /17–32 /33–48 /49–64 | Constant same quartiles |
|---|---|---|
| Qwen3 TREC |104 /98 /100 /104|105 /47 /37 /34|
| Qwen3 SST-2 |122 /126 /114 /118|112 /62 /80 /61|
| Qwen3 AG News |106 /98 /110 /109|69 /24 /30 /40|
| Qwen3.5 TREC |93 /97 /107 /100|70 /29 /24 /20|
| Qwen3.5 SST-2 |119 /125 /120 /121|112 /77 /57 /83|
| Qwen3.5 AG News |109 /107 /110 /112|90 /32 /31 /30|

The Qwen3.5 TREC constant valid-only support is112 positions/quartile, with16 additional strict-zero positions from the invalid array. Full64-position profiles and class confusion counts are in METRICS/POSITION_LEDGER; these are descriptive, not newly selected endpoints.

Count histograms can be close while correspondence is poor. For Qwen3.5 SST-2, constant mean class-count L1 is6.25 yet only329/512 labels align correctly; matching has L1=3.25 and485/512 correct. Repeated labels and label imbalance permit near-right counts despite wrong record assignments. Mean L1 matching/constant: Qwen3 TREC11.5/55.5, SST4/25.75, AG10.25/42.5; Qwen3.5 TREC20.25/53.14 (constant7 valid), SST3.25/6.25, AG11/23.5. L1 is undefined for the incomplete array, not silently repaired or treated as zero.

## Physical costs and actual serving

All144 raw usage records include cached-token counters and all are0, consistent with actual prefix caching disabled. Prompt=uncached input throughout. Total450480 input and126646 output tokens. Sum of concurrent call durations is3942.36 seconds; this is not elapsed wall time.

| Model | Calls | Input / cached | Output | Startup | Collection |
|---|---:|---:|---:|---:|---:|
| Qwen3 |72|220434 /0|65888|38.02s|414.86s|
| Qwen3.5 |72|230046 /0|60758|148.06s|582.85s|

Owned scientific elapsed1269.344 seconds; outer job1270.107 seconds, exit0, below2640/2670 caps. Both300-second startup and900-second collection limits were met; global work deadline was not reset. The operation reports GPU processes empty after exit. Authenticated release records cover7 owned identities for Qwen3 and42 for Qwen3.5. The latter count is process provenance, not evidence of additional model calls. Actual service logs contain exactly72 successful component POSTs/model, all200; raw call and wire coordinates each cover the exact72, with no replacement retry observed.

Matching adds exactly one input token/call relative to constant under each native tokenizer. Output costs are not fixed across representations:

| Model/task | Matching input/output | Constant input/output |
|---|---:|---:|
| Qwen3 TREC |14930 /11546|14922 /10779|
| Qwen3 SST-2 |21858 /8728|21850 /8728|
| Qwen3 AG News |36882 /9582|36874 /10402|
| Qwen3.5 TREC |16044 /8648|16036 /10107|
| Qwen3.5 SST-2 |22922 /8216|22914 /8222|
| Qwen3.5 AG News |37908 /8813|37900 /8411|

The apparent Qwen3.5/TREC output saving includes the failed constant response consuming3072 tokens. On its7 jointly valid pairs, matching uses7452 output tokens versus7035 constant: no matched-success saving there. SUPPLEMENT preserves matched-valid costs for every cell. Plain emits much shorter outputs but performs poorly; no equal-realized-compute claim is made. Sequential wall times, different native templates/tokenizers and distinct runtime settings cannot identify architecture efficiency.

Actual BINDING, SERVER_START/READY, endpoint, inference config and live preflight model cards agree on:

- Qwen3-4B-Instruct-2507 revision `cdbee75f17c01a7cc42f958dc650907174af0554`, alias `Qwen3-4B-Instruct-2507-no-research-adapter`.
- Qwen3.5-4B revision `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, alias `Qwen3.5-4B-no-research-adapter`.

Both are released post-trained instruction checkpoints, not randomly initialized models or research SFT adapters. Both declare adapter=None, enable_lora=False and live model-card parent=None; BF16, eager,8192 context, four sequences, generation_config=vllm and vLLM0.28.0. Qwen3.5 has the declared language_model_only/align Mamba cache mode and qwen3/qwen3_coder parser settings; its successful actual GPU startup resolves this run's prospective compatibility risk, not arbitrary future hardware compatibility.

All144 actual request bytes and ordered hashes equal the frozen requests. Public input ID/text maps exactly reconstruct source record order; schema tags/labels/order constraints and sampling are checked independently. Actual complete prompt-token vectors hash to the frozen native rendered vectors and match usage lengths; returned output-token vector lengths also match usage. Cross-model requests are identical after alias removal, while native token vectors intentionally differ. Qwen3.5 uses its declared empty-think native suffix, Qwen3 its assistant prefix. This audit does not independently detokenize every output vector; it scores raw returned text and binds its enclosing response to the full recorded vectors.

## Provenance, scope and next decisions

METHOD and parser were sealed before outcomes. Nine independent parser tests pass again in0.003s, including reversed-key primary-versus-order separation, late invalid tag, malformed/empty0 versus unavailable NULL. One raw reconstruction pass created ROW_LEDGER/METRICS/POSITION_LEDGER; supplemental arithmetic uses that ledger rather than rescanning all raw calls. There were no audit-script failures or primary discrepancies.

The pre-outcome194 small-source authentication is cached, with every source actually consumed now hashed in SOURCES. Both current acquisition manifests, configs/tokenizer/template/index artifacts are checked against pinned hashes; all5 weight-shard size/mtime/inode identities match the prior pinned full-byte-hash observations. This is explicitly not a fresh independent multi-GB tensor scan. Exact manifests and per-file checks are in SUPPLEMENT. No credential value is printed or persisted in the analysis; inference files are hashed and only non-secret config fields are projected.

All12 contexts are previously exposed: four each TREC, SST-2 and AG News,64 records/context and256 unique groups/task. Exact record/gold lineage is rejoined through the source context coordinate and frozen source specifications; source group IDs, lines and positions are retained. TREC/SST provenance follows the prior correspondence data and AG follows the prior AG acquisition. Unknown-license qualifications remain in those sources; no new permission or pretraining-exclusion claim is made. These are not12 new holdouts. Auditor did not author this study's model/data/scorer, but contributed to common upstream harnesses, so independence is outcome reconstruction rather than an independently built inference stack.

Ranked small follow-ups, each requiring a new prospective plan rather than modifying this study:

1. **Within-record reminder phase control:** shift sparse cadence4 anchor phase while keeping source order fixed, so each record is observed at all cue distances. Matching versus constant, balanced phases and fresh seeds can distinguish a distance pattern from easier records happening to lie at anchors. A192-call candidate uses12 contexts×4 phases×2 arms×2 seeds; exact prompt/schema/boundary costs and cap should be checked before approval. This complements the already prepared cue-order study; no cue96 outcomes were inspected here. No attention-mechanism claim follows automatically.
2. **Released-model generalization:**96 calls=two pinned released models×three tasks×four newly declared contexts/task×two arms×two seeds. Freeze source splits/licensing and exclusions before outcomes. Based on current startup and call costs, roughly20 minutes with a30-minute inclusive cap is a plausible preparation target, not a throughput guarantee. This asks whether the correspondence benefit survives new source clusters, not whether Qwen3.5 is generally better.
3. **Narrow child integration:** a new matched whole-RLM screen can compare the same free root with released versus learned typed children on fixed public contracts and fresh seeds, with child source correspondence/coverage and final map-to-count fidelity separated. A16-episode two-child readout over four fixed global contexts and two seeds would test operational relevance; this component study alone cannot predict root uptake or aggregation success. Keep root weights fixed and avoid mixing this with the active ledger manipulation.

Files: REPORT.md, ROW_LEDGER.json, POSITION_LEDGER.json, METRICS.json, SOURCES.json, SUPPLEMENT.json and SUPPLEMENT_SOURCES.json, plus the sealed pre-outcome method/parser and audit source. SEAL binds their final hashes. No GPU/service action, source mutation, reroll, answer repair or policy selection occurred in this audit.
