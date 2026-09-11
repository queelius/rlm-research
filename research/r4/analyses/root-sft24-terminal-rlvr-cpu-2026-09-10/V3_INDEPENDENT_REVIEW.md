# Independent review: warm terminal-RL V3 continuation

Reviewed after runtime_port sealed V3 and before any V3 launch. I authored neither V3 nor its output. V1 never launched; V2 (`attempt-002`) collected the original 24-slot window 1, exported 13 admitted episodes, then failed during service release before a trainer command, optimizer update, checkpoint, or readout request. V3 uses the new immutable namespace `attempt-003`.

## Verdict

No material prelaunch blocker found. Fresh verification returned identity `7ad4aad2f7fc6182ab0667b0fe1869343c076380b7f8bb1aceca91aa7471d972`; all 841 source and 1,436 input pins matched; and nine focused tests passed in 5.56 seconds.

## Contract checks

- `warm_resume_v3.source_proof()` pins the failed V2 owner, window-1 generation, complete group, and manifest; rejects prior trainer/training artifacts and any earlier readout request/result/physical/episode/row artifact. It binds the original SFT24/fresh-Adam0 generation and 13 admitted episodes.
- The actual CPU qualification replayed all 24 immutable native episodes, selected the same 13, and passed the real `warm_train_v2.py --preflight` path without loading a model or taking a gradient step.
- `warm_owner_v3` trains the reused window-1 group before starting a new model service. Only after a committed update or authenticated noop does it advance the cursor to window 1. Windows 2–8 retain the original tasks/seeds and require 1,380 training-side seconds before starting; there is no refill or reacquisition of window 1.
- A service pointer remains active until release succeeds. A failed release prevents the next service, trainer, and readout. The focused lifecycle fixture exercises the qualified SIGINT/SIGTERM/SIGKILL sequence under intercepted identities and confirms that the new 90-second release envelope contains the 50–60 second escalation path.
- V3 charges 381 seconds from V2 and limits its own outer/work/owned clocks to 10,419/10,119/10,299 seconds. Training-side time is 5,019 seconds and two final blocks retain 2,550 seconds each. Each final collection reserves 90 seconds for release; final cleanup retains 30 seconds.
- The output policy is the last actually committed checkpoint, including step zero. A checkpoint committed before a later exception is recovered once and consumes its fixed window; no second update is permitted.
- The replacement cost ledger unions stage-plus-request-ID role records, does not count typed mirrors twice, distinguishes routed-only intents, HTTP attempts, and authenticated native completions, and retains usage unknowns. Original and V3 costs remain separate before the combined view; billing is not inferred.

## Recovery provenance and boundary

The frozen V2 owner reports an active unreleased service. `V3_EXTERNAL_CLEANUP.json` records MAIN's SIGTERM, disappearance of the owned GPU identities, and a later successful same-port service start plus preflight. This is an external cleanup receipt, not a rewritten V2 release result. MAIN must still provide the normal accepted-parent/GPU handoff at launch.

This review establishes source/runtime continuity for a bounded infrastructure recovery, not numerical success. The qualification did not load weights, execute PPO/TIS, or prove that any gradient-bearing V3 run will complete. The original 192 training and 96 readout denominators remain authoritative: 24 training slots are reused from V2, at most 168 are newly acquired, and all original readouts were unattempted before V3.

## Seals reviewed

- `READY_v3.json`: SHA-256 `ae31dc8a3515da6a87a1cee8ac184ba15338062113766c9fee228851afcc1a9f`
- `RESUME_BINDING_v3.json`: SHA-256 `64a0e00343dc4c0d5ab8a9e8313ab07270e789aa3406b4f0ef03bb573e411f67`
- `V3_EXTERNAL_CLEANUP.json`: SHA-256 `3978f984b96dd003fb613b6731a3afdd98f111e52eda2b8b4f7d0c84af6dd0b1`
- `CPU_REPORT_v3.json`: SHA-256 `e6d5a1f3176359d702435acbbe81fcdc6b0f0803501309ad22d3e758fadaedfc`
