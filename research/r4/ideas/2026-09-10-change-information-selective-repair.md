---
status: prospective_design_only
date: 2026-09-10
gpu_authorized: false
primary_new_calls: 12
---

# Change the information, not the number of checks

Repeated checks failed because they changed the sample without changing what the child knew or what
it was asked to represent. The ceiling's map was already 1129/1280 correct but 0/8 on exact J1.
Confidence review found 107/151 errors and repaired a net 40 labels, yet moved only one answer to
exact. In the two-sample study, agreement abstained on just 20/320 task-aware labels, agreed on 48
wrong labels, and changed task-aware absolute error in only one episode. Same-checkpoint stochastic
agreement is therefore weak evidence about correctness; it largely reproduces correlated mistakes.

The smallest experiment that introduces different information is a 12-call direct sufficient-
statistics interface. For each existing 32-record chunk, ask the frozen c32 child for two values per
public user: whether any record asks for target A, and the total public weight of records asking for
target B. OR the booleans and add the sums across chunks, then use the unchanged J1 rule. This removes
the unnecessary requirement to correctly name every one of six classes and tests whether the model
can expose the evidence the downstream computation actually consumes.

The exact 12 sealed full-label ceiling calls on the same chunks and seeds are the comparator. This is
minimal and paired, but historical rather than a new independent control. A clean pass requires at
least 7/8 valid episodes, 6/8 exact answers, four more exact answers than the sealed label-map route,
and lower absolute error in at least 6/8. At most 2/8 exact, or failure to lower error in at least half,
retires this interface. More than one malformed/unavailable episode triggers interface revision, not
an efficacy conclusion. One A100, 12 calls, 600-second cap, no root calls, retry, reroll, or fallback.

Second, use the already-preparing mixed-child ceiling rather than duplicating it. A mixed-trained
child genuinely changes verifier knowledge; after it closes, compare its complete-map, J1, repair,
and regression behavior against c32 before designing another selective pass.

Third, and only after the current RL continuation, add a matched TRAIN-only reference-child arm.
Evaluate both roots using the unchanged actual child. This isolates whether reliable training
evidence improves planning, but it is not deployable oracle inference. A provisional serial one-A100
additional cap is 3,600 seconds, with a 10-point protected correct-and-faithful promotion threshold
and explicit acquisition/retention non-regression.

The primary panel is eight nested episodes from four exposed clusters, and its comparator is shared
historical evidence. Public records, weights, users, and reducer semantics are allowed; host labels,
gold answers, old labels, confidence, and error identities are forbidden from prompts. TRAIN-only
reference labels must remain out of protected evaluation. No generalization or novelty claim is
available.

No actual human semantic review was performed for this synthesis. It uses sealed native metrics,
deterministic reducers, existing audit annotations, and previously recorded literature notes. The
associated YAML is the authoritative machine-readable question card.
