---
id: question-sensitive-sft-new-corpus-attempt-001-audit
date: 2026-09-10
status: terminal_infrastructure_failure_no_scientific_readout
---

# New-corpus QS SFT: attempt 001 audit

This attempt produced no SFT result. It completed and sealed all 72 planned teacher trajectories,
then failed before model load or the first Adam update. The inherited owner used a helper that
deliberately removed `CUDA_VISIBLE_DEVICES`; the unchanged trainer therefore stopped at its
single-GPU preflight. No checkpoint and no metadata readout exist, so this attempt says nothing
about whether the new corpus reproduces the original QS6 improvement.

The capture is usable immutable input for an additive completion: 72/72 teachers, one genuine c32
acquisition per teacher, and the complete corpus receipt validates every pinned file. The ledger
records 72 physical model requests represented by 288 role-wire records, with 90,171 prompt and
17,855 completion tokens and no unknown usage record. There were zero readout requests. These costs
remain charged to attempt 001 and must not be counted again as new acquisition in recovery.

The owner ran 1,249.817 seconds and ended incomplete but released, with no active service. The parent
exited 1 without timeout after 1,250.328 seconds and reported an empty GPU. The original owner,
terminal, corpus, and parent artifacts remain untouched.

I authored the experiment package and later audited the failure. The method and semantic-reader
receipts were frozen after launch but before any readout; since no readout occurred, no semantic
endpoint scoring was possible. The recovery decision is infrastructure-driven, not outcome-driven.
