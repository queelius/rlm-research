# Executable recursive-call example: 12-episode development probe

CPU-ready, no GPU/server launched by this sidecar's author. The assigned weight snapshot is
the six-update self-SFT checkpoint, **not a successful RLVR checkpoint**. The operator owns
the running endpoint. This probe uses three deliberately selected development questions from
context 8 and six fresh paired seeds; no source-heldout question or outcome selected the hint.

Compare the exact abstract procedure from plan-hint-crossover-v1 against that same procedure
plus this executable API example, placed before the unchanged final aggregate question:

```python
import json
records = [line.split(" || Instance: ", 1)[1].strip()
           for line in open("context.txt") if " || Instance: " in line]
batch = records[:4]
child = await rlm(
    "Return only a JSON array of labels in input order. Allowed labels: "
    "human being, location, abbreviation, entity, description and abstract concept, "
    "numeric value.\n" + json.dumps(batch)
)
print(child.answer)
```

The surrounding text identifies this as a starting batch, not a final answer, and asks the
agent to continue covering relevant records and compute the requested aggregate. No label
assignments, gold values, aggregate answer, or solved task is supplied. The first four input
records are fixed by source order, not selected by outcomes. Both arms retain the same verbal
strategy and nano-RLM coding/recursion system prompt. This is an additive execution scaffold,
not a short-prompt comparison, free planning, or a train/test transfer test.

## Frozen design and model

- IDs 12000008, 12000009, 12000025 were selected from development-only truncation, subsequent
  literal tool-block and wrong-aggregate cases in the baseline. Two arms × two seeds = 12.
- Fresh paired seeds: 767095240, 1930367705, 507709489, 1090081857, 196921417, 1636418165.
  They are disjoint from all baseline hint56 seeds. Each task has each arm first once;
  six adjacent pairs are shuffled with Random(2026090812).
- Plan SHA-256: `fb9576dca3b6e810a9b122f3646ac69fdb82d739f2d18d2beac90553f20fba85`.
- Assigned seal: [SELF_SFT_SPEC.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SELF_SFT_SPEC.json"), SHA-256
  `714b27605e2a28a1a3cb3c23a5a8eec25c5ce23e71a0fe03d3aa1449af5fc351`.
  Alias `strict-rlm-qwen3-4b-self-sft-final`; checkpoint-0006 adapter SHA-256
  `0c08ef740d20c0c4928ee84996a4543494afb79536eb67d8c7224d4ee0712175`.
- The optional [PREPARED_BASELINE_SPEC.json](../../../../ARTIFACTS.md#unpublished-files "Not published: PREPARED_BASELINE_SPEC.json") preserves the same
  task/seed plan at the original zero-update adapter, without implying that a baseline
  example run has happened. Its SHA-256 is
  `2f376da372b3795afbedeba6dd5682bf7bb7ea34e67478b27aa3a2f2369b310f`.
- Same evaluation client, temperature .5, top_p=1, top_k=-1, min_p=0, per-call max_tokens=2048,
  same rootless image and nano-RLM 4ef3438/depth1, and same 300/900/60/60-second
  setup/rollout/finalize/scoring caps as hint56. Four paired workers, one existing endpoint.
  Total study cap 1800 seconds; each arm has identical budgets. Realized input lengths and
  model calls may differ and are counted. No source/harness changes to the baseline driver.
- Atomic per-episode checkpoints, null execution-error rewards, stop above 50% execution
  errors after eight attempts, and the original resume deadline all reuse the baseline runner.

## What counts as recursion

The primary outcome, `actual_recursive_model_call`, requires a `subagent_call` semantic edge
between committed sampled model-call nodes with ACP request identities. Also retain
`subagent_return` edges to identify the child result being consumed by a subsequent model
request. These are stronger than a code mention, but do not prove correct classification or
that recursion helped the final aggregate.

Separately record assistant mentions of `rlm(`, executed tool-cell AST calls to `rlm`, and
`sub_rlm_num_calls`. The last field is a **created child-session directory count**, not proof
of successful child inference. Missing session metrics remain explicitly missing. Additional
strict-success, terminal-validity, Python/inspection, token, truncation and error measures
are inherited unchanged. All raw traces are retained for adjudication of disagreements.

The exact pinned API was inspected in local public-source snapshots:
`api.py` and `broker.py` annotate `async run(prompt: str) -> RLMResult`; `types.py` declares
`RLMResult.answer: str`; upstream `test_real_kernel_uses_brokered_rlm_callable` executes
`child = await rlm('hello'); print(child.answer)`. `Session.aggregate_child_metrics` explains
the directory count; the supervisor and semantic-edge implementation explain actual child
launch and committed-call relationships. See the [source/checksum/MIT-license manifest](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/2026-09-08-literature/recursive-example.6xBrmx/PROVENANCE.json").
Downloaded source was read, not executed. A CPU test executes only our authored example with
an in-memory context and a fake asynchronous child returning `.answer`.

## Assigned self-SFT launch

The endpoint is already owned by the parent; API credentials must be in
`STRICT_RLM_CALIBRATION_API_KEY`. This command does not start a model server:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 timeout --signal=INT --kill-after=90s 30m /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/recursive-call-example-v1/driver.py --weight-condition post_update --endpoint-descriptor /project/alex_phd/runs/rlm-research-r4/operations/2026-09-08-resume/inference-self-sft-attempt-001/endpoint.json --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/recursive-call-example-v1/SELF_SFT_SPEC.json --endpoint-url http://127.0.0.1:18601/v1 --output-dir /project/alex_phd/runs/rlm-research-r4/sidecars/recursive-call-example-v1/outputs/self-sft-001
```

For a CPU-only read-only preflight, use the same descriptor/spec/weight flags with `--preflight`
and omit endpoint/output flags. A different assigned checkpoint must receive a new immutable
descriptor and spec via `--prepare`; never edit the existing files.

Five focused tests passed, including seed disjointness, exact additive prompt isolation,
authored-cell execution and `.answer` access, mention/session/committed-call separation, and
nonmutating configuration validation. Ruff check and format check passed. Runtime validation
uses a deep copy because nested config validators mutate dictionaries; the failed initial
prepare created no spec and was fixed before either sealed spec was published.

If the example increases committed child calls, it demonstrates execution headroom supplied
by a concrete scaffold. If it only increases mentions or unexecuted code, the bottleneck is
still action formatting/adherence. If calls happen but strict success does not improve,
classification, aggregation and added cost remain separate issues. No outcome here supports
a claim of discovered decomposition or broad compositional transfer.
