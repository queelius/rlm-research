# AG News96 implementation decision

Main decision, September 9, 2026 at 08:38 UTC. CPU preparation is approved;
this document does not authorize a GPU launch or change the accepted successor
order. The active broad-root training run and its two waiting successors retain
their original inputs, budgets and authorities.

I read the complete AG News design
`ideas/2026-09-09-agnews-identity-weight-screen.md`
(SHA256 d42483488566928501f22d8a899165ecb902a41b9a05c08411ad1cfda5bca6c0),
its acquisition/feasibility evidence, and the primary dataset card. The proposed
96-call grid is a useful new-task and two-fixed-weight comparison of the
source-matching output effect. It is not a replication on fresh SST contexts:
the original SST proposal failed its membership check and remains preserved.

Implement the exact candidate grid, selection, seed, order, prompt, grammar and
budget in that design in a new external `sidecars/leaf-identity-agnews-weight-v1`
directory. Reuse the proven component collector, dual-adapter service and owned
lifecycle, without editing their frozen sources. Repeat the bounded seed check
before freeze. Bind full source/data/model/config and physical-prompt provenance.
The pinned Parquet and host gold must remain outside model-visible payloads.
Retain all complete news text; no crop, selection adjustment or output repair.

Keep one absolute work clock (1080 seconds), collection at most 900 seconds,
owned envelope 1200 seconds including 120 seconds cleanup, outer 1230 seconds.
An acceptance file and exact predecessor operation will be prepared separately
after the focused CPU qualification. No actual model call is part of preparation.
Tests should address material comparison risks: displayed-record alignment,
weight-only paired-body differences, disjoint numeral mapping, fixed coordinate
count/order, strict schema failures, null versus invalid accounting and immutable
source binding. Avoid broad test suites and new service abstractions.

The output-ID contrast is the complete instruction/grammar representation package,
not proof that instruction alone or a hidden reasoning mechanism caused it. The
four source contexts are the sampling clusters. Report both weights separately,
their interaction, class-count cancellation and actual physical cost. Do not
pool labels as independent observations or promote this component result to
whole-RLM improvement. License uncertainty remains in the acquisition metadata.

Use the writing-plan/TDD/verification guidance in a bounded research-first form:
freeze the actual comparison before observations, test the material seams, and
let preparation overlap useful GPU work. The user's standing authorization is
the design approval; no interactive approval checkpoint is required.
