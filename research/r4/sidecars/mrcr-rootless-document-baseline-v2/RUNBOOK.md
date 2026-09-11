# Six-document paired MRCR pilot

Ready CPU preparation: `outputs/attempt-001`. No model requests or GPU launches
were made during preparation. Seven focused tests, source/input preflight, and
the actual trusted-code rootless probe passed.

The parent starts the frozen 4B step-0 service after the current GPU experiment.
Keep the planned endpoint file unchanged: the run links a separate **actual**
server/endpoint launch JSON naming alias `strict-rlm-qwen3-4b-frozen-replay` and
the original Prime step-0 adapter path. The API key stays in
`STRICT_RLM_CALIBRATION_API_KEY`, never in the descriptor or command.

```bash
env CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
  /project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/mrcr-rootless-document-baseline-v2/source/driver.py \
  run \
  --attempt /project/alex_phd/runs/rlm-research-r4/sidecars/mrcr-rootless-document-baseline-v2/outputs/attempt-001 \
  --actual-endpoint ACTUAL_LOADED_STEP0_SERVER_JSON
```

The last argument is the parent's observed launch artifact, not the planned
endpoint. The runner authenticates source/input hashes, original adapter hashes,
image identity, and advertised model alias before dispatch. The endpoint does
not expose tensor hashes; the actual loaded weights still rely on the operator's
launch configuration.

Twelve sequential episodes are paired on six distinct documents, with one fixed
question per document, temperature 0, seeds 970260100–970260105, balanced arm order,
and the native thinking-enabled Qwen3 renderer. Both arms receive the identical
file path/question; only the sketch arm receives the pre-existing context-only
sketch, bounded to 4,096 UTF-8 bytes. No direct arm or 8K input truncation.

Limits: 180 seconds per episode, 30 minutes total dispatch/generation budget,
2,048 output tokens per request, recursion depth one, and the native shared
six-completed-turn limit. Native concurrent subcalls may overshoot that turn
threshold by requests already in flight. There is no separate two-subcall knob;
no such bound is claimed. Cleanup may extend wall time after cancellation.

Gold/scoring files stay host-only and gold is absent even from TaskData, which
the framework can expose to tools. Each uniquely named rootless container gets
exactly one authenticated read-only context bind. The qualified runtime uses
host networking, so this is filesystem isolation, not a network sandbox.

Only an explicit, nonempty root reply on a clean `agent_completed` trace is
scored with the frozen official MRCR metric port. Partial turns, tool output,
answer files, budget stops, and infrastructure failures are not answer fallbacks.
Invalid episodes have a null score and a separate failure category. Full episode
records and analysis are checkpointed after every coordinate; this exploratory
pilot is evaluation only and makes no training claim. Document bytes read are
not instrumented; exact code/tool traces and native recursion metrics are kept.

Artifacts: `SPEC.json`, `tasks.json`, read-only `contexts/`, host-only
`host-scoring.json`, `CPU_ROOTLESS_PROBE.json`, then `RUN_BINDING.json`,
`episodes/`, `analysis.json`, and `STATUS.json`. No automatic rerun/resume is
provided: an already-started attempt is not silently replayed.
