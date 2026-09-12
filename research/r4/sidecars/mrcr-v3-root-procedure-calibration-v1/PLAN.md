# MRCRv2 Root Procedure Calibration Implementation Plan

**Goal:** Build one calibration-only 8-row × 4-rollout MRCRv2 owner over the
proven native root/RLM and released no-adapter service, with no optimizer.

**Architecture:** Freeze one externally mounted shared context plus 32 task
coordinates. Reuse the qualified MRCR task/harness and no-adapter service lifecycle;
add only immutable input preparation, native-call checkpoint observation, exact host
scoring diagnostics, and a bounded owner.

**Spec:** `analyses/mrcr-v3-root-procedure-calibration-prep-2026-09-12/REPORT.md`

## Global constraints

- Eight frozen rows and seeds `202609121401`--`202609121404`; one shared context.
- Qwen3-4B no adapter for root and child; T=0.5, top-p=1, top-k=-1, min-p=0.
- 2,048 tokens/call; current qualified runtime supports six total trace turns, not
  independently six root turns when children are enabled.
- Owner cap 900 seconds, external cap 1000; no retries, optimizer, or GPU launch in prep.
- Official scorer is source-extracted from pinned `eval_hub`; diagnostics are additive.

## Task 1: Frozen data, task and metric contract

- [ ] Add failing fixtures for row/hash inventory, one-context identity, prompt/gold
  separation, exact coordinate seeds, official `rfind` behavior, and strict-prefix
  diagnostics.
- [ ] Implement `study.py` and input preparation minimally.
- [ ] Run the focused fixtures green.

## Task 2: Actual native request and trace checkpoint contract

- [ ] Add failing fixtures for an actual taskset construction, exact ModelContext
  sampler/alias, six-turn/max-depth configuration, and native response token evidence.
- [ ] Implement `collect.py` using the existing MRCR task/harness and raw WireTrace,
  with per-call start/result and per-episode immutable files.
- [ ] Run the focused fixtures green.

## Task 3: Bounded owner and immutable seal

- [ ] Add failing fixtures for no-adapter binding, exact 900-second cap, attempt path,
  service release, and deadline-censored accounting.
- [ ] Implement `owner.py`, `prepare.py`, and the narrow context-mount wrapper.
- [ ] Run all focused CPU tests with CUDA hidden, verify the closure, and write READY
  only if the six-turn semantic limitation is accepted explicitly.

