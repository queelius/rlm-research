---
title: Cross-model stable output-anchor check
status: prospective
date: 2026-09-10
---

# Question

Does the large 4B advantage from a stable output key persist in the released Qwen3-8B model?

# Fixed comparison

Reuse the exact 16-context, 48-record user prompts, keys, schemas, seeds, and sampling settings from the sealed 4B stable-anchor study. Run only three conditions on Qwen3-8B: labels only, sequential numeric keys, and opaque stable keys (144 new calls). The 4B calls are not rerun.

The primary summaries are strict whole-contract label accuracy and paired context differences for stable-key conditions versus labels-only. Native absence or unverifiable responses are NULL, never zero; completed malformed answers are observed failures. Preserve native token IDs, bodies, usage, and all physical records.

This is a same-family cross-model check, not a pure capacity intervention: model weights, tokenizer, and rendered prompt tokenization change. The public model card documents `enable_thinking=false`; the experiment retains the earlier study's temperature 0.5/top-p 1 sampling rather than adopting the model card's recommended sampling defaults. The exposed 16-context panel is paired exploratory evidence, not a fresh-context replication.

# Decision rule

Promote a fresh-context 8B replication if both stable key forms beat labels-only on the context-paired estimate without an availability loss and the direction is positive in at least 12/16 contexts. Otherwise revise the cross-model generality claim; this small panel cannot establish equivalence or absence.
