# Exploratory end-to-end RLM RLVR pilot

This is a one-update research spike, not a confirmatory study. It asks whether an exact
terminal reward can produce a real, traceable LoRA update from a two-turn RLM trajectory and
whether any change is visible on separate held-out tasks.

## Frozen design

- Start policy: `rlm-adaptive-sft-adaptive-s2908202707-k576` at checkpoint 576.
- Calibration: four fresh train-split conditional-count tasks, task seeds 410000--410003;
  temperatures 0.8, 1.0, and 1.2; six samples per coordinate (72 episodes total).
- Admission: choose the valid task/temperature coordinate nearest 50% exact success with at
  least four valid episodes and both reward values. Invalid trajectories are excluded.
- Reward: exactly 1 when final text equals the private answer, otherwise 0.
- Update: one AdamW step at `5e-6`, clipped policy ratio 0.2, no KL term. The terminal group
  advantage is inherited by both controller turns. Prompt, observation, and all other
  environment tokens have zero loss. Only controller action tokens receive loss. Leaf-model
  output tokens do not receive loss in this pilot.
- Evaluation: eight separate task seeds 420000--420007 with three fixed samples each (24
  episodes), paired before/after at the selected temperature.
- Provenance: exact controller prompt/action token IDs and selected-token logprobs, canonical
  RLM traces, and leaf request/response event IDs and hashes are retained. This permits a
  follow-up comparison of root-only credit against shared root/child credit.

The CPU preflight generated 12 unique tasks. The largest public prompt is 1,630 Qwen tokens;
with the 512-token public completion cap it uses 2,142 of the 8,192-token server window. The
preflight task file SHA-256 is
`97cebe45cc71e9bda43994d1ce6c7a824736a93bf36a8283a4c08ab7eee5beda`.

## Exact launch

Run only after the controlled replay releases both GPUs and ports 8431--8432 are free:

```bash
cd /project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-e2e-pilot-v1/source

export PYTHONPATH=/project/alex_phd/repos/rlm-bootstrap/.worktrees/adaptive-context-tranche1/src:/project/alex_phd/repos/rlm/src:/project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-e2e-pilot-v1/source
export CUDA_VISIBLE_DEVICES=''

/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python \
  rlvr_pilot.py run \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-e2e-pilot-v1/attempt-001 \
  --gpu0 MIG-cfcfe369-9742-5104-84d9-7e0bfc536bc5 \
  --gpu1 MIG-43a3375a-1942-592d-accf-d0884164dcb8 \
  --port0 8431 \
  --port1 8432
```

GPU 0 and GPU 1 first host identical old-policy vLLM replicas for calibration. Next, GPU 0
performs the one-step update while GPU 1 serves the held-out pre-evaluation. Finally both GPUs
serve the new checkpoint for held-out post-evaluation.

Expected wall time is roughly 45--75 minutes. A 90-minute alarm is enforced. Other stop rules
are: no valid mixed-reward coordinate, token/logprob misalignment, old-policy logprob drift
above 0.5 maximum or 0.1 mean, server death, OOM, nonfinite or zero gradient, or no verified
trainable-parameter/adapter-file change. Every completed episode and the one-step checkpoint
are written before later phases continue.

## Verification and outputs

CPU-only validation command:

```bash
PYTHONPATH=/project/alex_phd/repos/rlm-bootstrap/.worktrees/adaptive-context-tranche1/src:/project/alex_phd/repos/rlm/src:/project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-e2e-pilot-v1/source \
CUDA_VISIBLE_DEVICES='' \
/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python \
  -m pytest -q test_rlvr_pilot_core.py test_rlvr_pilot_driver.py
```

The attempt directory contains immutable `tasks.json` and `spec.json`, per-episode JSON and
canonical traces, `training-group.json`, `training/checkpoint-1`, optimizer and RNG state,
`training/training.json`, paired evaluation artifacts, server logs, and terminal `result.json`
or `failure.json`.
