---
id: idea:harness-recursion-prior-art-boundary
date: 2026-09-12
status: literature_screen_not_implementation
related_questions: [rq:adaptive-decomposition, rq:harness-adaptation]
gpu_admission: false
---

# Compare what helpers can do, not just whether they exist

[Recursive Agent Harnesses, June11,2026, sections3.1–3.4](https://arxiv.org/html/2606.13643v1)
studies child agents with their own tools, planning and further spawning. It
contrasts script-driven parallel spawning with ordinary structured calls and
uses isolated child contexts with aggregated outputs. This makes child tool
access and the information returned to parents relevant comparison dimensions.
MAIN read these method sections and the introduction, not its complete evaluation
or implementation; no benchmark gains are imported as our evidence.

An important terminology caution: its broad contrast between RLM model calls
and full-harness recursion should not be repeated uncritically. The
[RLM paper, section3.2](https://arxiv.org/html/2512.24601v3)
explicitly distinguishes depth1 ordinary-model children from deeper RLM children.
Simply allowing children to use tools or recurse is therefore not enough to
establish a new architecture contribution. Our installed nano-RLM already has
recursive harness support; actual invocation and resulting behavior must be shown.

## A bounded future experiment

After the targeted-versus-broad MuSiQue comparison, preserve the same first helper
reports and compare a fixed small set of next actions: stop, ask a focused question
of the same helper, expose a larger input slice to that helper, or let it split
its slice once. Pair total calls and generated-token ceilings, record exactly
which original paragraphs reached each child, and keep final-answer quality
separate from intermediate fact recovery.

The question is which missing capability limits the answer: insufficient relevant
input, an unhelpful request, or inability to break down the local task. Learning a
selector among these actions becomes worthwhile only if the actions have different
outcomes on a repeatable subset of questions. Otherwise an RL router would be
learning from noise or an artificial reward. This proposal is conditional on the
current screen and needs frozen examples, seeds, per-action cost and a stopping
rule before GPU admission; it is not another queued infrastructure project.
