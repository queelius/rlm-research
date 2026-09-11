# Train-only leaf semantics × output-contract probe

Status: **CPU-prepared, queued, no GPU inference performed by the preparing agent.** The
original 4B service was stopped when the 8B pipeline began. Do not run this specification
against the 8B alias. Reloading the exact frozen4B alias is operator-owned.

Question: can concise category definitions and enforced output shape fix distinct errors
seen inside otherwise outcome-successful recursive programs? This is a direct first-response
classifier proxy, not a full RLM harness intervention or an exact byte-for-byte leaf replay.

## Immutable comparison

89 already-observed training/development context8 questions form 18 fixed source-order
batches: seventeen of five records and one of four. Each batch receives all four arms at
one shared fresh seed399651808, temperature0.5, max_tokens256. Arm launch order rotates by
batch; each arm occupies each within-batch position four or five times. There are 72 model
requests and 356 requested record labels, not 356 independent contexts.

| Arm | User text | Decoding constraint |
| --- | --- | --- |
| baseline | Observed child label-list prefix + exact question JSON | None |
| definitions | Same + generic category definitions | None |
| schema | Byte-identical messages to baseline | JSON array, six-label enum, exact batch length |
| both | Byte-identical messages to definitions | Same JSON enum and length constraint |

Neither messages nor request bodies contain record gold labels, aggregate answers or labeled
examples. Only the scorer reads the frozen [train label map](../../../../ARTIFACTS.md#unpublished-files "Not published: ../trec-train-process-audit-v1/CONTEXT8_LABEL_MAP.json").
The definitions paraphrase the [official TREC taxonomy](https://cogcomp.seas.upenn.edu/Data/QA/QC/definition.html):
they are an explicit operationalization, not a claim of reproducing every historical
fine-category annotation rule. The exact text is frozen in `design.definitions` within the
[bound specification](../../../../ARTIFACTS.md#unpublished-files "Not published: FROZEN_REPLAY_SPEC.json").

`CONTRACT.json` records the observed leaf system/user messages and effective sampling from
RLVR example task12000025/repeat1, trace0 nodes3/4/5. The selected prefix includes a newline
after `Allowed labels:`. Tool definitions are reconstructed from the trace's ToolDefs and
the pinned [nano request builder](https://github.com/PrimeIntellect-ai/nano-rlm/blob/4ef3438d55fdd39b18d34035833c73e13b006733/src/rlm/engine.py#L675).
The original HTTP envelope bytes/headers were not retained, so reconstruction is stated
explicitly. The native leaf coding-agent system message and ipython tool schema remain in
all arms, with no forced tool choice. A generated tool call is recorded but **never executed**.
There is no child filesystem, continued conversation, recursive scheduling or repair loop.
All arms reduce the observed per-call cap from2048 to256 and use the new seed; these fixed
changes mean the baseline is not an exact replay of an earlier output.

## API and CPU verification

The [official vLLM0.28 documentation](https://github.com/vllm-project/vllm/blob/2cf0a6915ce544dc493a0990f2ea38d81601128a/docs/features/structured_outputs.md)
supports a top-level `structured_outputs.json` schema. The probe uses that field, not the
removed `guided_json` API. It changes the decoder constraint without changing messages.
The installed ChatCompletionRequest model validated all72 concrete payloads; all36 schema
arms compiled through installed XGrammar on CPU, including the final four-item batch.
This qualifies request construction and grammar compilation, **not live GPU enforcement**;
the first live API error stops new dispatch rather than dropping the constraint or retrying.

Local environment: Python3.12, vLLM0.28.0, XGrammar0.2.1, HTTPX0.28.1. Eight focused tests
pass, covering record pairing, no gold in requests, invariant messages across schema arms,
strict labels/cardinality, cached-token accounting, immutable checkpoints, base-weight
identity and an injected HTTP failure through the actual runner. The bounded failure test
uses an in-process HTTP transport, never a live service. Original six tests first failed
before implementation; the descriptor-version mismatch was separately reproduced and fixed.
Source URLs, revisions, licenses and hashes are recorded in the external
[source manifest](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/2026-09-08-literature/leaf-contract.7HPUr5/PROVENANCE.json").

## Metrics and limits

Primary record accuracy uses exact canonical label strings. A complete equal-length JSON
array permits positional scoring; an out-of-vocabulary entry is wrong, never alias-collapsed.
Malformed arrays, nonstring arrays, wrong-length arrays and tool-call responses receive no
imputed positional matches. Whole-array schema validity is reported separately. Execution
or provider errors retain null scores, attempted coverage and explicit error counts; both
accuracy per model-completed record and conservative correct/89 planned records are named.
Each call preserves raw response text/JSON, the complete request object plus digest,
per-record predictions/gold/confusion, finish reason, wall times and raw token usage.

Raw vLLM `usage.prompt_tokens` **already includes** cached input; logical input is that value,
not prompt+cached. Cached and uncached subsets are separately recorded when available.
`return_token_ids=True` was already in the source Eval contract and is retained; returned
token arrays are preserved without requesting new logprobs. Missing usage is explicit.
Constrained decoding changes the sampling policy by design; these outputs are not declared
RLVR-trainable trajectories, and no current training admission rule changes.

Compute: one already-loaded4B model on one A10040GB, four concurrent direct requests,
30-second per-request timeout, 600-second total rollout cap, maximum18,432 sampled output
tokens. Expected duration is a few minutes, not a guaranteed timing claim. Each completed
or interrupted call is atomically checkpointed without overwrite. First API failure stops
new requests; at most four already in flight may finish. Failed attempts are preserved and
not silently resumed/retried. A new spec/attempt is required for any changed weights or design.

## Operator commands

The original-weight bound SPEC SHA256 is
`b8b72e5c9792000da8f190fbd662da0ca0d887ad920fee0497ebe76a767f5922`;
driver SHA256 is `a82baf0d9be7f5cbc756ced908c405f6aba4497b46a4ca56e15c8900798c8bce`.
The weight descriptor remains explicitly planned; the runner verifies local weight hashes,
then checks live `/version` and `/v1/models` before its first model request. A descriptor is
not evidence that an alias is currently loaded or that the server remains reserved.

After the operator reloads the exact alias `strict-rlm-qwen3-4b-frozen-replay`:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 timeout --signal=INT --kill-after=30s 11m /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/trec-leaf-contract-probe-v1/driver.py run --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/trec-leaf-contract-probe-v1/FROZEN_REPLAY_SPEC.json --output-dir /project/alex_phd/runs/rlm-research-r4/sidecars/trec-leaf-contract-probe-v1/outputs/frozen-replay-001
```

For separately assigned4B weights, first bind a **new** immutable descriptor/spec, then run
with a new output directory; `bind` is CPU-only and does not contact the server:

```bash
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/trec-leaf-contract-probe-v1/driver.py bind --endpoint-descriptor /absolute/path/to/new-endpoint.json --spec-path /absolute/path/to/new-LEAF_SPEC.json
```

## Decision rule

Definitions improving canonical accuracy without a shape change supports semantic ambiguity.
Schema improving validity without accuracy supports a distinct output-contract bottleneck.
An interaction suggests both matter. If neither helps, retire this particular wording/shape
intervention before building a generic typed-child feature. The selected six-rollout
original/dropFP29/dropFN75 counterfactual remains a ranked later proposal in the
[process-audit report](../trec-train-process-audit-v1/README.md); it is not another active job.
No heldout labels were used to construct or select this experiment.
