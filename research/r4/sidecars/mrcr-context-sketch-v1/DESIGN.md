# MRCR context-sketch ablation v1

Status: approved design, 2026-09-02 UTC.

## Question and evidence boundary

This sidecar asks whether a small deterministic map of a long input helps the exact same frozen
`Qwen/Qwen3.5-4B` policy inspect and decompose that input inside an RLM. The causal comparison is
paired vanilla file-backed RLM versus the same RLM plus the map. A one-call direct full-context arm
is an external reference, not a compute-matched control. This is an inference ablation, not an RLM
paper reproduction and not evidence about training.

Engineering fixtures exercise software only and are always marked
`research_evidence_eligible=false`. Sidecar preparation performs no inference, opens no port, and
does not mutate the model cache, official evaluator clone, RLM repository, or a shared environment.

## Frozen inputs

- Model: `Qwen/Qwen3.5-4B` at Hugging Face revision
  `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, Apache-2.0, from the complete local snapshot at
  `/project/alex_phd/research-cache/models/Qwen--Qwen3.5-4B--851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`.
  Its local research manifest binds every weight and tokenizer byte. The tokenizer JSON SHA-256 is
  `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42`; the chat-template SHA-256
  is `a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715`.
- 2-needle band: official MRCRv2.1 file
  `mrcr_v2p1_2needle_in_(32768,65536)_dynamic_fewshot_text_style_fast.csv`, SHA-256
  `db030da739e427139541debbab7cfee591690942d9a69a6973d7c71395f2ab00`, 37,975,202 bytes and
  121 rows.
- 8-needle band: official MRCRv2.1 file
  `mrcr_v2p1_8needle_in_(65536,131072)_dynamic_fewshot_text_style_fast.csv`, SHA-256
  `f64e725bc06e24b44a21495f51adbe09ffee4a17974487f6ba1387a2b9de1ddc`, 62,464,356 bytes and
  103 rows.
- Official evaluator: Google DeepMind `eval_hub` commit
  `67b7fd29b2205ee0a3226e0d3e5d74140a253b42`; `run_evaluation.py` SHA-256
  `8d96a13b7876ee761d58f1dc1f0d697fe7e9c4d3fe6085ad6b097a29f597a7cb`.
- RLM runtime: repository commit `3aeb99d2a6ff125868f0329bfea584de84c1f715`. Its model-facing
  prompt, engine, executor, CLI, and server bytes are sealed separately because the research server
  must run those exact bytes.

Despite their interval names, the released rows are pointwise near each interval's upper boundary:
the selected files report roughly 65,272 and 130,872 Gemini tokens. We retain the official band
names and report both official and Qwen-tokenizer counts rather than implying uniform length within
the intervals.

## Deterministic paired sample

Each source row receives a content ID from canonical JSON of every CSV field. Within each band,
rows are stratified by the quartile of the normalized start of the official answer position. Rows
inside a stratum are ordered by
`SHA256("mrcr-context-sketch-v1|" + band + "|" + row_id)`, then source index. Each of four strata
contributes its first two rows to calibration and next four to confirmation: eight calibration and
16 confirmatory rows per band, 48 rows total. The sealed sample plan contains IDs, hashes, source
indices, band, reported context length, needle count, normalized position, rank, and split, but no
answer text.

Calibration can reveal operational failures and whether opportunity caps are feasible. It cannot
change the sketch, prompts, model, decoding, scorer, sample, budgets, or primary analysis.
Confirmatory execution requires calibration completion and an explicit `--confirm` flag.

## Context and treatment

For each row, preparation verifies that `view_ops` is the exact suffix of `queries`, removes that
suffix, and writes the remaining context body once as `workspaces/contexts/<row_id>.txt`. Both RLM
arms receive the same relative path, final question, system policy, model request, decoding, and
caps. Their only model-visible difference is the treatment block.

The vanilla prompt states that the long conversation is in the named file and asks the controller
to use Python to inspect it before returning only the requested answer. It prescribes no search or
decomposition plan. The sketch arm inserts one bounded `CONTEXT_SKETCH_V1` block before the same
final question.

`build_context_sketch(context_body: str) -> str` is intentionally unable to accept row metadata,
the final task, or the answer. It reports UTF-8 bytes, characters, lines, turn/delimiter counts,
basic task-blind lexical frequencies, and nine fixed-position character samples. Output is
deterministic and at most 4,096 UTF-8 bytes. Tests prove that changing `view_ops`, answer, row ID,
or other metadata while holding the context fixed cannot change a byte of the sketch. The attempt
records actual sketch bytes and SHA-256. Fixed-position samples can coincidentally overlap useful
text, but their positions and contents never depend on the question or gold answer.

Across the sealed 48-row sample, actual sketches are 2,249 bytes for every selected 8-needle row
and 2,270 bytes for every selected 2-needle row. These observed sizes are reported alongside the
4,096-byte hard ceiling.

The direct reference sends the original full `queries` value exactly to the upstream Responses
endpoint. It never receives a context sketch or file path.

## Opportunity caps and request identity

Vanilla and sketch use identical ceilings enforced by the RLM server and independently audited by
the runner:

- eight total model calls;
- 2,048 generated tokens per call, hence at most 16,384 generated tokens;
- 262,144 total reported tokens, which also upper-bounds cumulative context tokens;
- 600 seconds wall time;
- eight controller turns, six subcalls, recursion depth one.

The direct reference makes one call with `max_output_tokens=8192` and a 600-second wall timeout.
Its actual use is reported, but it is not described as matched. All arms use temperature zero and
the same served model identity. Requests are hashed before dispatch.

An endpoint descriptor binds the two loopback Responses URLs, served model, API-key environment
variable names, vLLM version and exact launch command, model and tokenizer manifests, maximum model
length, tensor-parallel topology, RLM launch command, working and trace directories, RLM commit and
source-byte manifest, controller options, limits, and launch-attestation SHA-256. Every research
command requires both the descriptor path and its expected SHA-256. Descriptor drift, non-loopback
URLs, mismatched attempt paths, model identity drift, or missing RLM attestation fields fail closed.
Preparation never probes the endpoints.

## Scoring and analysis

The sidecar ports the official `mrcr_v2_metric` byte-for-byte in behavior: predictions without the
target's 12-character prefix score zero; otherwise the last occurrence of the prefix selects the
prediction suffix and Python `difflib.SequenceMatcher` supplies the score in `[0,1]`. Tests extract
the function from the pinned official source and compare golden and adversarial cases. The official
source hash is authenticated before research execution.

The primary endpoint is the mean paired confirmatory difference
`official_score(sketch) - official_score(vanilla)` over all 32 confirmatory rows. A deterministic
paired bootstrap reports a percentile interval as descriptive uncertainty, not a standalone proof
of significance. The direct arm is summarized separately.

Secondary summaries include band and answer-position-stratum effects, exact-match rate, failures,
wall time, model calls, generated/input/cached tokens, controller turns, sketch bytes, score per
1,000 generated and input tokens, and empirical Pareto dominance. Failed, timed-out, malformed,
trace-missing, and cap-violating attempts remain in denominators with score zero. Raw paired rows
and trajectories are retained for later SFT/RLVR design; a positive score change without changed
inspection behavior is not automatically interpreted as improved decomposition.

## Durable attempt and resume semantics

`prepare` authenticates immutable inputs, creates a new attempt, writes its sample plan, context
files, arm order, request templates, and seal, then fsyncs them. Arm order rotates by paired-row
rank across `(direct, vanilla, sketch)` to reduce temporal confounding.

Each terminal task-arm result is one canonical JSONL record with a semantic ID, prior-record hash,
request/response hashes, usage, elapsed time, scorer output, RLM attestation and trace hashes,
status, and error. Append, flush, and fsync happen before progress advances. A content-addressed
checkpoint is written atomically after every terminal record and binds the ledger tail and complete
pair set. Resume validates the immutable seal, full hash chain, checkpoint, descriptor hash,
workspace hashes, and all existing terminal records; it skips only exact completed task-arm keys.
It never overwrites a response or trajectory. Duplicate keys, truncation, mutation, changed order,
stale checkpoint state, or a second fresh attempt at the same path fail closed.

## CPU validation and launch boundary

`preflight` checks every source hash, repository identity, model manifest, sealed sample, sketch
bound, scorer parity, sidecar manifest, and descriptor shape without making a network request.
`fixture` uses an in-process deterministic fake transport, synthetic non-MRCR records, and an
engineering-only output directory. It exercises all three arms, usage accounting, hash chaining,
checkpoint/resume, analysis, and fixture exclusion without opening a port.

CPU tests cover provenance drift; split stratification and disjointness; suffix parsing; sketch
determinism, leakage resistance, and byte bound; prompt treatment isolation; identical RLM caps;
direct-reference labeling; official scorer parity; descriptor SHA and loopback gates; token/cap
audits; trajectory binding; append-only recovery; idempotent resume; paired analysis; fixture
exclusion; and immutable-manifest verification. Ruff check and format check are required before the
manifest is sealed. No inference is launched while building this sidecar.
