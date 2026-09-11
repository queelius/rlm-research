---
id: mnli-positional-anchor-binding-96
status: draft_for_main_approval
date: 2026-09-10
calls: 96
gpu: one_A100_40GB
outer_cap_seconds: 1800
launch_authority: MAIN_only
---

# Can explicit row anchors preserve late-position MNLI binding?

## Question and motivation

In the completed host-identifier-join study, all three label-only reference
conditions began at 77–84% accuracy over positions 1–16 but fell to 34–37% over
positions 17–48, with a decline in every one of eight contexts. Tag-first
aligned output stayed near 83% throughout. The first-16/remaining-32 split was
chosen post hoc, so this is a prospective mechanism probe on the same exposed
pilot contexts—not a replication or a causal conclusion.

**Question:** Can a fixed per-position row anchor retain correspondence late in
a 48-record answer, and does matching that anchor to an explicit input row field
reduce the extra penalty from a misleading visible record identifier?

## Frozen factorial

Use the same eight host-join contexts, record order, premise/hypothesis text,
host gold, visible `id`, `requested_tag`, wrong shift-17 mapping, aligned mapping,
and alien dictionaries. Cross:

- visible reference: `wrong`, `alien`, `aligned`;
- input row: absent versus integer `row: i` added to every displayed record;
- output: the existing exact 48-string label-only array versus an exact ordered
  48-object array `{"row": i, "label": ...}` with `row` first and fixed to
  integers 0 through 47.

This is 8 × 3 × 2 × 2 = **96 calls**, one call per cell and context. Use proposed
paired seeds `996217101` through `996217108`, one seed shared by all 12 arms in
each context; a named-catalog scan must confirm them unused before input freeze.
Rotate the 12 arm orders mechanically by context; do not select or reorder
contexts by prior accuracy.

The input-row-present representation is exactly each existing record object
with `row` inserted as the first field; all other fields and bytes remain. The
input-row-absent arm retains the existing object. The label-only instruction is
the prior natural instruction unchanged. The row-first instruction is:

> Return exactly 48 JSON objects in one array, in displayed record order. Each
> object must have exactly the integer field row followed by the string field
> label. At output position i, copy that displayed record's row integer exactly
> into row. For label, use exactly entailment, neutral, or contradiction. No
> additional text.

For input-row-absent, “copy that displayed record's row integer” becomes “write
the zero-based displayed position i”. No filler is added. The exact schemas fix
every row constant and field order. A row-first output is usable only when the
whole ordered schema is satisfied; no row-based reordering or repair occurs.
The labels-only host join remains positional and runs only after a complete,
authenticated 48-string array.

## Estimands and scoring

Primary is displayed semantic accuracy at positions 17–48, the range fixed from
the earlier post-hoc diagnostic. Report total 1–48 accuracy and positions 1–16
separately. For each visible-reference condition estimate:

1. row-first minus labels-only at input-row absent;
2. row-first minus labels-only at input-row present;
3. the input-row × output-row interaction; and
4. each effect's wrong-minus-aligned contrast.

Alien is a control for an unrelated visible identifier, not a neutral or
equivalent reference. Report eight context-level paired contrasts, all cell
counts, and the wrong/aligned interaction; do not treat 384 labels per cell as
independent. A completed malformed/invalid output is observed zero for all 48
positions. Missing or native-inconsistent output is NULL with planned-denominator
bounds. Preserve actual tag/row fidelity, prediction distributions, finish
branch, native IDs/tokens, and cost. No partial-array salvage, reordering,
resampling, answer repair, or tool execution.

## Runtime and interpretation

Reuse the qualified released Qwen3-4B Instruct2507 no-tools/no-adapter service,
native template, temperature 0.5, top-p 1, max 3,072 output/context 8,192, four
workers, and 90 seconds/request. Use 1,800 seconds outer, 1,650 work, and 1,770
owned, including 180 startup, 90 release, 30 harvest, 30 finalization, and 30
outer margin. Every response is an incremental checkpoint; all 96 NULL rows are
precreated and no coordinate is retried.

The intervention bundles instructions, input representation, schema, and
generated anchor tokens. A gain cannot by itself prove attention, instruction
ambiguity, or semantic binding, and fixed row tokens may steer subsequent label
generation. Promote to fresh contexts only if row-first improves late accuracy
in at least six of eight contexts without lower availability and the improvement
is larger when matching input rows are present. If only row-first helps, revise
toward output-token steering; if only input rows help, revise toward input
position marking. Retire this harness direction if neither main effect improves
late accuracy by a practical 10 points and context signs are not coherent.
