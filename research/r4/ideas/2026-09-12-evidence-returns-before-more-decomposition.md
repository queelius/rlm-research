---
schema: research-idea-v1
created_utc: 2026-09-12T19:45:00Z
status: refined_design_cpu_preparation_not_gpu_admitted
priority: after_qualified_sft_rl_rollouts
question: Does returning selected source passages preserve useful relations better than returning helper summaries?
evidence:
  - ../analyses/musique-task-directed-followup-independent-2026-09-12/outcome/REPORT.md
  - ../analyses/musique-task-directed-followup-independent-2026-09-12/outcome/MECHANISM_REPORT.md
claim_level: exploratory_mechanism_screen
---

# Ask helpers to select evidence, then preserve what they selected

## Why this is the next decomposition question

Our first focused-follow-up screen did not improve exact answers: stopping,
broad follow-up and focused follow-up each solved the same one of12 questions.
The full-source control solved three. Inspection found a planner asking the
right question of the wrong half, a lost relation between two reports, and a
final answer contradicting evidence that a report had supplied. These are
different problems; simply adding more calls does not distinguish them.

The most informative small follow-up may change what a helper returns, not the
number of helpers. A helper can identify passages worth retaining. The harness
can pass those passages unchanged to the answering model instead of requiring
the helper to paraphrase every important relation correctly.

## Proposed smallest comparison

Keep the existing question-blind two-way paragraph partition. Each selection
call receives its same source half and the task, and returns at most two
paragraph IDs. Two separate summary calls then see only those selected source
paragraphs. This additional isolation matters: a summary generated from the full
half might carry facts from unselected paragraphs and confound the comparison.
Run these four helper calls once per question and share their outputs.

The summary condition gives the final model the selected IDs and helper accounts.
The source condition gives it the same selected IDs and their exact original
paragraphs, retrieved by trusted harness code. Neither condition receives the
answer or gold support labels. Invalid or out-of-half IDs are recorded as model
selection failures and supply the same explicit empty-evidence/error payload to
both final branches; never replace them with gold IDs or silently pick alternatives.
The final prompt instructions, model, seed, output cap and grader remain fixed.

The counterfactual branches share the same acquired helper outputs. Their natural
policy costs differ: three calls for selection plus a verbatim-source final,
five for selection, summarization and a summary-based final. Their final input
token counts also differ. Report both actual shared physical calls and natural
per-policy costs; do not call this a token-cost-matched representation effect.
If verbatim passages help, a later matched-budget selection study must separate
the benefit of more retained text from that of avoiding paraphrase loss.

An initial mechanism screen can use all12 existing contexts, explicitly exposed,
with72physical calls (48shared helper calls plus24finals). Do not select just
the two full-source successes. Freeze the source-selection contract and seeds
before querying. Fixed preparation caps are science700seconds, owner950,
external1050 on the
single4B A100 service; checkpoint every call and use no training. Implementation
and GPU admission remain pending; CPU preparation has been assigned, but this
document does not authorize an automatic run. Fixed seed namespace202609220000
uses16offsets per question, with the same final seed in both branches.

## What would change the plan

If selected IDs omit the needed sources in both arms, the next bottleneck is
selection/routing, not summary fidelity. If both contain the needed sources but
verbatim improves answers, try a fresh prespecified panel before a claim. If
verbatim also fails with complete source support, focus on combining relations
or a more capable answering model. Exact support-set overlap is a diagnostic,
not proof that the answer used its evidence faithfully.

This is a fixed call graph, not learned recursive stopping. A later adaptive
controller could choose whether to request another passage, another helper
question, or an answer, but that requires new data and an actual policy test.

## Prior art narrows the claim

[Where Facts Go Missing, v3](https://arxiv.org/html/2607.22448v3), revised
August19, distinguishes deterministic pipeline loss from model behavior using
boundary observations. Its attribution study deliberately injects some faults,
and some behavioral labels are heuristic; the paper notes missing raw main-sweep
artifacts. It therefore motivates instrumentation, not importing a prevalence
estimate into our runs. Its future work already includes passing references.
We read the abstract, attribution methods and limitations, not its full code.

The [official RLM LocalREPL implementation](https://github.com/alexzhang13/rlm/blob/main/rlm/environments/local_repl.py),
inspected September12, already provides an answer object whose readiness signal
captures an environment value. Our own Responses runtime also has `FINAL_TEXT`.
Returning an environment value, by itself, is not our invention. The inspected
GitHub main URL is a moving reference, not a pinned dependency for this proposal.

Our prospective contribution must be an informative controlled comparison of
selection, information preservation, and learning—not a claim to have invented
references, exact returns, or pipeline-level error attribution. The strongest
connection to RL is whether preserving verifiable intermediate work supplies a
more useful learning signal and improves complete answers on new material.
