# Approve a small source-cue timing comparison

Main, September 9, 2026 at09:02UTC. Approve CPU implementation of the48-call
candidate in `ideas/2026-09-09-output-cue-order-design.md`, not a GPU launch.
Its CPU feasibility recorda8fad088659314433e562e41ed3713b6a0be9c6be7b9ae088a6a67e9aa90afa6
tested all48 prospective requests with the installed native tokenizer/XGrammar:
24order pairs have identical full physical prompt IDs; each designated64-object
order is accepted and the opposite order rejected. Maximum input plus3072output
is5910. No model/GPU call or prior outcome read was used for this preparation.

Use a new `sidecars/leaf-output-cue-order-v1`, the original fixed c32de child,
two TREC/two SST contexts selected by the documented lowest-context-index rule,
their first prior disjoint-q presentation, three tag rules and seeds981282011/
981282021. These are exposed explanatory contexts, not a new-data replication.
Reuse the existing single-adapter component collector/service/lifecycle. No new
environment, model, graph/training path, retry, answer rescue or shared edit.

Resolve the candidate's general counterbalance description before observations
as follows. Index the four selected contexts locally0..3, TREC then SST, each
in original index order. For each context c and repeat r, rotate the arm list
[meaningful,ordinal,constant] left by(c+r)mod3 and reverse if(c+r) is odd.
For original arm index j, enqueue the adjacent field-order pair tag-first then
label-first if(c+r+j) is even, reversed otherwise. Thus each matched condition
has opposite order-first exposure across the two seeds. Four collector workers;
retain actual start/completion/cache records, without claiming perfect balance.
This is a prospective dispatch refinement, not a changed source selection.

Within each tag rule retain exactly the same model-facing messages/tools/seed:
both use "the keys tag and label". Only the schema's property/required ordering
changes. Bind actual ordered schema and serialized-body hashes; canonical sorted
JSON and dict equality are not sufficient to authenticate property order. Do not
deduplicate distinct ordered grammars with an insensitive key. Repeat the exact
CPU native prompt/grammar proof and scoped seed check before final freeze.

Score each arm against its intended physical field order, then the same displayed
record's label. A valid label-first object is not a malformed tag-first object
to be repaired. Explicitly validate duplicates/extra fields, cardinality, exact
tag and assigned key order from raw pairs; keep original bytes and do not
relabel, move answers between records or hide violations. Any reuse of the old
tag-first semantic scorer must follow honest validation of the new contract and
not misreport changed raw output. Predeclared previous-record agreement remains
a secondary descriptive diagnostic with chance/multiplicity caveats, never a
repaired primary score.

Caps: collection600seconds, shared work780, owned900including120cleanup,
outer930. One absolute clock includes owned preparation/startup; disclose
pre-main import overhead under the outer cap. Meaningful-minus-ordinal differences
and their field-order interaction are primary by task/context, not pooled3072
independent labels. Constant contrasts, whole64 and class counts, invalid/nulls
and physical costs remain visible. Generic field-order sensitivity already has
prior work; this screen only tests the timing of a supplied source cue.

Focused TDD/verification and independent review should address those material
comparison seams while current GPU jobs run. Publish READY last. Main alone
accepts a successor after the ready whole-RLM and new-task comparisons, and can
reprioritize it if their results identify a more informative use of the allocation.
