# Process-consistency screen implementation plan

> For agentic workers: execute inline using the executing-plans skill. The parent approved this bounded N3 screen; no new approval, GPU/model calls or frozen-input edits.

Goal: measure evidence observability and count-reward ambiguity without declaring a new trainable reward.

Architecture: one narrow read-only screen.py authenticates saved traces and projects exact question/label pairs. Pure check_map computes the frozen diagnostics. JSON outputs retain episode/context identity and nulls. Existing parser source is evidence, not a case-specific scoring authority.

Tech stack: Python standard library and pytest in the existing project environment. SPEC.json is the frozen scientific method. All new files live in this analysis directory; no core commits or shared-source changes.

- [ ] Add focused tests for count cancellation caught by an independent facet, unobservable incomplete/conflicting maps, exact JSON cardinality and semantic-return alignment. Expectations are hand-derived, not produced by the implementation.
- [ ] Implement screen.py strict matching/trace projection and tri-state map checks; run only focused CPU tests. No generated-code evaluation other than literal parsing of arrays.
- [ ] Seal SPEC/source/tests before new raw readout scoring. Authenticate development/readout inventories and normalized source-group separation. Score development first without tuning the frozen method, then readout once.
- [ ] Report coverage and discrimination separately, preserve raw source hashes/map evidence, and seal artifacts. If observation is weak, recommend the smallest explicit ID-to-label instrumentation; do not engineer a generic parser.

Implementation is complete only when the final MANIFEST.json exists; the plan remains unchanged after method sealing.
