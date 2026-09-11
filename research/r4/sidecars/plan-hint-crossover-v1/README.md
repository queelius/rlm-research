# Plan-hint crossover

The live-ready baseline seal is **SPEC.runtime-id-v2.json**, not SPEC.json.
See [DESIGN.md](DESIGN.md) for the literal prompt contrast, exclusions, disjoint source
contexts, metrics, checksums and interpretation limits. The baseline launched by the parent
session on September 8 writes `outputs/pre-update-001`; do not modify its frozen inputs.

Five focused CPU tests and the no-inference preflight passed. An actual read-only image
inspection also passed after normalizing the rootless wrapper's digest prefix.

## Baseline / preflight

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/driver.py --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/SPEC.runtime-id-v2.json --preflight
```

The parent already launched the baseline; do not launch a duplicate. Resume uses the same
spec, endpoint and output arguments plus `--resume`, retaining the original 90-minute deadline.

## Post-update replay (after checkpoint exists)

The now-assigned replay is **six-update self-SFT**, not RLVR. Its immutable spec is
[POST_SELF_SFT_SPEC.json](../../../../ARTIFACTS.md#unpublished-files "Not published: POST_SELF_SFT_SPEC.json"), SHA-256
`a81755663d0289959270fd33a1d6c89df2385a1dc4d96b52fe32dd3ad19ace8c`.
The exact task list, full paired prompts, all seeds/order, environment and budgets equal the
pre-update seal. Only endpoint/model-weight provenance, request model alias and weight-condition
label differ. Both clients remain eval.

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 timeout --signal=INT --kill-after=90s 90m /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/driver.py --weight-condition post_update --endpoint-descriptor /project/alex_phd/runs/rlm-research-r4/operations/2026-09-08-resume/inference-self-sft-attempt-001/endpoint.json --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/POST_SELF_SFT_SPEC.json --endpoint-url http://127.0.0.1:18601/v1 --output-dir /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/outputs/post-self-sft-001
```

Prepare a new descriptor copied structurally from the frozen baseline descriptor. Change
`model_alias`, adapter `path`, `config_sha256`, and `model_sha256` to the actual post-update
snapshot. Keep the base-model path/revision/manifest, inference sampling and harness fixed.
The descriptor's API-key field is an environment-variable name, never a secret value.

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/driver.py --prepare --weight-condition post_update --endpoint-descriptor /absolute/path/to/post-update-descriptor.json --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/POST_UPDATE_SPEC.json
```

The printed `plan_sha256` must remain
`d2e8df38adba7d9ce199797df72f86604092fa7d22789eb6b467e6377ad90698`.
The new descriptor and spec are new immutable artifacts; never overwrite baseline inputs.

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 timeout --signal=INT --kill-after=90s 90m /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/driver.py --weight-condition post_update --endpoint-descriptor /absolute/path/to/post-update-descriptor.json --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/POST_UPDATE_SPEC.json --endpoint-url http://127.0.0.1:18601/v1 --output-dir /project/alex_phd/runs/rlm-research-r4/sidecars/plan-hint-crossover-v1/outputs/post-update-001
```

Use the actual owned server URL. The client stays eval in both weight conditions. Changing
client/rendering during the replay would introduce an additional factor. All fourteen task
prompts, paired seeds, order, budgets and four-pair concurrency remain fixed.

The source-heldout context 6 is report-only and already reused from September 2. Do not let
its outcomes select the training checkpoint, reward, prompt revision, or training schedule.
Context 8 is the development context; there are only two context groups overall. The baseline
is running alongside other requests on the warm server, so token use is a cleaner cost
comparison than wall latency unless concurrent server load is reproduced post-update.
