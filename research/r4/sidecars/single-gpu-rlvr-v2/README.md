# Single-GPU RLM RLVR v2

CPU-prepared on 2026-09-08. No GPU launch or research optimizer update has been performed by
this preparation. `outputs/attempt-001/spec.json` freezes the existing Qwen3-8B/adaptive k576
inputs, current rootless image identity, source hashes, dependency lockfiles, task inventory,
and compute/checkpoint policy. The real rootless import probe passed; all 15 CPU tests passed,
including a finite nonzero gradient through the actual action-masked policy loss. Ruff passed.

The 8B run collects 12 calibration episodes, then tries up to 24 predeclared fresh training
episodes in calibration-ranked cell order. It uses the first cell with a real mixed reward
group on one or more training prompts. Eight held-out episodes run before and after exactly
one LoRA optimizer step. Inference stops before training starts; post-update inference starts
after the trainer exits. The full cap is 90 minutes, including a 30-minute trainer cap.
This one-step result is an initial end-to-end proof, suitable for follow-up fresh-rollout
updates; it does not conclude the research direction.

When the controller assigns the GPU and port, launch the already prepared 8B attempt:

```bash
env PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/rlm/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/single-gpu-rlvr-v2/source/single_gpu_rlvr.py \
  run --attempt /project/alex_phd/runs/rlm-research-r4/sidecars/single-gpu-rlvr-v2/outputs/attempt-001 \
  --gpu 0 --port 19471
```

All calibration, training, and held-out task and sampler seeds are disjoint and predeclared.
The coordinator's calibration/train temperature is 0.8. The generic trainer accepts the one
positive temperature recorded in an externally exported group, including 0.5 for the native
4B training path. It rejects mixed-temperature groups and never silently substitutes 0.8.

For exported 4B data, import `training_group(rows)` from `source/single_gpu_rlvr.py`, write its
returned object as `training-group.json`, and call the `train` subcommand using the pinned
training interpreter with one explicitly assigned `CUDA_VISIBLE_DEVICES`. Pass `--group`,
`--output` (a new directory), `--model`, and `--adapter`. The current 4B inputs are:

- Model: `/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554`.
- Adapter: `/project/alex_phd/runs/rlm-research-r4/sidecars/prime-rlm-strict-pilot-v1/outputs/qwen3-4b-oolong-rlm-strict-smoke-v1/broadcasts/step_0`.
- Interpreter: `/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python`.
- Driver library directory: `/project/alex_phd/.cache/nvidia-driver-580.126.09/runtime-lib-v1`.

Each exported episode has `episode_id`, `task_id`, `cell_id`, `split="training"`, `sample_seed`,
`temperature`, `trace_trainable`, binary integer `reward`, and `turns`. Each turn contains
`input_ids`, `prompt_length`, `labels`, `loss_mask`, and exact aligned `old_logprobs`.
Context labels are -100 and context loss masks are zero. Any nonempty number of controller
turns is admissible. Include extra provenance on episode rows or in a separate export manifest;
`training_group` preserves row provenance in its canonical `group_id`.

Completed, aligned policy mistakes—including malformed answers—have declared reward zero.
Infrastructure failures and missing/corrupt action captures have reward null and are excluded.
The inherited runtime discards partial traces on exceptions, so budget-exhausted exceptions
cannot supply negatives in this version. A lack of valid reward variation is recorded as
`no_training_signal`, never repaired by inventing rewards. Loss normalization is equal per
episode, then per controller turn, with within-prompt population-standardized advantages.

Each generated episode runs entirely inside the inherited rootless boundary. Only its own
scratch directory is writable and visible as `/attempt`; the host inventory, gold answers,
training artifacts, and sibling episodes are outside this mount. Source and runtime mounts
are read-only. Container names include the attempt and episode identity; timeout cleanup
targets only that exact name. The worker refuses direct host execution.

Training saves adapter, optimizer, and RNG state immediately after one update, plus hashes,
finite positive gradient norm, changed-tensor count, parameter delta, action-token count,
old-policy logprob drift, package versions, and GPU memory. The CPU checks do not prove GPU
memory fit, rollout/trainer logprob agreement, a changed research checkpoint, or improved
held-out behavior. Those remain measured outcomes of the first GPU run.
