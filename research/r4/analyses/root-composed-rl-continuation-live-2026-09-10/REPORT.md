---
title: Sparse terminal-reward continuation and fixed checkpoint-6 readout
date: 2026-09-10
status: complete
study: root-composed-rl-sparse-continuation-v1
training_attempt: outputs/attempt-002
readout_attempt: outputs/readout-attempt-002
method_sha256: 3007f2102b6f53832aa9124e6636cc8608399e86a7d41f498354eb27570bf4c3
---

# Result

Four more high-learning-rate terminal-reward updates did **not** recover the original policy's
behavior on the fixed, research-exposed 72-question panel. Checkpoint 6 was correct on **47/72**
planned endpoints (69 available; bounds 47--50), compared with **55/72** for the unchanged start
(71 available; bounds 55--56), **53/72** at checkpoint 1, and **47/72** at checkpoint 2.

The exact checkpoint-6 versus start comparison has 3 wins, 9 losses, 56 ties, and 4 pairs with at
least one NULL. Its conservative net range is **-9 to -5**, so missing endpoints cannot reverse the
observed decline. On the 48 composed questions it is 30/48 versus 36/48 at start (net range -7 to
-3); on the 24 primitive questions it is 17/24 versus 19/24 (net -2). Relative to checkpoint 2,
checkpoint 6 is not distinguishable on this panel: the overall paired range is -5 to +3.

# What the final policy actually did

I read every available checkpoint-6 composed program and its actual child/tool observations; no
sampled program was executed. Of 45 available composed endpoints:

- **42 acquired a complete 16-record child-label result**;
- **32/45 actually performed the requested operator, scope, and threshold**;
- **26/45 were both faithful and strict-correct**;
- six faithful computations were wrong because of child-label errors or, in one case, malformed
  final formatting; and
- thirteen had an operator or execution failure. Four of those thirteen nevertheless received a
  strict-correct zero answer by coincidence.

The failures are concrete: three endpoints never obtained a complete child result; five acquired
labels but ended in repeated execution/file errors or no final; two replaced a per-user conditional
or maximum with a different aggregation; two used the wrong key/category arithmetic; and one
formed an invalid qualifying-user set. Thus **30 strict composed answers are not 30 demonstrations
of the desired mechanism**: only 26 were grounded faithful successes.

| Family | Planned / available | Strict | Operator-faithful | Faithful + strict |
|---|---:|---:|---:|---:|
| T1 | 8 / 8 | 4 | 6 | 4 |
| T2 | 8 / 8 | 5 | 6 | 5 |
| M1 | 8 / 7 | 3 | 4 | 3 |
| M2 | 8 / 8 | 6 | 6 | 5 |
| J1 | 8 / 7 | 6 | 5 | 5 |
| J2 | 8 / 7 | 6 | 5 | 4 |

# Execution and cost

The continuation resumed the exact Adam-2 checkpoint and committed four genuine updates, ending at
checkpoint 6. All five remaining windows and 120 planned training episodes were independently
replayed; checkpoint ancestry, optimizer state, RNG state, and the 504 Adam tensors were checked.
The four new optimization passes took 127.40 seconds; the full continuation owner took 1,780.42
seconds (parent 1,785.29 seconds). Training produced 607 physical request/response pairs, 603
choice-bearing responses and four errors: 1,188,260 known input tokens, 84,703 output tokens and
1,115,408 cached tokens.

The fixed checkpoint-6 readout completed and released cleanly: owner SHA `d0c53e1b...`, parent EXIT
SHA `57cde698...`, exit 0, 728.36 seconds, empty GPU. Its physical union contains 408 requests and
responses, 405 choice-bearing responses and three errors: 1,040,949 known input tokens, 62,466
output tokens and 974,592 cached tokens. The same three error calls have unknown usage, not zero.

# Advisor-facing interpretation

The clean statement is: **the sparse training machinery worked, but this extra terminal-reward dose
did not improve—and on the fixed panel worsened—the behavior we care about.** The model often still
obtains the child labels; its weak point is reliably turning those labels into the requested scoped
calculation and stopping with a valid answer. End-answer reward does not distinguish the observed
wrong zero computations from genuine successes; whether that caused the decline is untested. Lower
training loss or a successful optimizer step is therefore not evidence of better RLM behavior.

This does not show that RL is generally ineffective. It tests one model, one high learning rate, one
terminal-only reward, one fixed curriculum, and an exposed eight-context panel. It does show that
repeating this exact recipe or selecting a later checkpoint by training progress is not supported.
The decision-relevant next comparison is a genuinely different training corpus or interface with a
precommitted held-out readout and the same semantic-path audit—not more steps on these same windows.
