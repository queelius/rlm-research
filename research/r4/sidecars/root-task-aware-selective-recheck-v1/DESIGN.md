---
status: prospective_frozen
date: 2026-09-10
planned_physical_calls: 48
---

# Task-aware two-sample selective recheck

This sidecar implements the approved result-informed brief exactly: confidence and
confidence-times-local-public-J1-sensitivity selections, each with independently seeded samples A
and B. Each selection/sample uses the same 12-call 16/32-record repacking, yielding 48 physical
calls and 320 reviewed labels per selection/sample. The task-aware score is uncertainty percentile
times maximum one-label public-reducer sensitivity; neither selection, prompt, nor tuning reads
host gold.

Two policies are derived from shared calls. `single_a` overwrites every selected label with sample
A. `agreement_abstain_a_b` overwrites only A/B agreements and explicitly retains the first-pass
label on disagreement. A missing whole batch makes its dependent policy/episode NULL; an available
invalid whole batch makes it observed-invalid. There is no retry, fallback, or partial salvage.

The eight episodes are nested within four exposed clusters. A/B-derived policies and selection
comparisons share physical calls and are not independent. The 48-call physical cost is reported once;
the hypothetical standalone single policy's A-only 24-call cost is also reported without pretending
the shared consensus evidence is free.

