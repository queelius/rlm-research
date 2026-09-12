# Runbook

MAIN owns all GPU launches. Run the two fixed arms independently under the shared GPU lock and the
private credential environment; either order is scientifically acceptable because seeds and inputs
are already frozen.

```bash
/project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-long-transfer-eval-v1/owner.py \
  verify --stage base

/project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-long-transfer-eval-v1/owner.py \
  run --stage base \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-long-transfer-eval-v1/outputs/base-001 \
  --outer-seconds 1100

/project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-long-transfer-eval-v1/owner.py \
  run --stage checkpoint32 \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-long-transfer-eval-v1/outputs/checkpoint32-001 \
  --outer-seconds 1100
```

Wrap each owner with a 1,200-second external limit. Do not retry implicitly or substitute a new
seed. Preserve partial episodes, native calls, service receipts, and owner terminal state.

