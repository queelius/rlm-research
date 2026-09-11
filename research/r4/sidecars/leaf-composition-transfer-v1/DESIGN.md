# New-context composition transfer after leaf SFT

Frozen design before collection, 2026-09-08 21:52 UTC. This is an exploratory
composition test, not an untouched-source claim or evidence of discovered planning.

Use the official TREC test partition already frozen by trec-leaf-split-provenance-v1:
489 normalized question groups disjoint from the local SFT train/validation groups.
Sort by SHA256 of the fixed namespace/seed981260300/group ID, take the first384,
partition sequentially into six disjoint64-record contexts. No selection depends on
prediction or gold-label outcomes. Source test labels determine host-only scoring.
The same source questions also occur in the leaf component's pre/post test; the
composition and aggregate questions here are new, not the underlying question source.

For each context ask two fixed queries: count human-being questions, and count
numeric-value questions. Count over all64 records. Synthetic Date/User metadata is
deterministic and independent of the label. Preserve the demonstrated Date/User/
Instance layout so this first comparison changes context contents, not parsing API.
Each task exposes all six possible labels and the same definitions-enabled recursive
example used by leaf-role-routing-v1. No labels, counts or answer maps are in context.

Two fresh paired seeds per task, original root/original child versus original root/
validation-selected SFT child:48episodes,24pairs,12tasks,6independent context groups.
Keep exact prompts/root weights/sampling/budget/runtime paired. Root temperature0.5,
full-support decoding,2048token call cap, depth1/no compaction;4paired workers,
1800second study cap, atomic per-episode checkpoints and explicit partial-run records.
The separate role driver owns trusted routing; do not infer roles from message text.

Primary: strict final count correctness with no tolerance, using the existing
predeclared final-line parser. Mechanism: actual child routing/recursion, distinct
records covered, canonical classification, aggregation consistency and final copying.
Costs include all roots/children; execution, routing, grammar/format and truncation
errors remain separate. Use document clusters, not repeatedseeds as independent data.

Promising outcomes justify new source datasets, varied layouts and more genuinely
adaptive queries. Gains confined to this matching prompt/layout support only the
narrow claim that a trained child component can improve an example-guided harness.
