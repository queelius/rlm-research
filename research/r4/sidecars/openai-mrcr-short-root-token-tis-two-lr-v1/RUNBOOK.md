# Runbook

MAIN owns the GPU launch. From any directory, with exactly one assigned visible GPU:

```bash
/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-short-root-token-tis-two-lr-v1/owner.py \
  run \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-short-root-token-tis-two-lr-v1/outputs/attempt-001 \
  --cap-seconds 900
```

Use the established external shared-GPU lock and a 1000-second outer cap. The owner refuses
an existing output directory, a different cap, a changed closure, or anything other than one
visible GPU. It requires no API credential and makes no native-service or heldout calls.

Success requires `RESULT.status=UPDATED_TWO_INDEPENDENT_BRANCHES`, one step in each fixed
branch, exact initial identity and shared gradient receipts, persisted baseline/low/high
likelihood inventories, and a passing 10x dose relationship. Preserve partial/failure outputs.
