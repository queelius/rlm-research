# Leaf output-scope72

Parent supplies a currently assigned endpoint for the exact old c32de selected
child. Binding is CPU-only; it is not proof that the service is live. The run
checks `/version` and `/models` alias/root/base before any generation. No service
start/stop, GPU acquisition, tool execution or training occurs in this sidecar.

```bash
SCOPE_DIR=/project/alex_phd/runs/rlm-research-r4/sidecars/leaf-output-scope-v1
SCOPE_PY=/project/alex_phd/envs/prime-rl-5990b1b/bin/python
SCOPE_ENDPOINT=/absolute/current-service/endpoint-selected.json

env CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
  "$SCOPE_PY" "$SCOPE_DIR/driver.py" bind \
  --endpoint-descriptor "$SCOPE_ENDPOINT" \
  --spec-path "$SCOPE_DIR/BOUND-attempt-001.json"

env CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
  "$SCOPE_PY" "$SCOPE_DIR/driver.py" run \
  --spec-path "$SCOPE_DIR/BOUND-attempt-001.json" \
  --output-dir "$SCOPE_DIR/outputs/attempt-001"
```

The descriptor must resolve to checkpoint-0128 at
`trec-leaf-sft-v1/outputs/attempt-001`, adapter SHA
`c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`,
config SHA`ec773bc3b9de58af98a7c4dce9a40af795a4d05cd47284dbbfb27eac99b74174`,
Qwen3-4B-Instruct-2507 base revision`cdbee75f17c01a7cc42f958dc650907174af0554`,
local vLLM0.28.0 and context limit at least8192. CPU weight/descriptor checks are
reused unchanged from correspondence controls. The actual alias is explicit and
may replace only the frozen body.model field. The API key stays in the named
environment variable. No old stopped endpoint is accepted as live proof.

72 calls: all64=8, full16=32, local16=32. The four exact previously inspected
64-record validation contexts and stable IDs are frozen; seeds981261601/602 are
paired across arms.1024 output-token cap,T.5/full support,four workers,60s call
timeout,1200s global live metadata/collection budget,no retries. Treatment order
is cyclically shifted by context_index+4*repeat; asynchronous completion order
is measured, not assumed. No source-test examples are selected or inspected.

This preserves the qualified reconstructed native first-leaf-response contract
at `/v1/chat/completions`, including system text, tools and CPU template order.
It is not TrainClient generation, a byte-identical recursive episode replay or
a root-policy experiment. Tools are never executed. Grammars are exact-cardinality
anonymous label arrays:64 or16 enum strings. The input is an ID/question list;
only declared target IDs map output positions back to original records.

`REQUESTS.unbound.json` contains every complete frozen body; SPEC also includes
those bodies, context/gold provenance, target maps and source hashes. Binding
seals all72 bodies with the actual old-weight alias. CPU_QUALIFICATION records
the actual vLLM request validation, both compiled XGrammar schemas and per-body
CPU prompt-token hashes. Returned physical prompt IDs are checked against these
hashes; absent/mismatched physical capture is reported, never repaired.

Per-call raw requests/responses/token IDs/usage and scores are atomically saved.
`analysis.json` reports whole-array validity, aligned canonical item accuracy,
original-position quartiles, matched-record contrasts, HUM/NUM target16 and
reassembled64 counts with false-positive/negative diagnostics. Malformed arrays
remain unaligned; errors/unrun coordinates are null. Counts can be correct despite
incorrect individual labels. No majority vote, inferred alignment or fallback.

All observed provider costs count, including four full prefixes in full16 and
responses rejected for a wrong alias. Missing logical/cached/uncached/completion
usage is explicitly counted by field. Request wall time is not GPU-only time.
all64→full16 changes selection burden as well as output-chain length; only the
full16→local16 contrast holds requested IDs/instructions fixed while removing
irrelevant visible records. Four contexts/256 reused groups—not1536 independent
items or untouched heldout evidence. No generic attention-mechanism claim.

Verify without endpoint contact:

```bash
env CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
  "$SCOPE_PY" "$SCOPE_DIR/driver.py" verify --spec-path "$SCOPE_DIR/SPEC.json"
```

READY.json is published last. No automatic retry/resume: preserve a failed attempt
and explicitly prepare any later run under a new bound specification/output path.
