# Clean-validation leaf contract replication

The operator launched and completed the original-weight attempt after CPU qualification.
Results and mechanism caveats are in [analysis/REPORT.md](../../../../ARTIFACTS.md#unpublished-files "Not published: analysis/REPORT.md").
The immutable [design](DESIGN.md) defines 300 clean source-train validation groups,
60 five-question batches, four unchanged leaf72 arms and three fresh seeds: 720 calls,
3600 requested labels, 300 unique questions. Source-test question files and entries are
not read by this sidecar. This is exploratory validation replication, not source-test evaluation.

The frozen [driver](driver.py) imports the old immutable request builder, strict scorer,
cost accounting and checkpoint helper. It supplies a new source manifest, plan, runner,
dynamic denominators, classwise/macro metrics, paired per-question changes across repetitions,
and separately named DESC-alias sensitivity. It does not monkeypatch or edit the old module.
Gold/source labels stay in the host specification and scorer, never in model requests.

The [bound specification](../../../../ARTIFACTS.md#unpublished-files "Not published: FROZEN_REPLAY_SPEC.json") authenticates the actual operator-provided
`inference-frozen-contract-attempt-001/endpoint.json`, original base revision and zero-update
adapter. Its SHA256 is `a51ce28adb11b97c9a0a31224ec3f3cded948fbfa06ed6a1e4934d6aea469333`;
driver SHA256 is `f5504f456ed6aee9cc39e74efd314490bb53d4c22747572fbc19e45d2df4f371`.
Filesystem weight hashes and the descriptor are checked before the operator run; `/version`
and `/v1/models` are checked by the live runner. A descriptor alone does not prove current
server ownership or loaded memory state; those remain operator responsibilities.

Six focused CPU tests passed after first failing for missing implementation: clean paired
coverage, exact old request-contract parity, dynamic denominators and alias separation,
mutated source rejection, original-adapter enforcement, and checkpointed HTTP failure with
no retry. No GPU or live HTTP call was made by the preparing agent. Ruff reported one long
caution-string line; it was left unchanged once the specification was frozen. No broad suite,
environment change or new dependency was needed. [CPU_QUALIFICATION.json](../../../../ARTIFACTS.md#unpublished-files "Not published: CPU_QUALIFICATION.json")
records these checks and exact artifact identities.

## Operator invocation used

Do not rerun this command into the completed directory or launch another copy.

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 timeout --signal=INT --kill-after=30s 11m /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/trec-leaf-validation-replication-v1/driver.py run --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/trec-leaf-validation-replication-v1/FROZEN_REPLAY_SPEC.json --output-dir /project/alex_phd/runs/rlm-research-r4/sidecars/trec-leaf-validation-replication-v1/outputs/frozen-replay-001
```

Four workers share one operator-owned original4B vLLM service. Temperature0.5, max256
output tokens/call, three seeds980260100–980260102, 30-second request timeout, 600-second
rollout cap, atomic per-call checkpoints, no retries/fallback/tool execution. Dynamic
per-arm denominators are 180 calls and 900 repeated label assignments; per-seed denominators
are60 calls/300 labels. Null provider errors, unrecorded calls, model-completed malformed
outputs, canonical accuracy and schema validity are reported separately. Repeated predictions
remain grouped by their original question and batch; no independence-based confidence interval
is computed. Raw usage includes cached input once; wall times are descriptive under shared serving.

The new manifest uses the approved first source representative per normalized question group,
sorted by group SHA256; it verifies train bytes, the full prior OOLONG pool exclusion, group IDs
and class counts. Test disjointness is inherited from the authenticated partition audit and is
not re-established by opening source test files. Dataset license remains unknown.
