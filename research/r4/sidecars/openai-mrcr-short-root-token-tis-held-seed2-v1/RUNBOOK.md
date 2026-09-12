# Fixed held16 token-TIS seed-block replication

Preparation is CPU-only. MAIN may execute the three immutable stages sequentially using the exact
commands in `CPU_READY.json`. Each stage owns one fresh service and has a 650-second owner cap; an
external supervisor should allow 700 seconds. Do not retry a failed stage implicitly, choose a dose,
or launch only the previously successful context.

Before launch, run:

```text
CUDA_VISIBLE_DEVICES='' /project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py verify --stage base
CUDA_VISIBLE_DEVICES='' /project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py verify --stage lr1e-5
CUDA_VISIBLE_DEVICES='' /project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py verify --stage lr1e-4
```

The run commands require MAIN's exclusive GPU assignment and private credential environment. No
credential value belongs in an argument, manifest, or artifact.
