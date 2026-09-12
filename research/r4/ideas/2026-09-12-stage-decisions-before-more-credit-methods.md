---
schema: research-idea-v1
created_utc: 2026-09-12T22:26:00Z
status: ranked_followup_not_implemented
question: Can we learn a useful inspection or delegation decision when final-answer training mostly changes copying?
priority: after_current_rloo_readout_and_verifiable_report_pilot
related_questions:
  - rq:rl-effective-feedback
  - rq:decomposition-stability-and-composable-returns
primary_sources:
  - https://arxiv.org/html/2602.16165v1
  - https://arxiv.org/html/2607.07548v1
---

# Teach and measure the decision that is actually missing

## Why this direction changed

Our first final-answer RL gain reversed under fresh decoding seeds. New mixed
groups provide a larger gradient, but their verified contrast still concerns
copying and stopping, not choosing what to inspect. A generic instruction to
inspect the input produced no actual inspect-then-use behavior in32 reviewed
attempts. We should not infer that another credit formula alone will produce
an action that is absent from the sampled alternatives.

The B05 pilot first asks whether independently produced reports can create
useful differences in final success. Its original parent sees the full source;
a proposed report-only counterpart will separate source access from reliance
on helpers. True-source correctness and consistency with displayed reports
must remain separate. These are four-root feasibility tests, not learned plans.

## Primary research that helps frame the next experiment

[HiPER, February18 version1](https://arxiv.org/html/2602.16165v1) explicitly
represents continuing or changing a subgoal, the subgoal itself, and the next
environment action. One autoregressive model emits these fields; it is not
simply a larger planner paired with a separate executor. Its PPO-style method
uses learned high- and low-level value estimates and credit across subgoal
boundaries. This suggests making an inspect/continue/delegate decision visible
before trying to optimize it. The estimator's unbiasedness statement depends
on value/bootstrapping assumptions; it is not a guarantee for our capped
token-importance weighting. MAIN read sections4.1–4.3 and the relevant
appendix unbiasedness conditions, not the complete proof or implementation.

[Think Big, Search Small, version1](https://arxiv.org/html/2607.07548v1)
separates delegation, execution and a fixed answerer whose input excludes
agents' reasoning and raw passages. Its targeted executor SFT retains useful
single-search behavior and teaches second searches only when a one-search
counterpart fails. This motivates paired demonstrations of genuinely useful
inspection or repair, with retention controls. Its evaluation excludes some
no-delegation cases, so its findings should not be generalized into a rule
that every task needs delegation. MAIN read the controlled design, training
filter and evaluation setup in sections3–4.1. No repository or model was run.

## Smallest decision-relevant follow-ups

1. Finish the current fixed RLOO readout. Retain ties and regressions; do not
   choose a favorable seed or panel to rescue an improvement claim.
2. Run the verifiable source-visible/report-only comparison. Preserve every
   malformed report and unsupported combination. A parent can be correct
   despite disagreeing with a wrong helper, or consistent with a wrong helper
   while failing the original task. Measure both, plus calls and tokens.
3. If useful repair headroom exists, freeze an inspection-versus-continuation
   comparison at the same observable state. Teach only model-authored actions;
   never label a hidden host answer as an observation the model actually saw.
   Keep successful ordinary routines in the training mix. Compare a fixed
   inspect-every-time rule, a fixed continue rule and a learned choice.

An initial choice screen could use8 contexts with two continuation seeds per
action (32 continuations), one A100 and a10-minute cap. This is a proposal,
not an admitted run. Freeze actual states, seeds, reward, available actions and
checkpoint policy before sampling. Promote only when an available action
reliably repairs a real failure on new contexts; if all choices fail or a cheap
fixed rule dominates, improve the available action or retire the chooser idea.
Training a complicated selector before checking that headroom would waste
both GPU time and interpretability.
