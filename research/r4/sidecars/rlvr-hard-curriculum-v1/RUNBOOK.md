# Hard-curriculum RLM RLVR runbook

This is an exploratory one-update study. It is ready to launch only when `preflight` and `audit`
both return `status: ready`. CPU fixtures and tests are engineering validation, never research
evidence.

## Frozen study

The old policy is Qwen3-8B plus adaptive SFT checkpoint k576. Calibration walks five task-only
rungs at temperature 0.8: 96/8, 128/10, 160/12, 192/12, and 224/14 records/labels. Each rung is
four prompts by six rollouts. The first complete rung with at least 20 valid trajectories,
20--80% success among valid trajectories, and two mixed prompt groups is selected. Calibration
stops after selection or 120 episodes.

Malformed, timeout, model-failure, and turn-limit trajectories have `reward: null` and never
enter training. The update applies one clipped AdamW step (`5e-6`, epsilon 0.2, beta 0) only to
root/controller action tokens. Leaf, prompt, observation, and environment tokens are masked.
Held-out evaluation uses eight independent prompts by three rollout seeds. Its primary endpoint
is paired terminal-success change across all 24 pairs; invalid counts as terminal failure only
for this evaluation endpoint, never as a training reward.

## CPU-only verification

```bash
cd /project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-hard-curriculum-v1
export PYTHONPATH=/project/alex_phd/repos/rlm-bootstrap/.worktrees/adaptive-context-tranche1/src:/project/alex_phd/repos/rlm/src:/project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-hard-curriculum-v1/source

PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' python -m pytest -q \
  source/test_curriculum.py source/test_rlvr_hard_curriculum.py
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' python \
  source/rlvr_hard_curriculum.py preflight --json
ruff check source/curriculum.py source/rlvr_hard_curriculum.py \
  source/test_curriculum.py source/test_rlvr_hard_curriculum.py
ruff format --check source/curriculum.py source/rlvr_hard_curriculum.py \
  source/test_curriculum.py source/test_rlvr_hard_curriculum.py
```

For the slower full base-shard audit, run:

```bash
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' python \
  source/rlvr_hard_curriculum.py audit --json
```

Neither command imports Torch, initializes CUDA, opens a port, or starts inference.

## Prepare immutable attempt

```bash
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' python \
  source/rlvr_hard_curriculum.py prepare \
  --attempt /project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-hard-curriculum-v1/attempt-001 \
  --json
```

Preparation seals all 60 potential tasks before any outcome: 20 calibration tasks and 40
potential held-out tasks. It writes read-only `spec.json`, `tasks.json`, and `launch.json` and
refuses an existing path.

## Exact deferred launch

First verify GPUs and ports 18431--18432 are explicitly assigned and idle. Do not inherit a
global CUDA visibility mask; the driver gives each subprocess one exact GPU identity.

```bash
cd /project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-hard-curriculum-v1
export PYTHONPATH=/project/alex_phd/repos/rlm-bootstrap/.worktrees/adaptive-context-tranche1/src:/project/alex_phd/repos/rlm/src:/project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-hard-curriculum-v1/source
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1
export CUDA_VISIBLE_DEVICES=''
export GPU0='<exact GPU or MIG identity>'
export GPU1='<exact GPU or MIG identity>'

/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python \
  source/rlvr_hard_curriculum.py run \
  --attempt /project/alex_phd/runs/rlm-research-r4/sidecars/rlvr-hard-curriculum-v1/attempt-001 \
  --gpu0 "$GPU0" --gpu1 "$GPU1" --port0 18431 --port1 18432
```

Expected elapsed time is 35--70 minutes, capped at 90. Calibration takes at most 120 episodes;
the selected held-out rung takes 24 old-policy and 24 new-policy episodes; training takes exactly
one optimizer step.

## Resume and audit

After a nonterminal infrastructure error, rerun the exact command with `resume` instead of
`run`. Content-addressed episode artifacts are reused only when their bytes and phase inputs
authenticate. A completed training marker skips the update and revalidates checkpoint hashes;
partial training outputs without that marker refuse resume so a second step is impossible.

Do not resume `failure.json` or `result.json` attempts. A `no_calibration_coordinate` failure is
a scientific stop: create a newly designed and sealed sidecar rather than changing temperatures,
scoring invalid trajectories, or editing the attempt. Inspect `paired-analysis.json` for all raw
pair outcomes, jointly-valid exact delta, validity delta, transitions, and invalid reasons.

Launch gates are: exact bundle/adapter/source/repo hashes; raw-token contract probe; complete-rung
admission; action/logprob alignment; old-policy drift at most 0.5 max and 0.1 mean; finite positive
gradient; zero non-controller loss tokens; exactly one optimizer step; changed LoRA hash/tensors;
unchanged base shards; and complete 24-pair pre/post inventories.
