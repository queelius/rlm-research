# Prime RLM strict OOLONG pilot

This sibling preserves the authenticated 16-train/8-heldout OOLONG slice and four-step Prime RLM
smoke while replacing the inherited official reward with strict task-aware final-line correctness.
The only optimized hook is weight-1 binary `correctness`. Official correctness, strict validity,
and official/strict disagreement are zero-weight native metrics. Fixture tests establish engineering
behavior only; neither a dry-run nor a four-step smoke is research evidence.

The runtime boundary remains owned by `rootless-runtime-feasibility-v1`. This sidecar consumes its
sealed Docker adapter, image, manifest, and launcher hashes from `data/SOURCE.json`; it does not copy
or modify that implementation. The container uses host networking and is suitable only for this
trusted exploratory OOLONG task, not untrusted or network-restricted generated code.

CPU verification:

```bash
root=/project/alex_phd/runs/rlm-research-r4/sidecars/prime-rlm-strict-pilot-v1
cd "$root"
PYTHONPATH="$root/src:/project/alex_phd/runs/rlm-research-r4/sidecars/official-rlm-prime-pilot-v1/src:$root" \
  /project/alex_phd/envs/prime-rl-5990b1b/bin/python -m pytest -q tests
CUDA_VISIBLE_DEVICES='' ./scripts/launch.sh smoke --dry-run
/project/alex_phd/envs/prime-rl-5990b1b/bin/python scripts/preflight.py
/project/alex_phd/envs/prime-rl-5990b1b/bin/python scripts/seal_manifest.py --verify
```

Deferred two-A100 launch, only after the GPU owner confirms devices 0/1 and ports 8810, 8820,
8821, 8910, and 5555 are free:

```bash
CUDA_VISIBLE_DEVICES=0,1 \
  /project/alex_phd/runs/rlm-research-r4/sidecars/prime-rlm-strict-pilot-v1/scripts/launch.sh smoke
```

Prime maps the first visible GPU to inference and the second to training. Never pass `--clean`.
Use `--resume` only for the same durable run after inspecting its checkpoints. Report both strict
reward and the three audit metrics, truncation/invalid reasons, group variance, task errors, token
and call counts, checkpoint/broadcast movement, and paired heldout outcomes. Stop if task errors
exceed 10%, every complete reward group is constant, the rootless boundary fails, or weights stop
advancing.
