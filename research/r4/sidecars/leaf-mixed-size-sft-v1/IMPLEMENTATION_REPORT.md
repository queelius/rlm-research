# Mixed-size SFT CPU handoff

Both curricula are prepared with immutable source/recipe/data and exact original converted FP32 adapter provenance. No GPU calls were made during preparation. Existing SFT, root-TIS trainer, role-routing service and prior evaluation sources were not changed. The parent owns launch and independent critical-path review.

| Quantity | A:1/5/16/32 | B:1/5/16/64 |
|---|---:|---:|
| Epoch arrays |1641,1640|1621,1620|
| Optimizer steps |103+103=206|102+102=204|
| Actual question exposures |10,130|10,130|
| Supervised target tokens |47,368|47,288|
| Padded input tokens, microbatch2 |2,748,078|2,719,578|
| Maximum native training sequence |1351|1933|
| Fixed final checkpoint |checkpoint-0206|checkpoint-0204|

Each epoch assigns1266/1267 records per nominal size. A/B bucket memberships are identical; only the final bucket's array segmentation differs. Residual arrays are recorded in each MANIFEST: size5 residual1 then2, size16 residual2 each epoch, A-size32 residual18, B-size64 residual50. Every training group appears once per epoch, with independent deterministic epoch shuffling and separate array-order shuffling. Equal record exposure is not equal computation or optimizer steps relative to the prior all5 SFT.

Verification: five focused CPU tests passed in5.06 seconds, including an actual tiny mixed-length PEFT optimizer update, unchanged base, exact one-step state, masked prompt loss, balanced group allocations, shared A/B bucket membership, fixedepoch2 selection despite worse validation, and position-quartile scoring. Ruff passed for the curriculum driver/tests. A final read-only CPU audit independently loaded both prepared artifacts, authenticated all source/data/base/adapter hashes, checked every actual epoch's unique5065 group IDs and authoritative gold labels, prompt masks, native terminators, and recomputed manifest counts; cross-A/B real bucket memberships matched. No truncation was used.

Reuse is narrow: authenticated original SFT native renderer, loss, collator, exact adapter audit, checkpoint/RNG/cursor code and fixed5 evaluator. The new loop replaces hardcoded64-step epoch assumptions and validation checkpoint selection with dynamic206/204-step schedules and fixedfinalepoch2. Atomic checkpoints occur every16 global steps and at epoch boundaries; explicit resume restores exact optimizer/RNG/cursor. Training optimization cap remains3600 accumulated seconds, excluding model load, validation and serialization as in the prior experiment. Full wall time will be longer and must be recorded by the parent launcher. All trained weights are retained before final evaluations.

The final run automatically monitors original fixed5 validation300 each epoch, evaluates fixed5 test489, and evaluates six64-record composition prompts at greedy1024. Position quartiles report strict correct counts and entity-prediction/gold counts; array validity and truncation remain separate. Optional `evaluate --arm A --size 64` (orB and1/5/16/32) provides a489-group size-specific report from the fixed final checkpoint. No postprocessing repair or alternative reward path exists.

## Backend probe and serialization caveat

PROBE_READY.json was published earlier so the parent could immediately run six greedy vLLM calls and later the same existing selected c32de weights through HF. Probe inputs/source remain frozen. CPU request/native-render preparation passed; two harmless E501 lines in probe.py were deliberately left after freeze. The curriculum source itself passes Ruff.

Subsequent parent observation established three semantically identical but token-distinct tool serialization orders: vLLM outer type/function and inner name/description; HF probe outer function/type and inner description/name; original SFT outer type/function and inner description/name. Thus neither equal tool semantics nor equal token count means exact prompt-token identity. The frozen probe truthfully records HF-versus-vLLM ID mismatch. No active probe was edited to conceal it.

Training and fixed5 evaluation retain the original SFT native serialization. Final64 uses the frozen HF-probe IDs, so existing selected-SFT HF versus A/B HF is a same-prompt comparison; it is not an exact-input backend comparison. Both training-template and actual evaluation prompt IDs are retained in prepared transfer64 rows. These rows are explicitly evaluation-only, with supervised input/label fields removed to prevent a false causal-prefix claim. A future exact-provider-token HF control can be additive.

Source SHA256: driver.py `1a063bedc6882354736e822595472d8269211007aa92ff3fa8f3d487b7c5b708`; test_driver.py `ba419e84c1f62339a6ad6a9db9583d5e3f9df524d6573128311e938cf95cdcb5`. Readiness files contain full recipe/data identities and commands. No source changes occurred after A readiness; B used the same frozen implementation.
