---
status: proposed_not_executed
date: 2026-09-13
priority: after_singleton_replication_and_paired_credit_readout
question: Can a small learned router recover most singleton gains with fewer helper calls?
---

# From useful fixed decomposition to deciding when to decompose

Trigger: singleton176 improved exact sets4/12 to10/12 versus either whole
control, at3.75x list input cost. Independent audit found real matched-valid
decision improvements. This is six contexts and separable public policies,
not broad generalization or learned recursion.

Smallest next comparison after fresh replication: fixed k helper refinements
chosen by observable parent uncertainty versus random same-k choices. Preserve
the entire parent vector, replace only actually queried candidate decisions,
and count parent plus helper cost. Gold may evaluate the policy but cannot
choose queries. An oracle selector is an upper-bound diagnostic only.

Prospective dimensions: k=1/2/4, complete-set exact, corrected versus damaged
candidate decisions, input/output tokens, physical calls and elapsed time.
Use new cases and reserve an untouched evaluation split before fitting any
confidence threshold/router. Agreement and token likelihood are imperfect
uncertainty signals, not calibrated probabilities of correctness.

Expected GPU shape: one4B native service on current40GB A100, a capped small
generation panel of parent calls plus allcandidate helper calls can support
explicitly offline policy comparison; fresh online execution is needed before
claiming runtime savings. Anticipated minutes, external cap20minutes. A dataset
with interacting constraints is a later necessity: independent filtering does
not establish useful multi-level planning.

Promote if targeted refinement beats random at the same query budget on new
contexts without systematic omissions. Revise if confidence cannot identify
errors. Retire the cheap-router direction if even best-case saved-output
selection has insufficient headroom; do not relabel posthoc oracle gains as RL.

## Relevant prior art, checked September13

[DecomposeR, arXiv2605.30824v1](https://arxiv.org/abs/2605.30824v1)
separates graph-structured planning from answering and assigns training credit
to explicit planning components. This makes “train the planner separately”
prior art, not a novelty claim for our project. Abstract inspected only; method
and reward definitions must be reviewed before adoption.

[Context-Folding, arXiv2510.11967v1](https://arxiv.org/abs/2510.11967v1)
uses branching sub-trajectories and retained summaries, with RL process rewards
for decomposition/context management. Abstract inspected only. Our immediate
question is narrower: whether cheap local refinements recover selection errors.
We have not implemented their algorithm or independently reproduced results.

No repository downloaded or executed for this note. These leads must inform
comparisons, not displace a ready GPU job.
