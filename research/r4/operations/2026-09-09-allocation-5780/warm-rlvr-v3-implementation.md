# Warm RLVR V3 CPU handoff

Prepared by runtime_port, the V3 author; question_cards and MAIN provide independent review. No GPU/service/process/queue action was performed here. V1/V2 sources, READY receipts, and attempt-002 remain unchanged.

## Ready identity and launch

Sidecar: `/project/alex_phd/runs/rlm-research-r4/sidecars/root-sft24-terminal-rlvr-v1`.

- `READY_v3.json` SHA256: `ae31dc8a3515da6a87a1cee8ac184ba15338062113766c9fee228851afcc1a9f`.
- Identity: `7ad4aad2f7fc6182ab0667b0fe1869343c076380b7f8bb1aceca91aa7471d972`.
- Closure: 841 source pins and 1436 input pins, including the exact original export, role/typed wire artifacts, V2 qualification, and external cleanup receipts.
- Actual fresh `warm_owner_v3.py verify` exited 0 and returned the identity above.

Exact command (MAIN scheduling authority only):

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-sft24-terminal-rlvr-v1/warm_owner_v3.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-sft24-terminal-rlvr-v1/outputs/attempt-003
```

## Narrow correction and preserved science

V2 completed window-1 collection/export: 24 episodes, 13 selected training episodes, no training command/checkpoint. Its 30-second release alarm interrupted the qualified stop escalation before termination completed. The unreleased service then prevented readout startup. V3 first trains this exact immutable window-1 GROUP/GENERATION with fresh Adam at cursor 0; it does not reacquire, copy, reseed, or select new trajectories. Then original windows 2–8 may execute within the remaining budget. All original 192 training slots and 96 final coordinates remain planned, with the original fixed-start/c32, objective, masks, seeds, task semantics, and last-committed-policy rule unchanged. There were no original readout physical artifacts; the source verifier enforces this non-reroll condition.

Added `warm_resume_v3.py`, `warm_wire_v3.py`, `warm_owner_v3.py`, `test_v3.py`, `seal_v3.py`, `RESUME_DESIGN_v3.md`, `PLAN_v3.md`, `V3_PREFLIGHT.json`, and `V3_EXTERNAL_CLEANUP.json`; generated immutable `RESUME_BINDING_v3.json`, `CPU_REPORT_v3.json`, and `READY_v3.json`.

Lifecycle difference: release allowance is now 90 seconds using the unchanged qualified stop implementation; the active service pointer is cleared only after successful release. Failed release prevents a later service or trainer and leaves cleanup aimed at the same owned service. Main termination does not start later phases. A window cursor advances only after an actual update or declared noop; committed checkpoint recovery records consumption without replay.

Accounting difference: union stage/request-ID role-wire records, retaining known returned calls and unknown usage; typed records are mirrors, not extra physical calls. The old V2 zero-cost receipt is preserved and explicitly not used as evidence of zero cost. Original window 1 contributes 286 physical attempts (215 root/71 child), 283 native successful transports and 3 HTTP-400 responses; known input/output/cache tokens are 830188/31926/796496, with three unknown usage entries per field. Reusing its export does not count these calls again as new V3 acquisition.

## Bounds and qualification

Combined active execution cap is 10800 seconds: charge 381 seconds for the original 380.0108866-second parent run, leaving V3 outer 10419, owned 10299, work 10119. Training-side allowance is 5019; protected paired finals retain 5100. A fresh window requires at least 1380 remaining training seconds; final policy blocks reserve 90 seconds for release. Early stage completion advances immediately. Calendar stopover/idle is separately disclosed, not hidden as active execution.

Final focused run: 9 tests passed in 5.52 seconds (6.7627-second subprocess wall time), CUDA hidden, zero GPU calls/model loads. Tests cover budget/reserve arithmetic, immutable-source/no-prior-readout admission, actual qualified SIGINT→SIGTERM→SIGKILL escalation under an intercepted clock, failed-release ordering, original-input/new-output trainer arguments, actual trainer Popen GPU-environment inheritance, and native-wire known/unknown/dedup accounting. Actual original 24-episode native replay and exact qualified TRAIN `--preflight` also passed; `V3_PREFLIGHT.json` records the transcribed result identities rather than claiming persisted full stdout or a model load.

External cleanup is not rewritten into V2's failed owner receipt. `V3_EXTERNAL_CLEANUP.json` pins MAIN's PARENT_REQUEUE record and subsequent accumulation SERVER_START/SUITE_PREFLIGHT: original owned API/tracker/engine gone and GPU empty, then successful same-port service rebind. No separate socket probe is claimed.

Independent reviewer question_cards reports no material blocker; review SHA256 `467a395a59003c0afbc8290b2c9adf2b02d138fc5f3a29e4a90d66c60430faba`. CPU qualification does not establish learning efficacy, full future service availability, or that all eight windows will fit. Training admission remains stricter than endpoint availability; NULL and planned-denominator accounting remain explicit.
