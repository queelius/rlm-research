---
schema: openai-mrcr-sft32-t1-g4-mechanism-report-v3
status: TERMINAL_G4_AUDIT
---

# Checkpoint32 temperature-1.0 grouped rollout

Attempt-003 recorded 32/32 trajectories; 32 were scientifically
available and 27 were raw-exact. The fixed G4 reward vectors are
`[[1, 0, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [0, 0, 0, 0], [1, 1, 1, 1]]` and 1 complete groups are mixed. Attempts 001 and 002 are excluded
because their requests failed before the native endpoint.

The paired T0.5 screen used the same records and requested seed integers and returned 28/32 with
zero mixed groups. This remains a temperature treatment, not an independent seed replication.
Decision status: `INSUFFICIENT_G4_CONTRAST_REVIEW_DIVERSITY_BEFORE_EXPLORATION_CHANGE`. No optimizer is authorized.
