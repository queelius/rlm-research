# Pre-acceptance training-environment correction

The original operator-SFT READY was not launchable: od_study.TRAIN incorrectly equaled its native rollout interpreter. MAIN's targeted review caught this before acceptance or any scientific attempt. The original14 tests proved native transport/tiny numerical behavior, not full PEFT dependency availability. The earlier implementation handoff is superseded on this point.

Actual native environment: `/project/alex_phd/envs/prime-rl-5990b1b/bin/python`, Python3.12.12, torch2.13.0+cu130, transformers5.6.2, safetensors0.7.0; PEFT and Accelerate absent.

Corrected TRAIN exactly equals the qualified joint training path: `/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python`. Actual CPU imports report torch2.13.0+cu130, transformers5.15.1, peft0.20.0, accelerate1.14.0, safetensors0.8.0, Python3.12.12. PeftModel, AutoModelForCausalLM and the qualified training-module composition import successfully in this interpreter. No4B model or CUDA initialization was requested. No environment was installed or modified.

MAIN authorized the minimal pre-acceptance edit. TRAIN path and all local runtime READY references now agree on READY_v2.json. Five affected originals were preserved byte-identically in pre-acceptance-v1; ENVIRONMENT_AMENDMENT.json records each original hash/snapshot/corrected hash. Original READY.json is unchanged. No study inputs, starting adapter, objective, corpus, budget or readout changed. Source snapshots are retained, not deleted; the test snapshot uses .snapshot to avoid duplicate pytest discovery.

New exact-interpreter/PEFT/load-composition test plus three affected owner tests:4 passed8.07s. Original14-test native qualification remains explicitly pre-amendment; no redundant26s native rerun was needed. Corrected actual owner verify exited0.

Corrected READY_v2 SHA256: `3ca5943ec51e8b45525bf4c9dfe4a50616517279aa057e76127d440deaab9dde`.
Canonical identity: `a19086d24b3c0f41b7a14f34fed20bc8061c3da7c860ede8641f8077cee224e2`.
Closure:1176 source+25 input pins.
Amendment SHA256: `f649e13c2f6f073b0f60833d44f5aeec3f2016b9c5267a5dea59d6c0a08d345c`.

Owner argv remains the original od_owner.py run command in the implementation report; it now verifies V2 and dispatches only training through the qualified TRAIN interpreter. MAIN alone accepts/launches. No scientific attempt existed at this handoff.
