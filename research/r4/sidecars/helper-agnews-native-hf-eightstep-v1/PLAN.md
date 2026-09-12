# AG fresh-data eight-step implementation plan

Goal: prepare, but do not launch, eight sequential importance-corrected helper RL updates on the frozen broader training1024, starting from c32 and carrying complete Adam/RNG state. The separate fresh heldout512 is final-endpoint-only.

Approved spec: `ideas/2026-09-12-agnews-native-hf-eightstep-dose.md`, amended by `helper-agnews-broader-data-v1/DESIGN.md` and MAIN's conditional implementation approval. Work is confined to this new external sidecar; all sealed sources and live GPU owners remain unchanged.

Global constraints: 8 steps; each step32 B4 groups ×4 fresh actions,128 distinct new records; T.5; native concurrency4/batch-invariant; HF BF16 base/FP32 LoRA, SDPA/noKV/dropout off/nonreentrant gradient checkpointing; fraction-correct reward scaled4; unchanged count-RLOO /128 and raw detached full-sequence IS; ESS≥102.4/max normalized weight≤.1; all128 replay token1e-5/sequence1e-4; AdamW LR1e-5/wd0/clip1; no heldout selection; no optimizer step on any gate failure; no simultaneous native/HF model residency; MAIN sole GPU launcher.

## Task 1: continuation and exact per-step policy binding

- [x] Add `core.py` for frozen data/source verification, step view, exact parent binding and authenticated STEP_COMMIT chains; `train_step.py` for persistent Adam/RNG and the existing qualified objective/replay seams; `train_ag.py` and `prepare_masks.py` are narrow subprocess shims.
- [x] First write two focused fixtures. `test_continuity.py` performs two actual tiny HF/PEFT updates and compares uninterrupted versus saved/reloaded adapter+Adam+RNG, including all LoRA gradients and state tensors. `test_native.py` uses the actual native tokenizer/four-key response normalizer/mask generator and checks exact prior-checkpoint path/hash binding and rejection of a changed parent hash.
- [x] Implement `update_once(model, optimizer, records, masks, output, completed_steps)`; only call `optimizer.step()` after qualification and every replay pass. `restore_training_state` verifies parameter layout and Adam counters before RNG restore. Step1 constructs fresh Adam; subsequent steps load full state after model construction.
- [x] Run only those two actual fixtures in the existing pinned environments; record commands, elapsed times and stdout/stderr.

## Task 2: bounded owner, seal and MAIN review

- [x] Add `owner.py`, reusing the sealed one-step native/service/mask lifecycle for each step and saving exact parent input receipts before collection. Authenticate every previous committed step; stop on partial collection/gate/update/cleanup failure. Keep the last committed checkpoint, never promote it to step8.
- [x] Add `prepare_inputs.py`, `QUESTION.yaml`, `seal.py` and endpoint interface notes. Inputs reference the immutable eight schedules; prepare host-only per-context gold. The owner requires a separate MAIN admission receipt pinning reviewed qualified mixed first-step/replica evidence and actual measured phase caps, with total external≤10800s. Actual first step gave a tiny positive, so replication is prioritized and this run is not admitted.
- [x] Preserve per-call raw evidence; commit adapter/config/full optimizer/RNG/state plus collection/mask/qualification/replay/parent-binding hashes after each synchronized update. A later explicit resume starts only after an authenticated complete step and carries RNG/Adam; no partial-step recollection or automatic repair framework.
- [ ] Seal CPU readiness and exact final-checkpoint interface. Final evaluation is c32 versus checkpoint8 on fresh512; no intermediate evaluation. MAIN reviews and supplies admission/launch, or chooses replication/diagnosis from the first-step result. No GPU command is run by this agent.
