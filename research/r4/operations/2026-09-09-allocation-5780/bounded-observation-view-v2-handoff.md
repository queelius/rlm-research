# Bounded observation view V2 handoff

V1 READY `a5a50377…` was never launched and is rejected because its new raw-output ledger was task-working-directory visible. The additive correction is frozen at `sidecars/root-bounded-observation-view-v1/READY_v2.json` (SHA `889b59bef1acb1e0e14d2e494182cee5b599fa40486bda816b5128893038530f`, identity `f8312850c0b6b2250b6fc70aad6d3efefccc50929ffb01f79e916e2c2c5e1864`) and targets `outputs/attempt-002`.

V2 changes only raw-ledger placement and associated metadata. Complete raw tool results remain in nano-RLM's existing session log; hashes, sizes and clipping fields are added to that log, then harvested after rollout before harness cleanup. No raw ledger is added to task cwd. The system prompt advertises the conversation-log path, so deliberate policy access remains possible and must be audited. The estimand is passive next-request presentation, not access control. The 4,096-byte setting retains up to 4,096 raw payload bytes; warning/marker overhead is additional.

Focused CPU qualification passed six tests in 23.38 seconds, including an actual native clipped-next-request/session-harvest fixture. `CPU_REPORT_v2.json` SHA is `c49604685eeff2b6d58d08fafacc5460b51f5a2d0862db6c5645e65ad0feec6c`; all 5,479 transitive pins and the owner verifier pass. MAIN alone may accept and launch.

The prospective audit was frozen before attempt-002 existed at `analyses/root-bounded-observation-view-live-2026-09-10/METHOD_READY.json`.
