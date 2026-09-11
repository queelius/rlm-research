# MNLI visible-reference disambiguation40

Question: is the fixed-output wrong-visible penalty instruction-sensitive, driven by association
with a visible different record, or dependent on a local identity anchor?

Eight mechanically selected MNLI contexts (two each government/slate/telephone/travel) are new
relative to the named-inventory scan at freeze, not globally or pretraining unseen. Each context
has five exact-output arms under one paired seed: `wrong_legacy`, `wrong_explicit_slot`,
`alien_legacy`, `alien_explicit_slot`, and `aligned_explicit_slot`. The premise/hypothesis text,
display order, requested-tag vector, label options, output schema, sampling, and seed are identical
within block. Wrong uses label-blind left17; alien uses unique visible aliases absent from requested
tags and length-matched per position; aligned makes the visible ID equal its local requested tag.

Legacy uses the exact predecessor wording. Explicit wording naturally states that `requested_tag`
is an opaque output address, not a record reference, and that classification uses the premise and
hypothesis in the same object. No artificial filler is added. Exact token counts and differences
are frozen and reported. Explicit-minus-legacy is an instruction-sensitive component, not proof
that ambiguity caused the behavior. Alien-minus-wrong tests sensitivity to a visible wrong
referent. Aligned-explicit minus alien-explicit tests the behavioral benefit of a local identity
anchor; it does not reveal an internal binding mechanism.

Primary: whole-contract-gated displayed-label correctness over all 384 planned labels/arm and eight
paired context clusters. Secondary: native availability/NULL bounds, exact tag/order fidelity,
actual prompt/completion tokens, and named/third diagnostics on unequal-gold wrong arms. No repair,
reordering, rerolls, or outcome-selected subset. Completed malformed output is observed zero;
authenticated infrastructure absence is NULL.

The 10-point and 6/8-context thresholds are practical pilot continuation rules, not evidence of
equivalence or absence. Apparent closeness on eight contexts is not equivalence. This adaptive
exploratory control is not confirmation. One released Qwen3-4B base, no adapter/tools/thinking,
temperature .5, max output3072/context8192, four workers, request90s, outer1200/work1080/owned1170,
40 preplanned NULL slots. MAIN alone may launch.
