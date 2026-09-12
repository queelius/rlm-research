---
schema_version: rlm-research-idea-v1
id: idea:budget-state-and-training-frontier
created_utc: "2026-09-12T11:29:00Z"
status: conditional_not_gpu_admitted
questions: ["rq:rl-effective-feedback", "rq:adaptive-decomposition"]
evidence_scope: primary_methods_sections_read_not_reproduced
priorities: [budget_visibility, calibrated_checking, informative_training_examples]
---

# Make useful decisions possible before asking RL to learn them

Our current evidence separates three problems: extra checks can damage correct
answers; uniformly rewarded attempts provide no relative learning signal; and
code can be cut off before it becomes executable. The following are proposed
followups, not changes to live or sealed jobs.

## 1. Tell the controller what resources remain

AnySearch injects budget state during an initial RL phase and later removes that
support while varying training budgets. Its reward couples correctness and tool
cost. Its reported training uses eight H800s, so we should borrow a small control,
not attempt its full search-training setup. Methods 3.1–3.4 and Appendix A.1 were
read. [AnySearch, September 1, 2026](https://arxiv.org/html/2609.00813v1).

Our proposed test: keep the same code-generation caps and compare an implicit
limit with an explicit numeric remaining-budget message. Current numerical V2
asks for a complete cell within the turn limit but does not state the numeric
limit in its prompt. First let V2 finish; if truncation persists, freeze a small
new panel and test visibility with otherwise matched prompts and compute caps.
Measure finished cells, useful executed observations, final answers and token
cost separately. Budget-aware generation is prior art; an RLM-specific claim
would need reliable effects across tasks, not just repairing an undersized pilot.
Expected one A100, about 10–15 minutes; exact seed and cap remain to be frozen.

## 2. Supply calibrated evidence about when checking helps

Calibrate-Then-Act makes uncertainty and action costs explicit. Its file-reading
task distinguishes inexpensive format probes from executing a whole solution;
the QA task compares direct answering with retrieval. Task definitions 3.1–3.3
were read; a full implementation audit is not claimed.
[Calibrate-Then-Act, revision May 15, 2026](https://arxiv.org/html/2602.16699v3).

Our proposed test: after measuring complementary-solver headroom, compare a
default-answer-preserving verifier with and without reliability information
estimated on a separate calibration set. Evaluate on new records, include
agreement controls, and charge for calibration and all checker calls. This is
more informative than another contextual vote: our fresh routing test sent
eight already-correct answers to checking and missed seven shared errors.
Promote only a net quality/cost gain over the strong original helper. No arbiter,
calibration examples, threshold or GPU owner is yet selected. Expected one A100,
10–20 minutes for a first comparison, not a training campaign.

## 3. Choose examples that still teach the model something

Adaptive Data Scheduling groups training examples semantically and tracks
examples near the policy's success boundary. Its motivation directly matches
all-correct/all-wrong groups losing relative reward contrast. It tests a wider
math-training setup, not our category-classification task. Methods 3.1–3.4 and
experimental setup 4.1 were read.
[Learning at the Right Pace, June 21, 2026](https://arxiv.org/html/2606.22305v1).

Our proposed test comes after the broader AG pilot: compare uniformly sampled
training requests with requests selected using a disjoint development collection
to favor mixed rewards. Count the selection collection in the compute budget;
do not select using heldout answers or discard same-reward groups after drawing
the final training batch. Keep heldout label coverage fixed and include a
matched SFT control if RL remains weak. Start without embedding/clustering
infrastructure. More gradient-bearing samples are only an intermediate metric;
promotion requires a reproducible heldout improvement. One A100 suffices; a
one-update paired pilot should target under 30 minutes after the fast AG path
qualifies, with a separate immutable experiment specification.

The budget-message idea, calibrated checking, and difficulty-aware training are
not claimed as new inventions. Their value here is to distinguish explanations
and identify whether an RLM-specific combination warrants a fresh confirmation.
