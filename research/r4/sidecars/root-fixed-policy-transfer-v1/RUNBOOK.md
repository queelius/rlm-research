# MAIN-only acceptance

From this directory, read-only CPU verification:

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py verify
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 /project/alex_phd/envs/prime-rl-5990b1b/bin/python -m unittest -v test_data test_entry test_native test_lifecycle test_collect
```

After source acceptance, MAIN alone may execute READY.argv with its owned GPU and private existing credential preflight. Output must be new outputs/attempt-001. No restart/resume/retry. Parent outer cap2400s; owner work2100/owned2280s.

Expected immutable outputs: PLANNED_NULL_ENDPOINTS, OWNER_RUN, per-policy service bindings/actual descriptor/config/lifecycle, per-policy16 free endpoint records and failures, physical/role/typed audits, per-phase TERMINAL and ATTEMPT_COST_LEDGER when completed, owner COST_LEDGER and OWNER_TERMINAL even when readout is incomplete. Audit48 planned coordinates, never only surviving RESULT files. Do not execute model-generated code during audit.

CPU source tests initially failed on absent builder/owner/native inputs; these expected test-first failures are in the preparation transcript. A later termination fixture exposed swallowing MAIN SIGTERM in the per-phase failure handler; fixed before seal by propagating the stop request after scoped release. No scientific attempt exists from CPU qualification.
