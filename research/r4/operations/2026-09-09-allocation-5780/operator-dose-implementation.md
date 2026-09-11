# Operator dose continuation: training-first handoff

CPU READY: `sidecars/root-operator-dose-continuation-v1/READY.json`
SHA256 `76f1462596352a423546fe3f338d78247960d7a298871681244e04325b496191`;
identity `9ed37260c320313682a718747c3035083c8229859284a28bd38fbe116588d41f`.

Exact checkpoint6→24,18 unchanged full72 passes, persisted504 Adam states/moments and RNG, no child load/recapture. Actual step6 optimizer and source-derived meta-model504-name mapping validated on CPU; live loader must match order/shape/dtype before attaching states. Post6 diagnostic precedes RNG restoration; saves7–24 after committed global updates. Post24 diagnostic time is separate from optimizer/checkpoint time. Fixed24 only, no partial substitution.

Training-first MAIN-approved cap4320outer =4200work+90owned cleanup+30margin. Separate readout cap6480; combined10800. Training source frozen now; readout implementation will use a separate seal. Inherited lifecycle dependency preflight still requires the privately supplied local-provider credential, though training makes no provider requests. Assigned MIG is inherited unchanged by TRAIN Popen.

Fresh focused checks:5 TRAIN tests passed in4.70s (real CPU Adam next-step continuity, bad mapping/recipe/ordinal rejection, RNG, actual504 checkpoint validation, label-blind inputs);2 native owner tests passed in2.30s (actual composed owner→intercepted TRAIN Popen/CLI and failure inventory). No model/GPU/service launch by preparer.1307 source and3546 input pins verified; CPU seal14.48s. Whole4B GPU load remains actual-run qualification, not falsely covered by CPU tests.

Frozen evaluation:96 full episodes (fixed6/24 × original24 + root-new24) and24 single-action teacher-first probes. New64 source groups selected from scoped2192 without label/outcome filtering, four16-record clusters, three operators each supported/heldout. All source records were previously prepared and c32-training-exposed. New24 zero floor5/24, best constant1 gives8/24; old24 zero floor1/24, best constants2/3 give5/24. No rerolls. Policy order fixed6 then24; both contemporaneous, temporal-order limitation retained.

Launch argv and verify argv are in READY. MAIN owns fresh review/acceptance, GPU/queue and launch. All historical sources/seals unchanged. Training readiness does not claim the separately pending native readout is implemented.

## Additive readout readiness,03:15UTC

Separately sealed `sidecars/root-operator-dose-readout-v1/READY.json`, SHA256
`e51be544e14d037dcd92427310f5514609ea1f38f8ab33c176187d5433685f42`;
identity `3ba2eb66d366446359aa50dd472e7c3f3e31fc2bac3608094f00498fb3aa93cb`.
CPU_REPORT SHA256 `aaa02ff1703c8fb09418918b1b0a72bc359d1c35ef4526dfd6bb7c41752c75b9`.

Seven fresh focused tests passed in22.66s;1323 source and3648 input pins verified. Actual owner→qualified service wrapper→intercepted inference Popen config has twoLoRA/8192. Full collector CLI and explicit study/binding aliases are exercised. Authored native fixture executes file read→one exact-ID child fixture→scoped count8→authenticated Answer:8, correctly scoring0 against dataset gold1. The source prediction is never repaired to gold. All48 task prefixes/files are frozen and independent of policy/gold; max first prefix1084. Twelve direct first-action fixture requests preserve the original native body except root alias and fresh seed, authenticate output tokens/logprobs, and never execute returned programs. Parser tests preserve malformed native attempts separately.

The initial histogram-copy failure is retained under readout `preparation-attempt-001`; JSON numeric-key reserialization was replaced by literal byte copying. First native fixture failure is retained under `qualification-native-001`; its lazy original-protocol namespace was explicitly initialized against the original study before new aliases. These CPU failures did not reach a scientific model or change frozen task content. Readout task source metadata truthfully describes prepared-catalog/child-training exposure without changing prompt or file bytes.

Readout cap6480outer =6300work+150cleanup+30margin; two3000s phases advance early, with300s harvest. Each phase allows180startup,240probes,2490full collection,90release. A failed diagnostic substage does not gate otherwise runnable primary free48. MAIN termination prevents subsequent phases. All96 primary and24 diagnostic slots remain preplanned; no rerolls or partial24 substitution. Physical attempts/completions/unknown usage are separate, provider billing unknown. Training and historical acquisition costs are not counted as newly incurred evaluation work.

`dr_owner.py verify` is executable before training completes. `run` requires the training owner to have completed/released and authenticates the complete7–24 chain and actual selected24 artifact hashes before any service. No post-checkpoint performance gate or selection. All readout and training sources remain immutable after their respective seals. MAIN accepted/launched training03:01:15.83; initial live receipts confirmed all504 adapter tensors, all504 saved Adam states and all Python/Torch/CUDA RNG equalities, and checkpoint7 committed. This is author-side operational monitoring, not an independent outcome audit.
