---
id: leaf-mnli-positional-anchor-binding-v1
status: prospective_exploratory
date: 2026-09-10
planned_calls: 96
---

# Positional anchors for late-record MNLI binding

The earlier host-join position diagnostic found that all three label-only
reference conditions fell from 77–84% accuracy on positions 1–16 to 34–37% on
positions 17–48. The split was selected after that outcome and the same eight
research-exposed contexts are reused here. This is a mechanism probe, not an
independent replication.

Cross visible reference (`wrong`, `alien`, `aligned`), an explicit zero-based
input `row` field (absent/present), and output format (the existing label-only
array versus exact ordered `row`-then-`label` objects). Preserve every original
record, premise, hypothesis, gold, visible ID, requested tag, and record order.
Input-row-present inserts only `row`; the exact output grammar fixes rows 0–47.
No host reordering, partial salvage, repair, retries, tools, or gold exposure.

Use all 8×3×2×2=96 conditions, paired seed 996217101+context index across each
12-arm block and mechanically rotated dispatch. Fixed released Qwen3-4B
Instruct2507, no adapter/tools/thinking, temperature.5, top-p1, max3072,
context8192, four workers and90seconds/request. Outer1800/work1650/owned1770
includes180startup,30harvest,90release,30finalization and30outer margin. Save
every request/raw response/result and all precreated NULLs; each response is an
incremental checkpoint.

Primary is the paired late-position (17–48) row-first minus labels-only effect
when input row is absent, averaged across all three references and eight
contexts. At least10 points, positive in at least6/8 contexts, with no
availability loss promotes an output-anchor follow-up. A larger effect with
input-row present is mechanism evidence but is not required for a useful
output-only cue. Input-only gain is also actionable. Report all factorial simple
effects, total and first16 accuracy, wrong/aligned interaction, native validity,
NULL bounds and cost. The package changes instructions/schema/generated tokens;
it is not a pure attention manipulation, and emitted row tokens may steer the
next label.
