---
id: leaf-mnli-positional-anchor-new-context-v1
status: prospective_exploratory_replication
date: 2026-09-10
planned_calls: 192
---

# Fresh-context positional-anchor factorial

Replicate the complete visible-reference (`wrong`, `alien`, `aligned`) by
input-row (`absent`, `present`) by output-form (`labels_only`, `row_first`)
factorial on 16 newly selected MNLI48 contexts. Do not select only the winning
matched-row package.

Use four contexts from each of government, slate, telephone, and travel. Each
contains 16 complete three-label premise groups. Eligibility uses labels only
to require complete conflict-free groups; ranking uses a fresh fixed hash over
genre and normalized premise-group identity. Exclude premise groups and
normalized premise/hypothesis texts in all named prior MNLI DATA, PUBLIC,
GROUPS, and PLAN inventories, including the latest 16-context field-order
replication. “New” means disjoint from those named inventories, not model
pretraining or unrecorded work.

Keep the prior row values 0–47, relation definitions, exact grammars, prompt
wording, base Qwen3-4B model, no adapter/tools/thinking/prefix cache,
temperature 0.5, top-p 1, max 3,072 output tokens, 8,192 context, four workers,
and 90-second request cap. Use one fresh paired seed per context across all 12
arms and rotate dispatch order. Retain all 192 calls, raw responses and NULLs;
no retry, repair, reordering, or outcome-dependent replacement.

Primary is the input-row by output-row interaction on positions 17–48,
averaged over all three references: `(present row-first - present labels-only)
- (absent row-first - absent labels-only)`. At least +10 points, positive in
at least 12/16 contexts, with no availability loss promotes the mechanism.
To call the matched package a practical general remedy, present-row row-first
must also beat present-row labels-only in each of wrong, alien, and aligned.
Report all 12 cells, early/late/total effects, reference interactions, exact
row contracts, NULL bounds, and physical cost. The old output-only gate remains
a secondary unchanged diagnostic.

Use outer/work/owned caps 1,800/1,650/1,770 seconds, including 180 startup, 30
harvest, 90 release, 30 finalization, and 30 outer margin. This is exploratory
fresh-context evidence, not a pure-attention, novelty, or confirmatory claim.
