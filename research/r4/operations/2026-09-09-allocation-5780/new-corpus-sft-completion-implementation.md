---
id: new-corpus-sft-completion-implementation
date: 2026-09-11
status: ready_for_main_review
---

# New-corpus SFT completion recovery

The original run is preserved. It captured all 72 teachers, then its training subprocess failed in
18.5 seconds before model load because the inherited CPU-only command helper removed
`CUDA_VISIBLE_DEVICES`. There was no optimizer step and no scientific readout.

The additive sidecar
`sidecars/root-question-sensitive-sft-new-corpus-completion-v1` is ready. It verifies and reuses the
immutable complete72 corpus, launches the unchanged trainer with the assigned GPU visible, requires
the exact six-checkpoint lineage, and only then performs the unchanged metadata72 readout. It makes
no new teacher calls and does not rerun either comparator.

Budget: 3,000 seconds outer, 2,970 owned, 2,850 work; training 1,200, readout 1,500 including service,
finalization 150, release reserve 120, margin 30. Invalid completed outputs remain observed failures;
missing infrastructure remains NULL. Physical usage fields retain known/unknown counts.

READY file SHA-256: `35c205b3f84e247c1a0af855053b2dc1da0394961a58f08c5bdc90cd400b9a87`.
READY identity: `80c6477d0873d1225adad9df7f80be8600d83a999e80373e906dd3deae62bc49`.
Five focused tests passed; actual training import, native collector CLI parsing, source corpus closure,
and owner verification passed. `READY_PRESEAL.json` preserves the first pre-seal snapshot.
