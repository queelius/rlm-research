# Move the reminder, not the record

Design-only recommendation,2026-09-09. No implementation, study freeze, GPU/model calls or cue96 outcome inspection. MAIN chooses the new study before preparation. The brainstorming skill is being used to compare bounded options and retain the implementation approval boundary.

## Recommendation and alternatives

Prefer **192 calls: four anchor phases × matching/constant cue ×12 exact exposed contexts ×two fresh seeds**, keeping source record order and the entire model prompt fixed. This closes the most immediate gap in the old distance profile: different distances previously contained different records. Here, the same record is observed with each distance to the most recent anchor. Keep tag-before-label fixed; do not cross in another cue-order factor or another model.

| Option | Calls | What it identifies | Main limitation |
|---|---:|---|---|
| Preferred: all four phases, matching/constant, two seeds |192|Within-record matching-minus-constant profile at distances0–3, replicated over two sampling seeds within each context|More cost; phase changes the entire earlier output history, not just one local attention cue|
| Cheaper: same grid, one fresh seed |96|The same complete within-record distance profile on all12 contexts|No second sampling repeat; a narrower screen, not a two-seed replication|
| Reduced phases0/2, two seeds |96|Within-record distance0↔2 or1↔3 comparisons, depending on record position|Each record sees only two distances; cannot reconstruct the requested full within-record0–3 profile, so not preferred|

The192-call option is small enough relative to observed cadence4 costs to favor the stronger complete grid. If allocation pressure requires96, choose the single-seed full-phase version explicitly before outcomes; do not run half the preferred plan and rename its surviving cells.

## Inputs, weights and exact phase rule

Reuse exactly the12 contexts in `sidecars/leaf-sparse-anchor-v1/DATA.json`, SHA256 `dc105fbb5a07703f79f09ac2af4394d5e529b77be64bce452882c36e5edcdb81`: four TREC, four SST-2, four AG News,64 records/context, unchanged source IDs/text/permutation/gold lineage. These are exposed diagnostic contexts, not new holdouts; inherited unknown-license and pretraining-exposure limitations remain. No context, record, phase or label selection from new outcomes, and no pooling with old calls.

Fixed learned child alias `strict-rlm-qwen3-4b-role-sft-selected-v1`, adapter c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3; config ec773bc3b9de58af98a7c4dce9a40af795a4d05cd47284dbbfb27eac99b74174; Qwen3-4B-Instruct-2507 base revision cdbee75f17c01a7cc42f958dc650907174af0554. This is the existing learned child, unlike the completed released-model144 experiment. Do not choose a model based on cue96 or later RL outcomes.

Proposed master981308001, sampling seeds981308011/981308021. These are proposed values, not yet collision-checked or reserved; CPU preparation must check the small frozen campaign/spec/ready/seed/input-plan manifests and bind that evidence before READY. Seed sharing is variance-reduction intent, not deterministic counterfactual trajectories.

For zero-based displayed position i=0..63 and phase p=0..3, position i is an anchor exactly when `i % 4 == p`. The four one-based anchor lists are:

- phase0:1,5,9,…,61;
- phase1:2,6,10,…,62;
- phase2:3,7,11,…,63;
- phase3:4,8,12,…,64.

Every call has exactly16 anchor objects and48 plain label strings. At anchors, ordered object keys are `tag` then `label`. Matching tag is that displayed record's exact source ID; constant is literal `p0000`. At nonanchors, output is only a canonical label string. Same fixed64-item strict native JSON grammar, vocabulary and max output allowance apply to all conditions. No extra leading/trailing marker, synthetic record, ring wraparound or repeated source text is introduced.

## Fixed prompt, changing schema only

The old sparse prompt enumerates anchor positions. Reusing that wording would violate the requested fixed-prompt condition. Instead use this single neutral instruction in all eight phase×cue conditions, retaining the original task-definition, allowed-label and public input sections byte-for-byte:

> Return only a JSON array in displayed input order, exactly one item per input record. Follow the required output format at each position. At object positions emit exactly the keys tag then label; the output format fixes the tag value. Set label to that displayed record's canonical label. At string positions emit only that displayed record's canonical label, not an object. Do not omit any input record.

Do not enumerate phases/anchor positions or separately instruct matching versus constant in the prompt. The actual structured-output schema supplies both the object/string position schedule and tag constants. For record4 with source ID q1234, phase3 matching emits `{"tag":"q1234","label":"location"}` at that record; phase3 constant emits `{"tag":"p0000","label":"location"}`; the same record is a plain `"location"` string in the other phases. “location” here is only a readable example, not an outcome or task-specific supplied answer.

The intervention deliberately changes effective allowed output actions and the resulting autoregressive prefix. It is not harmless wording. Exact prompt, input order, system, tools, source IDs/text, task definitions, sampling and alias are common across all eight conditions; ordered `structured_outputs.json.prefixItems` is the only request-body difference within a context/seed. The sampling seed differs across the two predeclared repeats. Check equality mechanically rather than assuming the schema is absent from physical prompt serialization.

## Boundary handling and primary estimand

Distance is the number of displayed records since the most recent anchor, including the current position: d=0 at an anchor. For i>=p, `d=(i-p)%4`; for i<p, no anchor has yet appeared, so preceding-anchor distance is **undefined**, not modulo-wrapped from a nonexistent earlier block.

Positions1–3 lack a preceding anchor in some phases. Retain them in every whole-array/overall accuracy denominator and report them as boundary diagnostics, but exclude these same three positions from **all phases** of the primary within-record contrast. The common core is positions4–64,61 records/context. Each of these records has exactly one phase at each distance0,1,2,3. This shared61-record core avoids changing semantic support with distance. Position64 is allowed: its phase3 anchor has no successor, but that record still has valid preceding anchors and all four distances across phases.

Let Y(c,s,i,p,a) be strict position correctness for context c, seed s, core record i, phase p and arm a. A completed schema-invalid array contributes0 at all64 positions; an unavailable/provenance-invalid call contributes NULL, not0. For each distance d choose the unique phase `p=(i-d)%4` and define within-record cue advantage:

`A(c,s,i,d) = Y(c,s,i,p,matching) − Y(c,s,i,p,constant)`.

The proposed primary directional contrast is **A(d0)−A(d3)>0**: does the matching cue's advantage for the same record weaken by three following positions? Average first over the fixed61 records, then the two paired seeds within each context; report four context means separately per task and their mean. No label-level independence claim. Report the complete0–3 profile and underlying arm accuracies regardless of whether the primary direction holds. Secondary: adjacent differences and a linear-distance descriptive trend, without choosing the best contrast after seeing data.

For a primary context/seed core, require the full eight phase×arm calls to be observable; otherwise its paired primary is NULL. For a primary two-seed context mean, require both complete seed blocks. Keep all24 planned blocks and12 context means visible; do not reweight by surviving phases or records. Available-call/available-pair descriptives may be shown separately with exact support. Whole-array64 correctness, total strict assignments, per-phase accuracy/format errors, labels/confusions, count-vector L1, output length and first-anchor/pre-first-anchor/last-anchor boundaries remain secondary diagnostics. A key-order flag describing only a parsed prefix is not a full-schema validity proof.

## Minimal source/API seam and CPU qualification

Reuse the qualified component collector, native chat-completions token capture, owned service lifecycle and strict parser contracts. No recursive root, helper uptake, generated program execution, invented logprob or training export is needed.

`leaf-sparse-anchor-v1/study.py` SHA2728361c0f6b12dc887d6e171cc1f12941380428ab983ad18403e7d47ea0faa9 supplies exact source records and existing mixed object/string request/scoring structure. In a new private module, replace the anchor predicate in request construction, synthetic fixtures and scoring with the same declared phase predicate. Use a new common instruction instead of its anchor-position enumeration. Do not mutate/import-modify frozen source globals. The eventual script must join displayed gold by actual record ID/position, never silently shift predictions.

`leaf-sparse-cue-order-v1/driver.py` SHA5b9188810b041e79240ae9c9243d7ee11a4b04494ab31de15d23658c6e2ce357 is a qualified source-only reference for exact ordered schema compilation, typed native prompt hashing and grouped collector cancellation settlement. Its outcomes are neither needed nor inspected. Its underlying individual-row collector was privately adapted for quadruples; the new study needs only a counted grouping delta to eight-call units, not a scheduler framework. Authentication must state actual inherited semantics rather than inventing historical pairing.

CPU tests before READY, without a GPU service:

1. For every64-record context and all four phases, assert16 objects/48 strings, exact assigned key order/tag constants, and complete within-record phase↔distance bijection on positions4–64; pre-first-anchor distances remain undefined. Compile the60 distinct expected schemas (48 matching context×phase plus12 constant task×phase), accept complete fixtures and reject wrong-phase types, late wrong tags, duplicate/extra/missing keys, noncanonical labels and short/long arrays. If actual schema identities give a different deduplication count, resolve it explicitly before freeze rather than forcing that number.
2. Qualify the exact native renderer: all eight requests/context/seed must have byte-identical messages/system/tools, full physical prompt-token vectors and equal prompt lengths. Verify structured grammar is the only request-body difference and preserves insertion order; gold never enters public input. Tag tokenization and16-anchor cardinality do not guarantee equal actual output lengths or compute.
3. Exercise actual eight-call dispatch with a fake HTTP provider: no concurrent requests within a unit, all192 unique coordinates exactly once, at most four units active, and cancellation writes settled before STATUS counts. No model call, arbitrary source execution or broad test suite.

## Schedule, physical cost and stop rules

Use24 context×seed work units, eight conditions sequentially within each and at most four units concurrently. Freeze an eight-condition Williams order: encode conditions as phase0M,phase0C,phase1M,phase1C,phase2M,phase2C,phase3M,phase3C; base sequence indices `[0,1,7,2,6,3,5,4]`, then cyclically add k modulo8. Assign `k=(context_index*2+repeat)%8`. Each task's four contexts×two repeats receives all eight sequences once; all24 units give three occurrences/sequence overall. Master-seeded context-unit dispatch ordering is frozen before inference. This balances assigned position/carryover; it does not make concurrent timing or sampled prefixes identical. Log actual request start/finish times and nominal order.

Observed sparse144 cadence4 work was264.1007 summed call-seconds for48 calls at concurrency4. Scaling only that component suggests192 calls need roughly264 seconds of overlapped collection, plus startup/grammar overhead; this is a rough planning estimate, not guaranteed performance or an architecture comparison. New common prompts/phase schedules may change cache reuse, compilation and output behavior.

Propose **600s cumulative collection,750s shared work,870s inclusive owned with120s cleanup,900s outer**. This fits the requested900-second candidate envelope, retains roughly twofold nominal collection margin and normal owned cleanup. One fixed c32 service; startup bounded by the unchanged qualified startup allowance and remaining750-second work deadline. Collection uses `min(start+600,work_deadline)`, no phase reset. If setup is unusually slow, remaining coordinates become declared NULLs; do not increase the cap or reroll. There is no extra study API retry/replacement call. Preserve raw errors and unsuccessful/canceled/unrun coordinates separately.

Record all192 physical attempts/planned slots, full raw prompts/responses/output token IDs, actual aliases, strict grammar validity, raw usage cached/uncached counters, output tokens, stop reasons and overlapping wall/call durations. Keep the qualified service's cache policy unchanged and record its actual config/counters. Equal source text and object counts do not establish equal realized compute; no accuracy-per-token claim that ignores invalid/null work. Compare phase/cue costs and jointly observed/valid costs separately; count no shared execution twice because all192 are distinct calls.

## Interpretation and decision

A positive, context-consistent within-record decay contrast would show that the correspondence benefit depends on where reminders fall relative to the same records under this constrained generation package. It reduces the old “anchors happened to be easier examples” explanation. It does **not** isolate attention, establish a particular hidden-state mechanism, or eliminate prior-label/prefix/history effects: changing phase changes earlier sampled outputs and object/string action positions. The matching tag contains a source ID whereas constant does not; grammar and output syntax remain part of the intervention. No general adaptive planning or whole-RLM claim is supported.

A flat/inconsistent within-record curve despite a positive overall matching advantage weakens a simple local-decay account; it is not equivalence proof. Effects driven by schema failure or sample availability must be identified rather than renamed semantic gains. A stronger generalization study or released-model replication would be a separately frozen follow-up, not an extra factor added here.

Evidence used: independently sealed sparse144 REPORT SHA316683e51faa4d19cb789f992c67fe20a2788d58ec1af3f2c68fc5d66a207ae9 and its cadence4 costs; newly sealed released-model144 REPORT SHAf9dbe12e9fc85d3491f77199344c958aa05379eb726a9e81063122d2e46cbf0a establishes analogous matching benefits without research adapters. No cue96 outcomes, new model runs or implementation actions informed this proposal.
