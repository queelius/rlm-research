---
schema: openai-mrcr-fourneedle-balanced32-transfer-design-v1
date: 2026-09-12
status: CPU_DATA_FREEZE_ONLY
---

# Balanced four-needle transfer panel

Question: on 32 prospectively frozen, previously unqueried official MRCR four-needle
contexts—eight for each requested ordinal 1–4—does the fixed LR1e-4 root checkpoint
outperform the fixed procedural-SFT checkpoint32 under the same terminal-strip-disabled
runtime?

Selection uses a SHA256 namespace rank and no model outputs. It excludes exact source rows,
exact user/assistant core pairs, and target↔core-answer overlaps against explicit frozen
manifests for the original 48 short records, long16, fresh8, and the prior ordinal-transfer16.
Selected records are mutually disjoint under the same tests. The official source bytes,
question, answer, ordinal, and prefix remain unchanged. The panel requires the original
short band and a target answer within the fixed 2048-token action cap.

This is same-task transfer to fresh project contexts, not a new benchmark, independent
confirmation, or a pretraining-clean claim. LR1e-4 was chosen after an exposed held-panel
audit, so the comparison is exploratory and development-selected. Higher exactness must be
split into retrieval/procedure changes versus output-boundary-only changes.
