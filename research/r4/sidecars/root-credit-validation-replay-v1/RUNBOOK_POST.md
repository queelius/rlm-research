# Post-update binding and replay

The additive `post_replay.py` is CPU-tested. Actual result binding remains `WAITING_CHECKPOINT_IDENTITY`; no post-update binding/spec/checkpoint has been fabricated. The original replay/source/spec remain unchanged.

Once the declared trainer has a successful `RESULT.json`, bind its checkpoint on CPU:

```bash
env CUDA_VISIBLE_DEVICES='' HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  /project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/post_replay.py bind \
  --result /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/training/attempt-001/RESULT.json \
  --binding /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/POST_BOUND_WEIGHTS.json
```

This authenticates the one-step root-only result, finite positive gradient/delta, zero child/observation loss, passed correction guards, unchanged original-root/child identities, frozen recipe, execution/input envelopes, training source/group/manifest/correction hashes, checkpoint state and every checkpoint-file hash. Root model/config hashes come from that authenticated state. No pickle/optimizer objects or generated code are executed. The new alias is exactly `strict-rlm-qwen3-4b-root-tis-step1-v1`; the selected child and its prior selection provenance remain unchanged.

Parent may reuse the existing unmodified `leaf-role-routing-v1/source/serve.py` with that binding and a fresh `--run-dir /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/service-postupdate-attempt-001`. Only the parent assigns the GPU and starts/stops that service. Its historical filename `endpoint-original.json` names `role_map.root`; here its actual alias is the explicitly declared new trained root, not the old original alias.

After the assigned service exists, freeze the exact eight-coordinate post-update spec on CPU:

```bash
env CUDA_VISIBLE_DEVICES='' HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  /project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/post_replay.py prepare \
  --result /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/training/attempt-001/RESULT.json \
  --binding /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/POST_BOUND_WEIGHTS.json \
  --endpoint /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/service-postupdate-attempt-001/endpoint-original.json \
  --server-log /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/service-postupdate-attempt-001/inference.log
```

Run only on the parent's assigned service:

```bash
env CUDA_VISIBLE_DEVICES='' HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  /project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/post_replay.py run \
  --result /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/training/attempt-001/RESULT.json \
  --binding /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/POST_BOUND_WEIGHTS.json \
  --endpoint /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/service-postupdate-attempt-001/endpoint-original.json \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-credit-validation-replay-v1/outputs/postupdate-replay-attempt-001
```

Before model calls, the driver reauthenticates the result/checkpoint/binding, exact validation coordinates and runtime task hashes, native source/role-capture contract, and the current service's processed-logprob log prefix. The inherited collector checks live advertised alias/root/parent and uses the new root alias in actual requests. No hidden alias swapping, prompt changes, reseeding, task selection, repairs or retries are added. Child weights remain fixed. The same original replay estimates trajectory variability rather than assuming identical seeds imply deterministic trajectories.

Five focused tests pass across original replay and post-result/endpoint admission; F-rule checks pass. Full actual post-result authentication and service binding cannot be tested until those artifacts exist. Source SHA256: `9d19df28475dfbed4a59ebd148d2eefd4f2982e814109e243f98c63554d0e8fd`.
