---
question: Does a single10x larger step alter sampled copying behavior beyond the LR1e-5 result?
status: conditional CPU preparation; MAIN decides admission after original in-sample readout
scientific_change: learning_rate1e-5_to1e-4_only
start: original procedural SFT checkpoint32, not prior RLOO checkpoint1
frozen_batch: original fresh8 cp32 native32 trajectories
seed: 202609280001
science_seconds: 900
owner_seconds: 1100
external_seconds: 1200
---

Same original cp32 adapter020e05..., same original TRAIN_INPUTS bytes, temperature.5,32 denominator, eight G4 groups, RLOO(group mean with4/3 correction),12 nonzero bare-final actions5056 tokens,20 exact zero skips. No new rollouts, epochs, input selection, retries, compatibility sweep or checkpoint choice. Same HF-native selected-probability qualification/replay, detached biased tokenTIS cap2, same BF16 base/FP32 LoRA forward settings, dropout disabled, fresh AdamW once, weight decay0, clip1. Only learning rate becomes1e-4. An alias/output/receipt namespace distinguishes artifacts but does not alter sampled source actions.

This is a dose comparison, not a remedy assumed necessary. Serving-precision CPU evidence excludes total update erasure, while retaining quantization perturbation. The original LR1e-5 has flat primary short25/32 and long10/16; the one exposed four-needle whitespace win is unreplicated. No accuracy is used to select examples or alter this LR. MAIN may decline admission after the pending training diagnostic; READY is not permission to execute.

If admitted and qualified UPDATED, fix checkpoint-0001 and evaluate the SAME original fresh8 training32 plus the SAME exposed short-held32 used for prior RLOO (seeds202609270000..31), regardless training score. Reuse qualified old controls, explicitly treating both as development/in-sample or exposed evidence. Do not run held only after a good training score. These readouts are not implemented or launched by this training owner. Train-only gain is local fitting, not transfer or recursion. Uniform-zero selector-failure groups still have no RLOO signal; shared weights can change earlier actions despite the final-only mask.

Thin bindings import all accepted original core/train/owner functions unchanged. The new study changes LR and artifact namespace only. Fresh probability qualification and all12 gradient replays are recomputed before the optimizer; no old gradient is blindly installed. Source inputs, RNG, Adam initialization and exact zero masks are verified. CPU fixture checks actual branch Adam state equality and10x delta on a tiny real tensor model, and actual imported inner bindings; inherited real tiny-HF replay/no-step tests stay pinned.

MAIN only under shared exclusive lock and external1200-second timeout:

```text
/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python owner.py run
```

Verify CPU: same Python `owner.py verify`. Output `outputs/attempt-001`, checkpoint `outputs/attempt-001/checkpoint-0001`. Owner preserves NO_UPDATE/FAILED and reaps its child. All new source is additive; original checkpoint, trainer and outputs remain unchanged.

Evaluation interface: require result UPDATED, exact new READY, one fresh Adam step and learning_rate1e-4, parent cp32, actual initial tensors,12 replay/20skip, gradient/Adam/RNG/state/commit/binding hashes. The prior evaluator's qualifier hardcodes LR1e-5 and MUST NOT be reused as if it accepted this arm; its unchanged source needs an explicit narrow LR1e-4 qualifier in any later reader. No evaluation admission is implied by this file.
