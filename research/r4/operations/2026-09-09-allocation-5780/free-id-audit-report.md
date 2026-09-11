# Independent free-ID attempt003 audit

## Decision

Exact grammar makes all 48 outputs contract-valid; free decoding makes only 4/48 valid. Source-ID matching remains the strongest arm under exact decoding, but this experiment does **not** isolate a need for ID-copy grammar: 35/48 free outputs pursue the advertised Python tool, and another nine generate overlong arrays. Four successful free matching outputs copy all IDs in order without defects. Prioritize a final-only leaf interface calibration, then distinguish cardinality/shape constraints from literal-ID constraints. Do not blindly raise caps or train only more terminal answers.

This is a newly executed comparison on an already exposed panel and the original two seeds, not fresh-data replication. AGnews uses cached **test** rows; SST2 uses cached **train** rows. There are four independent context groups per dataset, two repeated seeds per context, not 512 independent experimental replications per cell.

## Primary endpoint

V2 strict correct labels / 512 planned labels per cell. A complete malformed, wrong-cardinality, wrong-ID, wrong-field-order or tool-call output scores zero, never infrastructure NULL. No labels are reordered by IDs. Parentheses give fully contract-valid calls / 8.

| Dataset | Arm | Free | Exact |
|---|---|---:|---:|
| AGnews | Plain | 0 (0/8) | 188, 36.72% (8/8) |
| AGnews | Source-ID matching | 216, 42.19% (4/8) | 418, 81.64% (8/8) |
| AGnews | Constant tag | 0 (0/8) | 173, 33.79% (8/8) |
| SST2 | Plain | 0 (0/8) | 307, 59.96% (8/8) |
| SST2 | Source-ID matching | 0 (0/8) | 468, 91.41% (8/8) |
| SST2 | Constant tag | 0 (0/8) | 314, 61.33% (8/8) |

All 96 HTTP responses completed with authenticated captures; zero infrastructure missing, request errors or unknown-usage calls. Thus every primary lower/upper bound is exactly the reported numerator. Full-shape and full-contract validity coincide on these actual outputs. Conditional positional accuracy is 216/256 (84.38%) for the four free matching successes; it is not 84.38% on the planned denominator. All other free cells have **undefined** conditional positional accuracy, not observed zero semantic accuracy. Exact cells have all labels aligned and their conditional accuracy equals the table.

Independent scoring agrees with the recorded V2 score on all 96 calls, including predictions, bounds, field order and validity. Neither literal tool wrappers nor prefix arrays were repaired into primary answers.

## Paired context evidence

Each entry below is correct labels / 128 planned labels, summing both original seeds. Columns P/M/C are plain / matching / constant. This keeps the four context clusters visible.

| Context | Free P/M/C | Exact P/M/C |
|---|---|---|
| AGnews 0 | 0 / 106 / 0 | 52 / 106 / 43 |
| AGnews 1 | 0 / 110 / 0 | 53 / 110 / 45 |
| AGnews 2 | 0 / 0 / 0 | 38 / 101 / 38 |
| AGnews 3 | 0 / 0 / 0 | 45 / 101 / 47 |
| SST2 0 | 0 / 0 / 0 | 82 / 116 / 83 |
| SST2 1 | 0 / 0 / 0 | 73 / 124 / 81 |
| SST2 2 | 0 / 0 / 0 | 77 / 112 / 72 |
| SST2 3 | 0 / 0 / 0 | 75 / 116 / 78 |

Exact matching exceeds both controls in every context. Its advantage over plain is +44.92 percentage points on AGnews and +31.45 on SST2; over constant, +47.85 and +30.08 points. These are descriptive exposed-panel contrasts. Constant tagging controls object serialization imperfectly: repeating one tag is not the same output/correspondence burden as copying 64 distinct source IDs. The four successful free/exact matching pairs have equal correct counts; success is clustered entirely in AGnews contexts 0–1. No independent-record significance test is warranted.

## Actual failure behavior and ID diagnostics

Free decoding: 27 length-capped outputs, 10 provider-parsed tool calls, seven additional stop outputs containing literal tool wrappers, four valid arrays. All 27 length outputs consumed exactly 3,072 tokens. The 44 invalid outputs comprise 35 tool-directed continuations (10 parsed, 25 literal wrappers including 18 truncated) and nine unfinished arrays. All 24 SST2 free outputs are tool-directed. The actual system prompt describes a coding agent with a persistent `ipython` tool, and every request advertises that tool. The single-call collector never executes it. Therefore these are completed interface failures, not service failures or a tested native multi-step tool trajectory.

The nine unfinished AGnews arrays already contain 139–1,022 complete items for 64 inputs. Constant arrays contain 139 or 179 repeated `p0000` objects; plain arrays contain 766–1,022 labels and end in repetitive World labels. All exceed the required cardinality before truncation. This is uncontrolled stopping/repetition, not evidence that 3,072 tokens are intrinsically insufficient for 64 answers. Complete prefix values are diagnostic only, with no repaired score.

All 20 complete matching arrays (16 exact, four free) have 64/64 literal positional ID matches, full source-set coverage, no missing IDs, no extra IDs, no duplicate IDs, and tag-before-label field order. All 16 complete constant arrays have 64/64 `p0000` tags and the required order. Repeated constant tags are intentional, not source-ID duplication errors. There are no complete-array order-only or ID-only failures in this run. ID-set diagnostics are undefined for tool programs and malformed wrappers; an apparent generated expression synthesizing IDs is not an executed emitted array.

Consequently, exact grammar here jointly constrains cardinality, stopping, canonical labels, object fields, literal IDs and the output route. It is not a clean literal-ID-only intervention, although paired bodies are otherwise identical.

## Native/source authenticity and availability

All 96 actual wire bodies equal the frozen ordered request bytes. All 48 free/exact within-arm pairs differ only by removal of `structured_outputs`; seed, prompt, tools and sampling parameters are identical. Exact schemas allow all canonical labels and constrain visible source IDs or the constant, not gold labels. All 512 displayed ID/text pairs match source records without privileged gold fields.

All 96 provider prompt-ID sequences equal both the frozen typed-render hashes and an independent CPU re-render using the actual vLLM request schema. A raw Hugging Face render without vLLM's typed tool normalization is not equivalent; the audit uses the typed schema, matching the service. All 96 output-token sequences decode exactly to the returned content or parsed tool-call envelope, with 69 non-length continuations ending in `<|im_end|>`. All usage counts equal captured token lengths; no reasoning output, execution or inference fallback was introduced.

Actual serving evidence binds Qwen3-4B-Instruct-2507 revision `cdbee75f17c01a7cc42f958dc650907174af0554`, no research adapter, BF16, LoRA disabled, prefix caching disabled, maximum model length 8,192, four sequences, Hermes tool parser, no reasoning parser. SERVER_READY, served alias, response aliases and physical model directory agree. Model-shard size/mtime/inode identities match the previously full-hashed pins; this audit does not claim a new full weight-byte hash. CPU native qualification used the existing prime environment, Transformers 5.6.2, with GPU visibility disabled.

All 512 gold labels and texts were independently joined to their cached parquet source rows; 512 normalized text groups are unique across the eight contexts. Current contexts equal the previously exposed leaf-fresh-correspondence data exactly. Dataset byte hashes and split provenance are in SOURCE_CHECK.json. Method was frozen before opening new response content; raw outcome files were pinned after verifying OWNER_TERMINAL, rollout STATUS and the parent's clean release. No source, earlier attempt, seal, GPU, service, queue or generated code was changed or executed.

## Cost and preserved failures

| Dataset / arm | Free prompt + completion | Exact prompt + completion |
|---|---:|---:|
| AGnews plain | 37,280 + 24,576 | 37,280 + 1,986 |
| AGnews matching | 37,464 + 17,072 | 37,464 + 9,874 |
| AGnews constant | 37,456 + 24,576 | 37,456 + 10,392 |
| SST2 plain | 16,080 + 20,424 | 16,080 + 2,205 |
| SST2 matching | 16,264 + 17,544 | 16,264 + 8,728 |
| SST2 constant | 16,256 + 17,161 | 16,256 + 8,753 |

Attempt003 paid 96 calls: **321,600 prompt + 163,291 completion = 484,891 total tokens**, all known; cached and created-cache tokens are zero on all calls. Free totals 282,153 tokens; exact totals 202,738. Collection wall time 989.087 s; scientific owner 1,065.648 s; parent job 1,075.801 s (whole parent 1,075.874 s). These are overlapping wall clocks, not additive GPU-seconds or a measured utilization integral. No training, map acquisition or child executions occurred; prior data/preparation cost is reused and not falsely counted as new generation.

Preserved attempts001/002 have zero call artifacts and no model-outcome denominator. Attempt001 owner failed at launch after 0.726 s; attempt002 failed the collector namespace check after service startup, 39.689 s. Both report released and remain intact. Their 40.415 s combined owner elapsed is additional failed-attempt overhead, not silently absorbed into successful scientific outcomes. Exact historical GPU-active time and monetary cost are unavailable; do not report them as zero.

## Ranked follow-ups

1. Calibrate a matched final-only leaf contract with no advertised/executable tools, comparing free versus exact decoding across the same three serialization arms on newly frozen disjoint contexts and fresh paired seeds. This directly tests whether tool affordance and uncontrolled stopping explain the free collapse. Keep native typed rendering and planned-denominator scoring.
2. Under that calibrated interface, compare shape/cardinality-only grammar, literal-ID grammar and free decoding. This separates stopping/canonical-format support from forced correspondence; preserve distinct-ID versus constant controls and report semantic accuracy separately from validity.
3. If source correspondence survives, train on genuinely disjoint contexts using complete source-ID/label arrays with explicit final termination. Randomize IDs, displayed order, batch size and label vocabulary; include appropriate final-only/tool-use routing examples rather than merely saturating terminal-token loss. Evaluate free-decoding validity, ID fidelity, semantic accuracy and transfer to held-out tasks independently.

Do not use this single exposed panel to claim a general root/leaf capability ceiling, a pure ID-copying mechanism, or that increasing epochs/caps will solve the observed behavior.

## Artifacts

METHOD_READY.json freezes the outcome-blind method and source/test pins. OUTCOME_PINS.json freezes 226 terminal/raw JSON files. AUDIT.json contains all 96 independent scores, 48 paired contrasts, context aggregates, complete responses and costs. DETAILS.json contains exact CPU-native qualification and unrepaired failure-prefix diagnostics. SOURCE_CHECK.json contains independent cached-row verification and safe serving flags. FINAL_MANIFEST.json seals this report, scripts, focused tests and external source dependencies. The operations copy is byte-identical to this report.
