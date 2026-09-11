---
schema: rlm-literature-decision-note-v1
id: "idea:state-interface-and-query-curriculum"
updated_utc: "2026-09-09T21:58:00Z"
status: exploratory_proposals_not_results
related_questions: ["rq:reduction", "rq:controller", "rq:sufficient-interface"]
read_depth: targeted_primary_methods_and_selected_source_only
---

# Separate state management, semantic decisions, and useful learning

The running experiments now give a sharper question than simply adding memory.
Actual observations make old predictions more likely to be used, but final accuracy
does not automatically improve. Historical action quotations without observations
mostly trigger new acquisition. [Our report and limits](../operations/2026-09-09-allocation-5780/state-content-factorial-audit-report.md),
[authoritative width-denominator correction](../operations/2026-09-09-allocation-5780/state-content-factorial-audit-report-erratum.md).

## Primary literature that informs the next tests

**Harness-1.** This retrieval agent stores and renders working state outside the
model. Its supervised stage teaches interface operation; subsequent RL uses a
terminal reward that includes several shaping terms, not answer correctness alone.
Its component removals are inference-time tests on trained weights, not independently
retrained matched harnesses. Read: main state/training methods and component-ablation
discussion, not the full63-page appendix or an independent results reproduction.
[Paper](https://arxiv.org/pdf/2606.02373).

Official code is cached at commit8ac4012167858f6478fb2a8fd840e4550e2af161. The
inspected context builder combines compact memory, recent actions/observations and
result summaries; budget reduction can remove older context or ultimately leave
only the minimal task. No downloaded code was executed, model fetched, or environment
installed. Full evaluation has additional backend requirements. Root code license is
Apache2; this does not settle separate data/model licenses.
[Pinned source and retrieval manifest](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/repos/harness-1-8ac4012167858f6478fb2a8fd840e4550e2af161.PROVENANCE.json").

**Harness-RL.** Revisited sections3.2–3.3 and training setup: it retains exact
per-call tokens, separates session visibility from execution dependence, and masks
nontrainable observations/roles. Its proposed action/argument gradient routing is
not what our joint SFT implements. The paper also uses process rewards; it does not
justify relabeling our terminal-only training or changing its objective mid-run.
This refresh extends the earlier07:22 triage; no repository was cloned or numerical
result independently reproduced. [Paper](https://arxiv.org/html/2608.29641v1).

**VERIFY-RL.** Read differentiation/curriculum methods, not a validated implementation.
The useful idea is to check that a proposed decomposition is useful and structurally
related. However, its product-rule strict-depth argument needs caution: its stated
depth of a product is the maximum factor depth, so a factor containing a composition
need not have smaller depth than the product. For example, sin(x²)·cos(x²) and each
factor share that depth. Do not import its universal strict-descent claim as a proven
verifier. This is our counterexample to the stated definitions, not a reproduced
benchmark result. [Definitions and theorem2](https://arxiv.org/html/2602.07559v1).

## Our proposed comparisons, not results from those papers

1. **Keep evidence usable.** On new root-context groups, compare the same actual
   predicted map as archived files, concise inline state, or an initial genuine tool
   observation. No gold repair, answer injection or automatic final submission. Keep
   source correctness, retrieval choice, faithful reduction and final accuracy separate.
   Candidate64 endpoints on one4B/A100,20–40min cap. Promote only an improvement
   beyond uptake on new context clusters; otherwise revise the state carrier.
2. **Test actual composition with tools.** The native purchase-join experiment is
   being implemented: same facts with Python present/absent, original records versus
   genuine complete partial reports. The host reducer is only a diagnostic ceiling.
   Candidate48 roots+24 source extractions,1800s cap. If tools solve the task, inspect
   executed aggregation before any claim of learned decomposition; if both fail,
   improve the task/interface instrument before scaling.
3. **Train decisions that vary with the question.** The proposed broad-count run
   was found to duplicate completed BROAD16 data/schedule. It is retired, not renamed
   into a new result. Replacement options vary aggregate operations and scopes or
   separately vary genuine acquisition starting states. Do not bundle both changes
   without an interpretable comparison. Candidate2–4h RL campaign, checkpoints every
   complete update and fixed paired transfer reserve. Require actual mixed rewards
   and held-out operator×scope behavior, not another loss curve or category substitution.

Shared lesson: a useful state representation can change what a model does without
changing whether the answer is right. Our contribution must establish where that
change matters, with controlled evidence quality and task success. Generic memory,
recursive harnesses, exact-token training logs and harness optimization all have
prior work; none is a standalone novelty claim here.
