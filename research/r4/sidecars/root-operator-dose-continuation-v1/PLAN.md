# Operator-dose continuation implementation plan

Goal: launchable exact checkpoint6→24 training first; separately finish the already frozen contemporaneous evaluation while training runs.

Architecture: isolated explicit-module reuse of qualified operator objective/model loader and lifecycle. New bounded optimizer validator/restorer replaces incompatible old LR/step assumptions. No shared-source changes. Python/PyTorch/PEFT, existing TRAIN/NATIVE environments only.

Spec: ../../ideas/2026-09-10-operator-sft-dose-decision.md and additive APPROVAL.md.

I use writing-plans, executing-plans and TDD; explicit external isolation and narrow checks override generic git worktree/commit/full-suite steps. No delegation.

- [ ] Input preparation (`dose_study.py`, `prepare.py`): tests require96 full/24 diagnostic coordinates, deterministic64-group label-blind selection from pinned2192, same gold/prompt across policies, all scopes balanced, no zero filtering. Save positive membership/provenance and realized baselines. Read original teacher first-prefix only for probes; do not append target actions.
- [ ] Exact restoration (`dose_train.py`, `test_restore.py`): fail first on absent restoration; test real CPU Adam step6 moments loaded unchanged, next step matches uninterrupted optimizer, reject reordered names/shapes/bad steps/LR/moments. Verify RNG restoration occurs after forward diagnostic and model setup. Derive actual504-name mapping with pinned CPU meta-model; no pretrained tensors or GPU loaded in qualification.
- [ ] Training entry (`dose_train.py`): compose qualified BF16base/rank8FP32 loader with checkpoint6 only; reuse unchanged full72 update. Save linked checkpoints7–24 after committed full passes, inherited checkpoint6 state as first parent. Postcheckpoint6/24 role/span NLL on fixed12. Fixed24 selection only; journal failures and physical elapsed. No child loading.
- [ ] Owner (`dose_owner.py`, `test_owner.py`): actual inherited MIG/TRAIN visibility,4320outer,4200work90cleanup, no services/provider requests in training. The unchanged qualified dependency import retains its private-credential preflight; MAIN supplies the existing credential, never logged. Qualified subprocess observation/owned cleanup, explicit exact output path and partial-failure terminal. CPU composed owner→training intercepted Popen check; never invoke actual model loading.
- [ ] Preparation/seal: source/input/corpus/checkpoint/base/environment closure, focused CPU tests and exact entry verification, READY publication last. Source immutable after READY. Parent fresh review/acceptance, no launch here.
- [ ] During actual training, implement separately sealed readout owner/collector under the fixed6480s cap, exact96+24 preplanned coordinates, native request/final/usage qualification. No training source mutation.
