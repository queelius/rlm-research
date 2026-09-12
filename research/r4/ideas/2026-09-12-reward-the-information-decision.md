---
schema: research-idea-v1
created_utc: 2026-09-12T23:03:00Z
status: ranked_followup_with_interface_pilot_preparing
priority: high_after_current_dose_and_interface_checks
questions:
  - Can the helper choose a sufficient set of references without rewriting their contents?
  - Does reward for useful information teach selection better than reward for final copying?
  - When does an additional helper recover a missing choice rather than repeat existing work?
claim_level: hypothesis_not_demonstrated_method_or_novelty
---

# Reward the information decision, not unnecessary copying

Our latest reward update learned on its original examples: exact answers rose
from7/32 to17/32, with10 wins and no losses. All ten wins repaired final spaces
or line breaks after unchanged correct retrieval. The main unseen-example
panels stayed flat. This is evidence of local behavioral learning, not merely
a nonzero gradient, but it does not establish the more general ability we want.

The new table-decomposition pilot has a different failure. Helpers omit eligible
choices and miscopy fields. In its unqualified second attempt, using code to
look up the fields for the IDs already selected still cannot recover the right
global solution. The proposed interface experiment therefore asks whether
removing the copying burden changes the *selection itself*. Its baseline must
be the repaired third attempt, not a favorable comparison with a broken prompt.

## Immediate informative comparison

Keep each helper's full original input, model, seed and384-token limit. Change
only its output task from complete records to a set of IDs. Code resolves the
claimed IDs using public input tables; it must not silently remove ineligible
IDs, add omitted ones, or consult the gold relation to repair an answer. Apply
the same lookup to the old selected IDs for a fair selection comparison.

Measure exact eligible sets, recall, precision, malformed outputs, known cost,
and the correctness of deterministic recombinations. These are24 draws over
12 stages nested in four roots, not24 independent problems. Reduced output
length is expected; it is not a benefit unless the needed information survives.
The host combiner is supplied code, not a learned planner or a successful RLM
parent. A positive result justifies fresh roots and another task family.

## Primary research that informs the next reward experiment

MAVEN (July2026) trains an editable evidence memory with add, drop and link
actions. A frozen verifier estimates gold-answer likelihood changes, including
leave-one-out contributions, and assigns rewards to action spans after an
interface SFT stage. Its value is a learned proxy, not a proof of evidence
sufficiency; the paper's diagnostic coverage metric is also not logical
sufficiency. Our potential adaptation is to replace that proxy with exact
task checks where possible, then compare local coverage reward with global
decision preservation. [Primary methods, sections2–3](https://arxiv.org/html/2607.02073v1).

BAR-RAG (February2026) samples evidence sets, measures a frozen answerer's
success, and trains selection toward an intermediate success rate before
adapting the answerer. It filters uninformative questions during training,
while retaining all evaluation queries. This informs batch selection and
co-adaptation; it does not imply we should deliberately make deployment
evidence worse or optimize a half-correct final system. [Primary methods,
sections2.1–2.3](https://arxiv.org/html/2602.03689v1).

RSAT (May2026) combines structured-output SFT with group-relative training
for table answers and citations. Its main faithfulness measure uses the same
NLI model for reward and evaluation, which the authors acknowledge as a
limitation. The useful lesson here is to separate format validity, evidence
selection and answer correctness, not to treat a learned judge's improved
score as verified semantic progress. [Primary methods and limitations,
sections3–4 and6](https://arxiv.org/html/2605.00199v1).

These readings are method inspiration, not replications or endorsements of
their novelty claims. No associated code was cloned or executed for this note.
Exact reference resolution and programmatic arithmetic are established ideas;
the interface pilot alone would not constitute a new algorithm.

## Conditional next steps, not an automatic training queue

If the IDs-only interface creates valid but incomplete sets with meaningful
within-question variation, train the helper on fresh roots. Compare one fixed
local set reward (for example Jaccard overlap) with a global reward that checks
whether recombined choices preserve the correct optimum. Include an all-IDs
control and deliberately retained ineligible choices so recall-only shortcuts
cannot masquerade as learning. Evaluate both local validity and actual global
decisions on untouched root groups; do not select the best checkpoint on them.

If all variants remain incomplete with little useful contrast, teach an
explicit inspect/enumerate action by small verified SFT before RL. If selection
becomes reliable, add a bounded second helper only on a prespecified ambiguity
signal and compare with always-stop and always-delegate at equal compute.
That tests when another decomposition is worthwhile. A learned recursive tree
is a later question, not something our current fixed three-stage graph proves.

Compute shape: current interface24 calls on one A100, a few minutes with a
finite owner cap. A later RL feasibility batch can use8 fresh roots×4 draws,
one update and a fixed small readout; freeze the exact task, reward, seed,
splits, budget and checkpoint policy before admission. Do not build a large
training system until the action and reward actually supply useful contrast.

Evidence: `analyses/openai-mrcr-fresh8-rloo-training-readout-2026-09-12/`,
`analyses/b05-attempt002-contract-diagnosis-2026-09-12/`, and the active queue.
