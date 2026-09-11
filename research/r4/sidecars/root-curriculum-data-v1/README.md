# Candidate data for a broader root-only curriculum

Data/design only. No trainer, coordinator, model binding, acceptance, or GPU launch is included.

Read the [ranked proposal](../../ideas/2026-09-09-broader-root-curriculum.md) first. It distinguishes broader root aggregation, true length extrapolation, requested-category transfer, and optional sentiment task transfer.

- `PUBLIC.json`: candidate context text and count questions. Runtime allowlist is context.text and task.question only; routing IDs are host metadata.
- `HOST_GOLD.json`: host-only source records/labels/counts; never pass this artifact into an interpreter or prompt.
- `GROUPS.json`: host-only context membership, source partition, exact UTF-8 context hashes.
- `CANDIDATE_SCHEDULE.json`:16 data-schedule slots, three tasks each;24 training contexts each visited twice with different targets. This does not bind rollout seeds, optimizer or model choices.
- `PROVENANCE.json`: named historical exclusions, exact source hashes, duplicate/source counts, licenses and explicit unknowns.
- `prepare_data.py`, `test_data.py`: CPU-only reproduction and focused data audits. Preparation writes once; tests recompute in memory without changing frozen data.
- `MANIFEST.json`: final candidate-data closure, published only after verification. It is not a launch READY or training recipe.

There are58 disjoint contexts containing3,136 unique source groups. Train max64; length transfer128/256. All TREC training/validation/composition/length groups were child-SFT training examples; separately named leaf-validation/test strata were not gradient-training examples but have previous leaf-evaluation exposure. SST96 excludes768 named previous leaf-study groups; unknown outside-history/pretraining remains.

Run focused verification with `CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/rlm/bin/python -m unittest -v test_data` from this directory. Runtime prompt/tool/token-budget qualification is intentionally pending a reviewed experiment recipe.
