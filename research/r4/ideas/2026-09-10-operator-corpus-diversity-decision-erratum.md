---
schema: research-note-erratum-v1
corrects: idea:operator-corpus-diversity-decision
original_sha256: a3dcafa4f1d7567757682fbd415a8aae450d92dc26064e83abc584861a8f7eb5
actual_write_utc: "2026-09-10T00:29:29Z"
status: additive_correction
---

# Operator-corpus note corrections

The original note's `as_of_utc: 00:38` was later than its actual filesystem write time,
`00:29:29Z`; the latter is authoritative. Its recommendation compared 72×6 with prior evidence,
not a randomized 72×6-versus-36×12 study. A trained-versus-unchanged readout can estimate the
72×6 package effect, but cannot causally attribute any gain to diversity rather than repetition.
A direct breadth/repetition causal question would require both matched training arms.

For the initially approved CPU proposal, widths are fixed at 4 and 16. The original mention of
4/8/16 was not an authorized inventory, and its exact “180 child acquisitions” forecast therefore
is not frozen. Recompute child-call and token budgets from the final fixed trajectory plan before
READY; keep failed genuine child outputs and do not repair them.
