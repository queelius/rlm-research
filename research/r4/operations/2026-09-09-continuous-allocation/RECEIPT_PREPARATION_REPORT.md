# Receipt ablation preparation: CPU READY

Prepared September9,2026, approximately06:29UTC. Main acceptance and launch remain
outstanding. Only new `sidecars/root-receipt-ablation-v1` and this report were
written. No live model/GPU calls, service launch, process signals, acceptance,
environment installation, current independent-root outcome inspection, or frozen
historical source edits were performed.

## Frozen result

Sidecar root:
`/project/alex_phd/runs/rlm-research-r4/sidecars/root-receipt-ablation-v1`.

| Artifact | SHA256 |
|---|---|
| READY.json | `1eba49031384deda22bbfdd9d234cc7ff1b43e63c0b72081af2c7c270a5b74f2` |
| SPEC.json | `90000411c23cc92ad1ed21906cd30a5687bfa315e509b19eecc9e3792532b198` |
| receipt_api.py | `4ffaccc9ad15ee088ab1f6d50545a8d9bf269cf2481febaf5bf5d42e333706a6` |
| experiment.py | `1803aa59cfaf94edf7ac5db865cce4c721eb2302b31ab186c5b88b0fc4488690` |
| driver.py | `e3b936b3d2a5358fe4682cad0a875a28673bb7aae7fe06de4606567fee5ff32e` |
| results.py | `4878bf245d105a41e7d008343f8bbaae577832c800cff11964222276c02d012a` |
| prepare.py | `430192f4ebce2317067fff7331abc8f1df69469f5e029f32b62181f7baf4b099` |
| qualify.py | `ff24b13e62a9d086da06583b4c0c68e16ed06b7d4d1f5935a4d8792bb5f3c441` |
| FOCUSED_TESTS.json | `af4455c58c3775f08da77d422a19fe3444ceb291fd47b267ef7b1e2ae6dad1c3` |
| qualification-map-attempt-001/RESULT.json | `e358ecdfb36b6af9f2c1b985061677c9b9d67647676f459136b0e4e4f5ad2fbd` |

SPEC binds222 source/input artifacts, including the inherited source and model
closure, exact new sources, public task identities, all72 coordinates, fixed
historical root473210…/childc32de bindings, both decision documents, and current
map-format CPU qualification. READY additionally binds the fresh test result.
No source closure is rehashed within an episode loop.

## Experiment contract

72 end-to-end episodes: six exposed64-record transfer contexts × two original
target-count questions × two fresh seeds × three arms. Each of24 matched triples
shares its task/context and seed. All six permutations of unchanged/indexed_raw/
receipt occur four times. Seeds981267101–981267124 are frozen; no collisions with
739 prior seed values found in35 existing top-level sidecar SPEC*.json and
inputs/PLANS.json files. This is a bounded audited scope, not a global registry.

Root and child are the fixed historical identities in the decision, not selected
from the live independent-root run. Task gold and strict final score are unchanged.
No training, new likelihood, alias/action mask, decoding grammar, retry, repair,
fallback, or result-schema modification was added.

Main's pre-inference format amendment is implemented: output is a JSON **object
mapping requested IDs to allowed label strings**. Duplicate keys, missing/unknown
IDs, malformed JSON, fences/prose/truncation, non-JSON constants, invalid labels
and types remain visible errors. Invalid `labels_by_id` is null. Raw text and
lexical key order are retained. Valid maps need not return keys in requested order.
Validation does not establish semantic correctness.

Both helper arms use the same `rlm_records(selected_ids, query, allowed_values)`
request constructor. A public source catalog binds positional source IDs to exact
record bytes, context SHA and source group IDs. Caller can choose any subset,
query/vocabulary, decomposition/recovery, or ordinary `rlm` calls. Target-only
yes/no queries work without demanding all-label evidence. Each invocation makes
exactly one original `rlm.api.run` call; transport errors propagate unchanged.
Only the receipt view exposes optional `receipt()`. Both retain the native result
and its original answer/session/usage/turn metadata.

Unchanged arm has byte-identical historical instruction and receives only
`context.txt`. Both new arms replace the historical procedure/example equally with
the optional helper example. First-task prompt lengths are566 tokens unchanged,
314 indexed_raw,349 receipt (exact counts frozen for every task). Thus the
secondary comparisons to unchanged are practical harness-package comparisons,
not isolated indexing-only effects. Primary receipt−indexed_raw compares receipt
availability plus35 tokens of explanatory consumption documentation here.
Do not claim physically paired child calls after root decisions diverge.

## Actual runtime seams qualified

No experiment-local code changes nano's engine, broker schema or native client.
`ReceiptTask.setup` inherits strict task setup and writes the stdlib module,
public catalog, and arm config to the new owned runtime working directory.
`ReceiptTask.finalize` saves the root-writable helper audit in `trace.info`; missing
diagnostics are recorded separately and do not change task reward.

The inherited collector assumes two-row queue units. Main approved a private
hash-gated adapter: source SHA
`406a64ca59e4d77e6126c3fd97339c57cb5d7aef6808c998d7e18be7e6456832`,
with exactly one `range(...,2)` and one slice `offset+2` changed to3. Only the
adapted `run` AST is loaded against inherited globals. Native collection, scoring,
episode persistence, fail-stop, timeout and cleanup logic remain inherited.
An actual queue-AST execution test proves24 complete triples with unchanged
dispatch order and full72-row coverage; it does not merely inspect source text.

Driver uses unchanged qualified native capture, original campaign owned command/
service start, and lifecycleV2 owned-service release. CPU analysis is an explicit
separate command after the owned GPU job exits, not an in-lock postprocessing step.

## Fresh verification evidence

- Parser/adapter tests were written and observed failing before their corresponding
  implementation; the map-format correction again produced three expected failures
  before implementing the amended parser.
- Seven focused tests PASS: valid reordered target-only map; strict invalid-map
  rejection/raw preservation; identical prompt/one-call/no-retry behavior; unchanged
  task/gold/context/public-only files and balanced triples; actual queue dispatch;
  unknown/unrun outcome separation; owned cleanup on collection failure with no
  inline analysis.
- All10 local Python files compiled in memory, without bytecode writes.
- `qualification-map-attempt-001` passed three actual pinned rootless/native fixture
  episodes: nine deterministic CPU provider calls, zero actual model/GPU calls.
  Both helpers imported in active IPython, traversed the original broker, and
  round-tripped exactly `{answer,session_dir,usage,turns}`. Receipt availability
  and valid map were checked in executable runtime code; local audit survived
  finalization. No live smoke is needed.
- `qualification-attempt-001` is retained superseded array-format CPU evidence,
  also nine fake calls and zero actual model/GPU calls. It is explicitly not the
  map-format qualification. These18 total fixture calls carry artificial
  token/logprob values, never behavior likelihood evidence.
- Fresh `driver.py verify` exited0 with `planned:72,gpu_calls:0` after freezing.

## Exact main-only launch

```sh
PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-receipt-ablation-v1/driver.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-receipt-ablation-v1/outputs/attempt-001
```

Main supplies the existing credential and one exclusive CUDA_VISIBLE_DEVICES only
after predecessors release ownership. External outercap2430s; whole owned job2400s;
work deadline2280s including service startup; collection cap2100s; minimum120s
owned cleanup reserve. Expected15–25min on one A100, not a guarantee. The service
and collector have no implicit retry or replacement coordinates. Raw failures and
unanswered/capped episodes remain separate; original >50% execution-error fail-stop
after8 episodes is retained.

After exit/release, CPU-only analysis is `driver.py analyze --output <same output>`.
It reports all three paired success contrasts, observable and scheduled accounting,
context summaries, helper failures/access/coverage diagnostics, root syntax markers,
native seed/alias capture verification, and raw physical attempt/token costs.

## Remaining concerns

No material runtime integration blocker remains. Source review and acceptance are
still main's responsibility. Receipt audit files are writable by root code and need
native-trace corroboration; access counts do not prove use in the aggregate. Contexts
are repeatedly exposed development data. New arms intentionally differ from the
historical supplied procedure, and receipt documentation is longer than raw-arm
documentation; report these package/instruction differences rather than attributing
everything to parser internals. Free child output can remain malformed or semantically
wrong, and optional helper uptake can be low. Those are experiment outcomes, not
reasons for hidden repair or changing the frozen grid.
