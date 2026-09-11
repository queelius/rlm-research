# Fixed-policy transfer implementation plan

> For agentic workers: execute inline with executing-plans; no subagents. Steps use checkboxes.

Goal: CPU-qualified READY, never a launch. Spec: ../../ideas/2026-09-09-fixed-policy-root-transfer-design.md, SHA3d32336edf6326209a00a267790fae086becf8c6fcf04da1dc5aa322d5ef0ed2.

Architecture: qualified joint-study imports with a new immutable panel and fixed-checkpoint binding; free-only wrapper around actual old collector; bounded readout-only owner. Existing external sidecar is the explicitly authorized isolation; no Git/env changes.

Constraints: four16-record contexts from QSR-complement78,16 coordinates per policy,48 planned slots before startup; no train/control/retry,180 episode/480 phase/2100 work/2280 owned/2400 outer,4 workers. Same actual root-native contract and c32 child.

## 1. Source and panel

- [ ] Write test_data.py asserting64 unique selected groups, exclusion from QSR448 and exact historical exclusion closure, four disjoint16 blocks and16 paired free rows. Assert no width factor, exact repeat/seed pairing, host gold absent from public records.
- [ ] Run `python -m unittest -v test_data` and retain missing implementation failure.
- [ ] Create transfer_study.py with qualified source pins, immutable JSON helpers and original stack/runtime seams. Create transfer_data.py `build()` returning PUBLIC/HOST_GOLD/GROUPS/FREE_PLAN/PROVENANCE; use sorted SHA256([981401001,'source',group]) first64.
- [ ] Add prepare.py inputs command; freeze actual native rendered prefixes from unchanged old free prompt with accurate-field amendment. Run test_data.

## 2. Fixed binding and free runtime

- [ ] Write test_entry.py and test_native.py: actual owner argv parsed by real collector, all48 NULLs before startup, reject wrong output, pinned selected adapters, original versus new prompt render parity, malformed final0 versus absentNULL, cost attempts versus completions.
- [ ] Run focused tests before implementations.
- [ ] Implement transfer_binding.py using original fixed4 selected verifier, no new selection. Implement collect.py exposing free-only CLI and actual qualified episode/run under explicit joint module aliases; audit all physical attempts separately from old paid-model flag.
- [ ] Implement owner.py readout-only lifecycle, one phase per fixed policy, releases in finally, planned48 and all physical-cost paths preserved even if phase expires. Test actual owner→service wrapper→config/descriptor with only Popen/network boundaries intercepted, plus actual collector composition under a bounded fixture.

## 3. Qualify and seal

- [ ] Run `python prepare.py qualify` in existing native environment with CUDA empty; record command, complete output and source pins. No broad tests/containers/model calls.
- [ ] Add DESIGN.md handoff and write READY only after source/input/selected-checkpoint closure and CPU qualification. Canonical identity must survive write/read.
- [ ] Fresh `python owner.py verify`; send exact READY hash/identity and focused test results to MAIN. MAIN alone reviews/launches.
