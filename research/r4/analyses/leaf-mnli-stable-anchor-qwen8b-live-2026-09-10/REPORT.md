---
status: complete_independent_native_audit
date: 2026-09-11
study: leaf-mnli-stable-anchor-qwen8b-v1
planned: 144
available: 144
null: 0
decision: promote_fresh_context_replication
---

# Stable output keys transfer to Qwen3-8B

The stable-key advantage reproduced strongly within Qwen3-8B on the exposed 16-context panel.
On the harder final 32 labels of each prompt, labels-only achieved 484/1,536 (31.5%), sequential
numeric keys achieved 1,313/1,536 (85.5%), and opaque keys achieved 1,245/1,536 (81.1%). Thus the
paired gains over labels-only were +54.0 and +49.5 percentage points. Both gains were positive in
all 16 contexts, with no availability loss. The prospective rule therefore says to promote a
fresh-context replication; it does not claim that this exposed-panel run is itself fresh.

Sequential keys outperformed opaque keys by 68/1,536 labels, or 4.4 percentage points. This is
evidence that stable correspondence matters much more than human-readable label names, while also
showing that arbitrary opacity is not free. Across all 48 labels per response, accuracy was 45.2%
for labels-only, 85.4% for sequential keys, and 81.6% for opaque keys.

The exact reused 4B coordinates show the same pattern descriptively: late-label accuracy was 34.2%,
85.4%, and 84.9% for labels-only, sequential, and opaque respectively. Relative to 4B, the 8B
sequential-key gain over labels-only was 2.7 points larger, while the opaque-key gain was 1.2 points
smaller. This is not a clean capacity comparison because model weights, tokenizer, and rendered
tokenization all change; no 4B calls were rerun.

All 144 planned calls were physically attempted, returned, uniquely identified, native-authenticated,
available, and contract-valid. There were no NULL or observed-invalid endpoints. Native usage was
594,075 input tokens and 74,910 output tokens; cached usage was reported as zero and no usage fields
were unknown. The run took 521.10 seconds end to end. Provider billing was not measured.

The main limitation is dependence: 48 labels and three reference variants within each context are
not independent observations. The panel was already research-exposed, and structured decoding
fixes grammar and order. The result supports a robust output-interface effect across two sizes in
one model family, not a general claim about model capacity, unseen data, or unconstrained output.

Machine-readable plotting values are in `FIGURE_DATA.json`; complete endpoint evidence, cost counts,
context effects, missing-outcome bounds, and the exact 4B join are in `AUDIT.json`.
