---
status: approved_cpu_implementation
date: 2026-09-11
planned_root_episodes: 216
---

# Fresh-input three-policy question-sensitive SFT evaluation

Select eight new 16-record contexts from the frozen 2,000-group TREC-train pool after excluding
every group named in recorded root PUBLIC, GROUPS, TASKS, or plan inventories. Freeze the inventory
scan before selection. Rank the remaining group IDs only by a new namespace hash, select 128, and
never rerank or replace them after computing gold.

The preliminary feasibility probe reported 245 eligible groups because it inherited the original
QS preparer's intentional self-skip. The independent scanner includes that original QS corpus and
freezes the corrected union: 1,819 excluded and 181 eligible. This correction occurred before any
selection or gold computation; 181 still supports the fixed 128-group design.

Port the exact changed-metadata transform used by the prior transfer panel onto these new source
groups: users u4–u7, weights 8–15, protected thresholds 13/25, and the same nine operator families.
Metadata, layout, order, seeds, and native IDs derive from public identifiers, never gold. Compute
gold after selection with the two trusted question-sensitive oracles and retain every zero and
nonzero task.

Compare exact fixed24, original-corpus SFT6, and new-corpus SFT6 policies on the same 72 tasks with
the same fixed c32 child: 216 new root episodes, three serialized services, no training, no retries,
and a 5,400-second outer cap. Primary effects are each SFT policy minus shared fixed24, paired over
all 72, composed 48, primitive 24, eight contexts, and zero/nonzero gold. The direct two-SFT contrast
is secondary.

These groups are new to the recorded root evaluation/training inventory, not globally unseen. They
come from TREC train; their source catalog and likely examples were exposed to c32 child training
and may have been seen in base-model pretraining. This isolates new root input groups under the
existing changed metadata, not independent task-family or child generalization.
