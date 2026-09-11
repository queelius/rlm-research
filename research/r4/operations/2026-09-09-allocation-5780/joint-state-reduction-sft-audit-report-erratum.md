# Erratum: joint-state reduction SFT audit

This additive correction preserves the original sealed report (SHA
`819575ff5180fe7956b7018ef6344e200efcf48fc1a568e52434578058fa4b90`) and its manifest.

In “Training and native evidence,” replace “exactly four Adam steps in every checkpoint of both
arms” with: **Each arm has four committed checkpoints. In both arms, the recorded Adam step matches
the checkpoint ordinal: checkpoint 1/2/3/4 contains step 1/2/3/4 respectively; the selected final
checkpoint is checkpoint 4.**

The original wording incorrectly described every intermediate checkpoint as containing four steps.
No outcome, mechanism ruling, cost, or interpretation changes. The authoritative underlying values
remain in `OPTIMIZER_AUDIT.json`.
