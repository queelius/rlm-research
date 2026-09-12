---
schema: exploratory-research-question-v1
id: rq:category-guidance-versus-weight-learning
created_utc: 2026-09-12T15:26:00Z
status: deprioritized_after_source_prompt_review_not_gpu_admitted
priority: low_unless_a_distinct_calibration_hypothesis_is_frozen
parent_question: rq:rl-effective-feedback
---

# Did RL learn category conventions that a clearer instruction could supply?

## Source review changes the decision

The actual shared prompt already defines all four categories and asks for the
primary topic. In particular, it defines Business through companies, markets,
finance, trade and the economy, and Sci/Tech through science, technology,
computing, engineering, space and research. The proposed wording below is
therefore mostly a small definition revision, not supplying missing guidance.
Its expected information gain is lower than initially assumed. Do not launch
this as a generic "clearer prompt" control or begin a wording search. Revisit
only with a specific, train-derived calibration hypothesis and a frozen test.
Source: `sidecars/helper-unseen-generalization-panel-v1/build_panel.py:prompt`.

The initial proposal is retained below to make this revision explicit.

Two eight-update RL seeds corrected almost the same news labels on the first
512-example panel. Most corrections move commercial technology stories from
Business to Sci/Tech. Both seeds also introduce the same two Business errors.
This is evidence of stable task-specific learning, but it may partly resolve
an ambiguous category boundary rather than improve general classification.

The inexpensive alternative is a clearer category instruction. Test a small
two-by-two comparison: starting versus fixed RL helper, each with the original
instruction versus the same short definitions of all four categories. Reuse
the original-condition results only with exact data/runtime provenance.
Keep all articles, B4 groups, output grammar, temperature and endpoint fixed.
Do not alter instructions after seeing this comparison's outcomes.

Candidate definitions, to freeze before any new condition is queried:

> World covers international affairs, politics, conflict and major public events.
> Sports covers sporting competition, teams, athletes and sporting transactions.
> Business covers the economy, markets, financial performance and commercial affairs.
> Sci/Tech covers scientific research, technology, engineering and technical products.
> Choose the category that best describes the article's main subject.

These definitions are a research intervention, not authoritative dataset rules.
They were motivated by the already examined first panel; that exposure must be
declared even if evaluation uses separately frozen official-test examples.
They may worsen ambiguous cases. Do not relabel benchmark gold to favor them.

If guidance closes most of the baseline–RL gap, a narrower interpretation is
that training acquired a useful category convention. If gains remain or combine,
the weight change contributes something beyond these particular instructions.
Either result still concerns a single helper task, not learned decomposition.

Smallest useful screen: two additional 128-call/512-article evaluations on the
separately frozen official-test panel, against its existing original-prompt
starting/RL arms. Approximate single-A100 workflow is 15 minutes, including two
model loads; use measured caps rather than claiming isolated GPU compute.
Report paired corrections/regressions, per-class changes, unknown answers,
request-cluster uncertainty and token costs. No repeated prompt search on that
panel: a later revision requires separately declared exploratory data.

Decision: prepare only after higher-priority controller and fixed four-arm
generalization studies are ready. This is not a substitute for the supervised
comparison or a new default prompt.
