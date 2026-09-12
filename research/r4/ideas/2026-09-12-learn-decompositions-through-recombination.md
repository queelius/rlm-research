---
schema: research-idea-v1
created_utc: 2026-09-12T21:47:00Z
status: ranked_future_pilot_not_implemented
priority: after_current_rl_replication_and_literal_inspection
question: Can reusable intermediate alternatives make decomposition decisions learnable from sparse terminal rewards?
source_scope: primary_methods_read_no_external_code_execution
---

# Teach the choice of decomposition, not only its final wording

Our fresh MRCR attempts now provide contrast for accurate copying, but the two
literal-selector failures have no successful alternatives. The MuSiQue helper
experiments have mostly changed source coverage, wording or citations, without
reliable recovery of new evidence joins. These results motivate a separate
experiment in which a decomposition decision has measurable alternatives.

## Primary methods that change the next experiment

[DecompRL, July2 preprint, methods2–3](https://arxiv.org/html/2607.02390v1)
separates a decomposition policy from independently conditioned implementations.
It reuses sampled implementations in different combinations, evaluates complete
solutions, and trains with leave-one-out multi-sample objectives. Its main
training alternates the two policies, and its reported advantage is principally
high-budget search, not a promise of better single-attempt answers. The paper
uses large distributed compute; a small local pilot should test the mechanism,
not pretend to reproduce that scale. This is existing prior art, not our new
algorithm. MAIN read methods2.1–2.4 and experimental setup3.1–3.2; not all proofs.

Our inference from this source: a fixed intermediate contract lets us vary one
module at a time and reuse the rest, yielding more diagnostic terminal rewards
than blindly resampling an entire RLM. Conditional independence must actually
hold; replaying code with replacement helper outputs is not resampling an
adaptive parent's full continuation.

[λ-RLM, methods3 and appendixD](https://arxiv.org/html/2603.20105v1)
already chooses from task types and constructs typed, predetermined recursive
execution plans. Its partition result assumes a particular cost model; it is
not a universal optimal depth rule. The paper also identifies settings where
free-form control does better. We should compare a learned/adaptive choice
against a competent fixed compositional baseline, not against an intentionally
invalid chunking rule alone. MAIN read the combinator/task table, fixed-point
definition, planning algorithm and stated comparison limitations.

[HaReCAP, August17, methods3](https://arxiv.org/html/2608.16447v1)
compiles successful leaf-action grounding into reusable rules and executes a
rule only when it uniquely matches a current legal action. Otherwise it keeps
the original model path. Reported token savings on jointly successful tasks
are not all-task accuracy gains. This is related to our source-wording failures:
binding to an actually observed choice is different from inventing a plausible
string. MAIN read rules, triggering and evaluation-denominator distinctions.

## Smallest informative pilot

Use controlled customer/purchase tasks with known cross-partition dependencies,
plus at least one surface-template holdout. Keep CPU generation and grading
separate from model-visible inputs. Compare two useful contracts: return local
qualifying customers, or return per-customer purchase sets for exact merging.
First include a direct full-input baseline and an oracle-interface ceiling,
so failure is not automatically attributed to learning.

For a fixed decomposition, sample two independent implementations per leaf
on 16 small contexts. Evaluate their combinations on CPU under a fixed cap,
retaining invalid or incomplete outputs. Charge all model generation and CPU
verification; correlated combinations are not independent examples. Only if
alternative decompositions produce reproducibly different downstream rewards
should we train the planner. Keep the child model fixed for that first update.

Expected shape: one local4B model on the A100, approximately64–128 bounded
calls and5–15 minutes for the first small comparison, conditional on actual
throughput. Do not reserve a long run before confirming mixed outcomes.
Checkpoints: immutable generated-data seed/templates/split, both contracts,
all leaf alternatives, exact recombination map, verifier revision and costs.

Promote if a composable contract improves new cross-chunk cases and supplies
meaningful planner reward contrast. Revise if local extraction dominates.
Retire this formulation if a simple whole-input method solves everything at
lower cost or the interface leaks the answer. Do not reward agreement alone:
two wrong decompositions can agree. A later depth test must hold input length
and compute separately controlled from tree depth.

No repository has been cloned for this idea and no GPU work has been launched.
It is queued behind already-ready experiments, not a reason to interrupt them.
