# Queued leaf correspondence controls

CPU-prepared only. Parent owns the warm service and every live launch. Both jobs require the OLD selected child c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3; neither mixed-size A nor B is accepted.

## Parent launch

Set CORR_ENDPOINT to the actual endpoint descriptor for that loaded checkpoint. The historical role-service descriptor is used only by CPU tests and is not a default. Binding checks local base/adapter bytes; run checks live vLLM version and alias/root/base before dispatch. The descriptor must report local vLLM0.28.0, max_model_len at least8192, and inference_only=true. Its API key is read from the named environment variable, never written to artifacts.

```bash
CORR_DIR=/project/alex_phd/runs/rlm-research-r4/sidecars/leaf-correspondence-controls-v1
CORR_PY=/project/alex_phd/envs/prime-rl-5990b1b/bin/python
CORR_ENDPOINT=/PARENT/ACTUAL/old-selected-endpoint.json

CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 "$CORR_PY" "$CORR_DIR/driver.py" bind --comparison representation --endpoint-descriptor "$CORR_ENDPOINT" --spec-path "$CORR_DIR/BOUND-REPRESENTATION-attempt-001.json"
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 "$CORR_PY" "$CORR_DIR/driver.py" run --spec-path "$CORR_DIR/BOUND-REPRESENTATION-attempt-001.json" --output-dir "$CORR_DIR/outputs/representation-attempt-001"

CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 "$CORR_PY" "$CORR_DIR/driver.py" bind --comparison rotation --endpoint-descriptor "$CORR_ENDPOINT" --spec-path "$CORR_DIR/BOUND-ROTATION-attempt-001.json"
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 "$CORR_PY" "$CORR_DIR/driver.py" run --spec-path "$CORR_DIR/BOUND-ROTATION-attempt-001.json" --output-dir "$CORR_DIR/outputs/rotation-attempt-001"
```

Run sequentially unless the parent explicitly budgets eight combined workers. Each comparison has four workers, a five-minute wall cap including live preflight, a sixty-second request timeout, atomic per-call checkpoints, no retries, and a new output directory. A repeated bind/attempt refuses overwrites. Binding itself makes no server contact. A bound descriptor is not a declaration that a service is already live.

## Exact treatments

All arms retain CONTRACT.json's complete system message, IPython tool definition, the frozen plain-language definitions, and request settings: temperature0.5, top_p1, top_k-1, min_p0, parallel_tool_calls=false, cache_salt0, return_token_ids=true. No extra logprobs, tool execution, gold labels, examples, or label-dependent case selection. This is the existing isolated native-leaf first-response proxy, not a byte-identical replay of a recursive episode.

The unchanged suffix after each following output instruction is the same six-label list, a blank line, the exact frozen definitions, then JSON-encoded questions. Exact request hashes and all source inputs are inside each SPEC. Instructions before the shared six-label list are:

- Anonymous: `Return only a JSON array of labels in input order. Allowed labels: \n`
- Indexed: `Return only a JSON object mapping every input ID to its one label. Include each input ID exactly once, with no missing or extra IDs. Emit entries in input order. Allowed labels: \n`
- Echo: `Return only a JSON object mapping every input ID to an object with exactly "question" and "label". For each entry, first copy the complete input question verbatim into "question", then emit its one label in "label". Include every input ID exactly once, with no missing or extra IDs. Emit entries in input order. Allowed labels: \n`

Anonymous input is a question-string list; indexed/echo input is an ID-to-question object. IDs are q0001–q0256 from the frozen validation record_index. The anonymous grammar is exactly64 enum strings. Indexed grammar requires exactly the64 source IDs, each mapped to one enum label, no additional properties. Echo requires the same IDs, each with exactly question:string and label:enum; question is a free generated string, never a const or enum of input question text. The parser rejects duplicate keys at any level, missing/extra IDs, nonfinite values, wrong cardinality and extra prose; no offline repairs. Copy fidelity and question-before-label field ordering are scored separately from canonical classification. A copied-question error does not silently relabel or invalidate an otherwise structural label assignment.

| Comparison | Coordinates | Output cap | Explicit differences |
|---|---:|---:|---|
| Representation |4 contexts ×2 seeds ×3 arms =24|3072 in every arm|User instruction, input/output representation and matching constraints|
| Rotation |4 contexts ×2 seeds ×4 offsets =32|1024 in every arm|Anonymous input left-rotated by0/16/32/48; same instruction/schema|

The representation contrast is a whole representation-plus-constraint-package treatment, not a pure index or copy ablation. Rotation scoring inverts the declared permutation; it does not vote. Offset0 is shared in content across comparisons but has a different cap and a separate request, so do not pool it blindly. Within each context/seed, treatment order is cyclically counterbalanced; async completion order is measured, not assumed.

## Provenance and analysis

Inputs are record_index1–256 in validation720's existing question-group-hash order, not raw TREC line order. Four disjoint compositions use256 unique reused validation question groups from the declared300-validation partition. Source representative/all line numbers and original manifest hashes are retained. No source-test entries/files were read. Seeds981261401/402 are fresh against the declared scan and intentionally paired across both comparisons. Existing validation and checkpoint selection have already used these questions; this is exploratory reuse, not untouched test evidence.

Each call stores its exact request, raw response text/object, physical prompt and output IDs, parsed result, logical/cached/uncached input and completion tokens, wall time, and errors. Coordinates contain per-source question predictions, source/input/output positions, confusion-ready labels, copy fidelity, and host-only HUM/NUM counts. Physical prompt IDs are checked both for complete message text and exact equality with the CPU-rendered template hash. The latter is diagnostic, not assumed from schema compilation. Server/version preflight and STATUS preserve live identity, stop reason and unrun IDs.

Primary reports are canonical item accuracy among aligned outputs plus whole-contract validity/coverage, paired by context/seed/source ID. Malformed/unaligned arrays are not treated as64 semantically wrong items. Infrastructure errors are null, not model failures; all observed provider costs remain accounted, including alias rejection, while missing costs are explicitly counted by field. Repeated seeds/rotations do not create independent question or context samples. Host count accuracy is secondary and can conceal cancelling errors.

Promote correspondence as a useful mechanism only if its paired semantic improvement, especially late-position recovery, appears across contexts/seeds at an explicit token-cost premium and without copy/coverage failure. Rotation supports a position-linked mechanism if the same questions reliably change with presented quarter; persistence by source question instead weakens that account. Null/mixed effects retire broad correspondence claims at these weights, not all batching methods. This small exploratory design does not establish generic batching novelty, free planning, or improved training.

## CPU evidence and freeze

CPU_QUALIFICATION.json validates all24+32 actual protocol bodies, compiles9 representation schemas and1 rotation schema against the frozen tokenizer, and records every rendered prompt hash. Inputs max2069/1566 tokens respectively, so caps fit the8192 context limit. It verifies installed CPU protocol/compiler support, not live enforcement.

Focused tests use only a network fake around the actual inherited collector. They cover native request preservation, split/order, rotation inversion and request payload, strict IDs, free echo strings, separate copy scoring, host-gold invariance, raw token capture, and wrong-alias null/cost accounting. The frozen old collector/source remains unchanged; only a privately imported module instance receives this sidecar's callbacks.

PLAN.md records the approved implementation checklist; READY.json is the authoritative completion receipt, written after fresh checks and both immutable specs. No Git integration or broad suite is needed for this additive external research sidecar.

