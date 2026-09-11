---
schema_version: rlm-research-idea-v1
id: idea:harness-literature-method-refresh
created_utc: "2026-09-09T20:29:00Z"
status: literature_method_refresh_not_ready
related_questions:
  - rq:controller
  - rq:adaptive-communication
  - rq:continuation
  - rq:reduction
gpu_jobs_authorized: false
sources:
  - url: "https://arxiv.org/html/2512.24601v3"
    version: v3
    read_scope: "Training setup, Appendix A, Appendix B and selected native RLM/depth prompts; not all43pages or figures."
  - url: "https://arxiv.org/html/2606.13643v1"
    version: v1
    read_scope: "Abstract, harness architecture and evaluation setup; not full appendix or independently rerun scores."
  - url: "https://arxiv.org/html/2607.15524v1"
    version: v1
    read_scope: "Abstract, introduction and objective/search-method sections; not full numerical evaluation."
  - url: "https://arxiv.org/abs/2608.24302v2"
    version: v2
    read_scope: "Primary abstract only."
new_code_executed: false
new_model_or_dataset_downloads: false
---

# Refresh the method, not just the headline

This extends the earlier [official-code inventory](2026-09-02-official-rlm-research-experiments.md)
and [07:22 literature triage](2026-09-09-binding-and-harness-literature-triage.md).
The current GPU jobs and frozen evaluation definitions are unchanged.

## What the primary sources actually support

The original RLM paper trains on filtered multi-turn teacher trajectories, with
each root turn supervised against its full preceding history. Its appendix reports
300 updates at batch64 and48 H100-hours. It also reports repairs to teacher template
errors, differences in useful prompts across models, excessive child calling, and
problems distinguishing continuation from final output. Our four-update authored
pilots are not a reproduction of that training scale or diversity. The relevant
lesson is to teach useful actions in their actual preceding states, while preserving
the distinction between curated training data and unmodified evaluation outputs.
[RLM v3](https://arxiv.org/html/2512.24601v3).

Recursive Agent Harnesses gives children full agent environments and returns their
results through structured artifacts. Its evaluation, however, uses a separate
answer-extraction model call and published aggregate baselines; the authors lack
the baselines' per-instance scores. Matching the backbone alone does not give us
a paired, budget-matched replication. Its extracted-answer score is also different
from our unchanged strict native-final score. We should borrow artifact interfaces
as candidate designs without importing its attribution or efficiency claims.
[RAH v1](https://arxiv.org/html/2606.13643v1).

Recursive Harness Self-Improvement optimizes prompt-level roles, instructions,
communication contracts and workflow using local comparisons with prior revisions.
Its method explicitly distinguishes the local predecessor objective from global
comparison over possible harnesses. The application uses LLM preferences over
generated repositories, unlike our exact verifiers. Local revision is a useful
search heuristic, not a guarantee of generalization or monotonic true improvement.
[RHI v1](https://arxiv.org/html/2607.15524v1).

VideoHarness-RSI searches executable context constructors around a frozen video
model. The abstract distinguishes weak and strong starting harnesses and mentions
matched cumulative visual-token controls and transfer. This is adjacent evidence,
not a text-RLM reproduction; no implementation or full results were inspected here.
[VideoHarness-RSI v2](https://arxiv.org/abs/2608.24302v2).

## Our decisions and bounded candidate experiments

The current source-ID work already has extensive controls, including negative
specialized-training results. Do not restart another ID-SFT run before the queued
role/tool pilot establishes what remains after correcting the leaf interface.

For roots, the [new wording audit](../analyses/root-map-contract-clarity-live-2026-09-09/REPORT.md)
shows why the search objective needs execution evidence: agreement with a supplied
map can coexist with loading it and then replacing it. The pending corrective-SFT
comparison will distinguish learning a calculation from learning to reach its
prerequisite state. Neither overall accuracy nor training loss alone identifies
that distinction.

The smallest next harness-search screen would freeze four explicit state/wording
packages, keep actual fields accurate and hold model, observations and final
scoring fixed. Use a small complete paired development matrix, then a separately
selected new-context comparison of the chosen package against a strong clear-prompt
baseline. Proposed envelope: one A100,64 development endpoints,2400seconds inclusive;
checkpoint every returned endpoint and preserve all costs and failures. This is
not READY, and the four packages/seed/data must still be specified before any call.

Promote only if gains survive new contexts and reflect useful evidence use or
lower measured cost at comparable correctness. Revise if improvement is only format
or avoidance of a misleading description; retire a candidate if a simple clear
baseline already matches it. Include candidate generation and failed candidates
in search cost. Bootstrap resampling of the same development cases cannot turn
adaptive selection into fresh confirmation.

Higher priority remains the bounded [state-representation feasibility test](2026-09-09-state-use-to-continuation-tests.md),
conditional on authentic controlled states. A fresh root given a quoted transcript
is an explicit restart condition, not the original native conversation; an honest
weaker comparison is preferable to disguising token-history substitution as an
unchanged continuation. No changes to the active SFT or accepted partition run
are authorized by this note.
