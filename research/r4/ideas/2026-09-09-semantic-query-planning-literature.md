# What semantic query-planning research changes about our next experiment

September 9, 2026. This is a bounded primary-literature/source review, not a
systematic survey or a claim to have reproduced the cited systems. It was prepared
while the accepted helper-uptake experiment used the A100. No accepted design,
model, data membership or outcome was changed by this review.

## Main implication

Filtering irrelevant records before asking a language model to classify them is
an established optimization, not a novel RLM contribution. Our adaptive pilot is
useful because it tests a prerequisite: can this small coordinating model choose
and execute an appropriate plan when the question changes? If it cannot, teaching
the interface may be a better next step than rewarding increasingly long attempts.

The potentially interesting connection is narrower: an accurate local classifier
can lose its usefulness when predictions are attached to the wrong records or
returned in a form the coordinator does not use. We have strong component evidence
and some root-training evidence, but have not yet demonstrated that connecting
them improves adaptive end-to-end answers. Generic planning, output IDs and
model–harness co-adaptation are not firsts.

## Closest inputs to a small experiment

| Primary source and actual reading scope | What it contributes | Consequence for our work |
|---|---|---|
| [LOTUS, version 3](https://arxiv.org/abs/2407.11418v3), abstract read | Semantic operators and query optimization under cost/accuracy objectives. | Treat filtering, joining and aggregating model outputs as established baselines. Do not claim the mere operator vocabulary is new. |
| [Larch](https://arxiv.org/html/2606.07923v1), introduction/background and selected method sections read | Learns filter ordering through cost/selectivity models or a lightweight policy. | Cheap-filter-first and learned ordering are established. Its learning policy is not a root-language-model weight update; our RLVR should not be described as a reproduction. |
| [Compositional Online Learning for Semantic Data Processing Systems](https://arxiv.org/html/2608.27244v1), abstract and selected methods/discussion read | Connects caching, filter ordering and model routing, with lightweight learning alongside expensive model calls. | Charge all layers and their quality assumptions. Its large combined speedup discussion is analytical, not evidence that our proposed combination was measured. |
| [NL2Pipe](https://arxiv.org/html/2606.04641v1), abstract/introduction/related work and methods3.1–3.4 read | Separates data/query grounding, a backend-independent plan and API-specific executable code. Supplies schema/previews and API examples. | Compare a truthful public data sketch with interface teaching; later separate planning from code generation only if the pilot identifies that bottleneck. |

These papers do not establish that our model needs their architecture or that a
larger harness improves its answers. That is an experimental question.

## Source acquisition and limitations

The official NL2Pipe repository was cloned outside Git-managed research source at
`/project/alex_phd/research-cache/repos/nl2pipe-9abf5cbfe98654453bb1073cc80a9750f78c02e5`.
Commit9abf5cbfe98654453bb1073cc80a9750f78c02e5, MIT license; roughly2MB. The adjacent
PROVENANCE.json records the paper/code link, exact tree, hashes, retrieval date,
read ranges and intended experiment. README, license and the complete UTF-16
requirements were read; selected planner/reference-generation source was inspected.
No repository code was executed, no environment installed and no datasets fetched.

The requirements include Windows-specific local paths and dependencies. This is
source inspiration, not a ready one-A100 reproduction. No claim about its complete
implementation or empirical reproducibility follows from the selected inspection.

## Ranked, conditional follow-ups

1. **Teach the interface before teaching a plan, if uptake is the bottleneck.**
   Use the active matched uptake comparison to decide. A small native-action SFT
   warm-up could teach how to read public records, call the helper and decode its
   actual return type, without supplying a complete filter-and-count solution.
   Keep SFT-alone and later RL gains separate. The existing training-options memo
   supplies a feasible, but not yet reserved or accepted, dataset plan.

2. **Give the coordinator a truthful sketch, if it fails to inspect the input.**
   Compare ordinary environment inspection with a deterministic public schema and
   metadata summary. Use the same API, root/child weights and query/context pairs;
   never summarize hidden labels or expose the reference program. A minimal screen
   is24–48 whole-RLM episodes on one A100, approximately15–30minutes under declared
   caps. Charge sketch CPU work, extra prompt tokens and later model calls; do not
   confuse an informative sketch with a token-matched causal control. Promote only
   if selection/use or accuracy/cost improves across context groups. Retire if it
   merely restates a fixed algorithm or has no observable uptake.

3. **Train query-sensitive decisions, if the free policy has usable variation.**
   Hold input fixed while the requested subset changes; include global questions
   where filtering must not discard relevant records. First use terminal exact-
   answer rewards and independently observe decisions. If both plans already
   answer correctly but one wastes calls, a separately declared cost objective may
   be needed. Binary reward cannot reliably prefer two equally correct plans.
   Do not silently introduce process rewards or cost penalties into an accepted
   binary-reward campaign. Constant answers and subgroup skew need explicit baselines.

4. **Test correspondence where it matters, without banning a better solution.**
   Global class totals can remain correct when labels are permuted. Queries joining
   predicted labels to public record metadata expose a real consequence of wrong
   correspondence. Compare fixed all-record operators as diagnostic baselines, but
   also allow the free coordinator to filter first; avoiding the binding problem
   is a legitimate planning success, not cheating. Keep component mapping accuracy,
   aggregate accuracy, selected-record coverage and complete call costs separate.

None of these proposals displaces the four already accepted successors. Their
priority and exact design depend on the uptake, role, news and adaptive outcomes.
A broad training gain was not demonstrated by the completed16-update campaign:
the final64-record composition comparison stayed5/24. That limits optimism about
simply extending its recipe; it does not prove adaptive planning cannot be learned.
