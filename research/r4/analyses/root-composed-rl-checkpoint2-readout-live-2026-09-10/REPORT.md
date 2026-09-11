---
title: Fixed checkpoint-2 protected readout audit
date: 2026-09-10
status: complete
study: root-composed-rl-checkpoint2-readout-v1
science_attempt: outputs/attempt-003
method_sha256: a6213e97422888dc7ad7ca3a42b138e5fffdb4c2da5a4847743c9886e626d033
method_v5_amendment_sha256: b2f8545efac267345a5a1ad3fb595405e19b25d2e0ddb7541e08e77feda423d3
---

# Result

The second sparse-head RL update did not improve this exposed protected panel. Checkpoint 2 was
strictly correct on **47/72 planned endpoints** (five NULL; conservative bounds 47--52), versus
53/72 for checkpoint 1 (one NULL; bounds 53--54) and 55/72 for the unchanged start (one NULL;
bounds 55--56). On exact checkpoint-2 versus checkpoint-1 pairs, there were 3 wins, 5 losses,
58 ties and 6 unknown comparisons (known-pair net -2; possible net range -8 to +4).

The decline is concentrated in the 48 composed questions. Checkpoint 2 scored 28/48 (five NULL;
bounds 28--33), checkpoint 1 scored 35/48, and the start scored 36/48. Among 42 observed
checkpoint-2/checkpoint-1 composed pairs there were 2 wins, 5 losses and 35 ties; six were unknown
(net -3, possible range -9 to +3). The 24 primitive questions instead moved from 18 to 19 strict
answers, with all pairs observed. With only fixed optimizer ordinals 0/1/2 on one exposed panel,
these counts are not a smooth dose-response curve.

# What checkpoint 2 actually did

I read every available checkpoint-2 composed program and its actual tool observations; no sampled
program was re-executed. All **43/43 available composed endpoints acquired and retained a complete
16-record child-label map**. Only **32/43** then executed the requested operator, scope and threshold
faithfully. Of those, 27 were strict and grounded in the observed map; five faithfully computed the
wrong scalar implied by child-label errors. Thus the strict 28/43 includes one zero-answer success
from an unfaithful record-count-for-weight computation.

The eleven downstream failures were concrete rather than scalar-only disagreements:

- six stopped without a requested result after syntax/runtime errors or immediately after label
  acquisition;
- two counted totals across every category instead of the requested category;
- one assigned the global location sum to every user instead of making per-user totals;
- one counted records rather than weights; and
- one used a global location-existence test instead of the requested per-user conditional.

Nineteen observed-label oracles were zero; 13 of those endpoints were strict. Twelve of the 13
strict zeros followed the requested computation, while the record-count substitution above was a
coincidence. One otherwise faithful zero path also contained a dormant undefined-name bug that was
not evaluated because no predicted abbreviation records existed. These zero-support cases are not
evidence of robust nonzero composition.

By composed family (planned/available, strict, operator-faithful, faithful-and-strict):

| Family | Inventory | Strict | Operator-faithful | Faithful + strict |
|---|---:|---:|---:|---:|
| T1 | 8/6 | 2 | 3 | 2 |
| T2 | 8/8 | 5 | 4 | 4 |
| M1 | 8/8 | 5 | 7 | 5 |
| M2 | 8/5 | 4 | 4 | 4 |
| J1 | 8/8 | 5 | 6 | 5 |
| J2 | 8/8 | 7 | 8 | 7 |

# Native and cost audit

The source exporter independently authenticated all 72 attempt-003 episodes and their checkpoint-2
binding. The owner terminal is `098632e1...` (complete, released, no error; 756.4105 seconds), and
the exact parent EXIT is `d8fed507...` (exit 0, no timeout, empty GPU; 758.5939 seconds).

The raw union contains **446 physical requests and 446 responses**: 443 successful choice-bearing
responses and three error responses. Known usage totals are 1,107,375 input, 65,699 output and
1,048,992 cached tokens; each field is unknown for the same three error responses, not zero. By
returned model identity there were 366 checkpoint-2 root responses and 77 c32 child responses,
plus the three error responses without an authenticated model identity. This is local physical
usage, not provider billing.

Attempts 001 and 002 remain separate zero-request infrastructure failures and are not experimental
outcomes. Attempt 003 used the original qualified source namespace and phase name while binding the
root to exact Adam checkpoint 2; the phase string does not imply checkpoint 1.

# Interpretation and next comparison

Checkpoint 2 demonstrates continued acquisition competence but supplies no evidence that the
second terminal-reward update improved protected free behavior. The available traces instead show
that downstream operator/execution reliability remains a material bottleneck, while five otherwise
faithful paths are limited by child labels. Continuing windows 4--8 can still answer whether a
larger fixed dose changes behavior, but it should be judged on precommitted readouts with explicit
operator faithfulness and NULLs—not teacher loss or terminal scalar alone.

The panel, contexts, and seeds are research-exposed. Results support an exploratory within-panel
comparison only, not independent generalization or checkpoint selection.
