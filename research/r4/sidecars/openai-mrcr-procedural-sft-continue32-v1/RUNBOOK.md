# MAIN-owned continuation

Run CPU qualification with the existing training interpreter and hidden CUDA:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python -m pytest -q -p no:cacheprovider test_resume.py
```

From any directory, `train.py plan` prints the exact proposed GPU invocation. MAIN must
assign one exclusive visible GPU and enforce the shared lock plus1600-second external cap:

```bash
/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-procedural-sft-continue32-v1/train.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-procedural-sft-continue32-v1/outputs/attempt-001 --seconds 1500
```

Success requires RESULT.status=COMPLETED_32_TOTAL_UPDATES, optimizer_steps32,
additional_optimizer_steps28, all28 committed new checkpoints, and the fixed step32
binding. Readout uses an independently admitted evaluator; a low teacher loss never
authorizes held evaluation by itself. No credential is required for this trainer.
