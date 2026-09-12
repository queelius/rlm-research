# Runbook

MAIN alone may launch this fixed training-only rollout screen. The owner does not optimize.

```bash
/project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py verify
/project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py run \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-procedural-sft32-onpolicy-screen-v1/outputs/attempt-001 \
  --outer-seconds 1100
```

Use a 1,200-second external cap and the shared GPU lock. Preserve timeouts and partial coordinates;
do not resample dynamically. The terminal-strip-disabled hook must wrap the entire collector and
environment-serving scope.

