# MAIN-only launch

CPU preparation grants no GPU authority. Parent must authenticate READY/source closure, own exactly one free allocated GPU and the existing shared scheduling lock. Never signal a predecessor or start a duplicate.

Verify using the qualified native interpreter, with CUDA_VISIBLE_DEVICES empty:

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-coverage-first-v1/driver.py verify
```

Exact accepted-job argv (parent supplies GPU/environment and2700s process envelope):

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-coverage-first-v1/driver.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-coverage-first-v1/outputs/attempt-001
```

Environment: inherited qualified Prime Python; PYTHONDONTWRITEBYTECODE=1, OMP_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1; same accepted rootless image/local-cache wrapper. No installation, source edits or model download. The localhost fake provider was CPU-only preparation, not a serving checkpoint probe.

Driver uses the unchanged authenticated suite/lifecycle helpers; success_sft8 phase then efab. Each phase exposes only its exact root and fixed c32 child aliases and independently verifies live models/base paths before episodes. Four workers execute eight sequential rotated triples per root.900s collection/phase,2550s shared work from before verification,2670s owned/120 final cleanup reserve,2700 outer. Owned service release runs in finally; next phase starts only after successful release. No automatic retry or resume. Any failure preserves output and leaves later phase unrun; only MAIN may choose a new prospective attempt.

Terminal markers: outputs/attempt-001/TERMINAL.json; each phase's PHASE_TERMINAL.json, rollout/STATUS.json and INITIAL_ROOT_PROVENANCE.json, service-stage/SERVICE_STOPPED.json. All raw rows/episodes/native and typed attempts/ledger events are immutable per-call artifacts. Collection completion is not model success. Independent scoring/graph audit must not retain the GPU scheduling lock. No expensive built-in post-release analysis in this runner.
