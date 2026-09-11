---
id: question-sensitive-sft-new-corpus-replication-v1-implementation
status: ready-for-main-review
date: 2026-09-10
---

# CPU implementation handoff

The isolated package freezes 128 live-inventory-new TREC-train groups into eight contexts and 72
teacher coordinates. Capture uses the qualified genuine-c32 collector; the corpus verifier requires
all 72 distinct episode-local attempted child records and retains wrong child labels. The trainer is
the qualified six-full72 objective with seed `992173003`, fixed24 start, fresh Adam, 504 trainable
LoRA tensors, and checkpoint6 only. The only new readout is the existing metadata72 plan; its public
contexts, prompts, IDs, and seeds are unchanged, while the root binding points to the new checkpoint.

The live freeze scan found 79 manifest rows, 309 eligible groups, 2,902 used seeds, 7,944 public IDs,
and 176 native IDs. The approved design's earlier aggregate was 74/373/2,750/7,724/172. The exact
79-row live list and all source hashes are in `inputs/PROVENANCE.json`; this sidecar excluded itself.
Because the earlier observation retained no row list, the five-row diff is not guessed. The approved
rule allowed the live freeze census, and selection ranks the resulting eligible set once without
rerolling.

The owner enforces the approved 4500/4470/4320-second clocks and 1500 capture, 1200 training, 1500
readout, and 120 finalization allocations. Capture incompleteness blocks training; training failure
blocks readout. All 72 readout slots are predeclared. Completed malformed/wrong responses are zero;
attempted or unstarted missing endpoints remain NULL. The cost ledger unions capture and readout
physical records and does not call missing usage zero.

CPU qualification covered the SHA selection and collisions, exact 72 plans, metadata prefix replay,
collector CLI, owner capture→trainer→readout composition, qualified training-environment import, and
fixed24 binding. It intercepted model/service/gradient boundaries and made no scientific calls.

- READY identity: `182cac7a458a0eb2b1a082b3b303faeaea31e473507cf0ae3fb7a341aae64348`
- READY file SHA-256: `a701a8d57245a3c5ba9f691ec68cb67de4a3523096a5d684e8858db1bf9d521e`
- Closure: 12 local source/design/test files and 5,809 input/transitive pins
- Focused native tests: 6 passed in 11.67 seconds
- GPU/service calls: 0

`PRESEAL_LIVE79_DRAFT_READY.json` preserves the superseded first seal made before the census-drift
annotation and final binding correction. MAIN alone owns acceptance and launch.
