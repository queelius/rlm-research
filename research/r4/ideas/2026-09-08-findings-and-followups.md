# Findings worth carrying forward

These notes separate useful observations from research claims. They are exploratory
and refer to the September 8 single-A100 allocation. Raw records, source hashes,
and analysis are in the named sidecars under this research store.

## Latest synthesis: local competence, coordination and useful batch size

Updated September9 at00:36 UTC. The earlier sections below retain the sequence of discoveries;
this section records the latest completed experiments, not a confirmatory claim.

Full supervised child training completed128 optimizer steps on5065 source-training
question groups. Validation selected the second epoch before the final test. On489
test groups, strict correctness rose355 to473; itemwise canonical correctness rose
374 to473. Thus formatting explains part, but not all, of the strict gain. This is
one4B model/one training seed on a public old classification dataset, with unknown
pretraining exposure. It establishes useful local competence, not general planning.

Two full mixed-size SFT followups are now complete: training sizes1/5/16/32 gives
477/489 small-batch test, and1/5/16/64 gives476/489. Both still return0/6 usable
64-item arrays. The latter does stop naturally rather than repeat to the cap,
but emits57–62 labels rather than64. This is a change in failure shape, not solved
large-batch correspondence. The additive [full report](../analyses/mixed-size-prefix-diagnostic/REPORT.md)
separates strict success from post-hoc partial-prefix diagnostics and explains the
remaining training/evaluation tool-key serialization difference. Schema, ID and
fresh exact-template controls test those mechanisms without replacing old scores.

That local gain is much clearer with a supplied aggregation routine than with the
free coordinating model. New composition tasks use six64-record contexts and two
count queries per context, repeated with two seeds. The full RLM gets4/24 correct
with the original child and6/24 with the trained child. Fixed five-item batching
and Python aggregation gets1/24 and15/24. A root failure can erase good child work:
in one case the child correctly identifies all14 target records, but the root adds
the answer string character-by-character and returns0. Conversely, a correct count
can hide a false-positive/false-negative cancellation and incomplete coverage.

Crucial causal limitation: identical forwarded first-root requests/seeds did not
guarantee identical first-root actions. They differed before any child response in
3/6 development pairs and15/24 composition pairs. Those differences are not caused
by child answers. The unchanged-weight native validation replay finished4/8 versus
the initial2/8. After one root-only update the same eight coordinates gave2/8.
This tiny three-way pilot supplies no validation evidence of improvement.

Batch size is already a useful scaffold parameter. Here are the completed fixed
operator outcomes with the trained child; each row reuses the same384 source
questions in24 coordinates (1536 repeated assignments):

| Questions per child call | Strict counts correct | Complete valid aggregates | Canonical aligned assignments correct | Calls per coordinate |
| --- | ---: | ---: | ---: | ---: |
| 1 | 5/24 | 5/24 | 1460/1536 | 64 |
| 5 | 15/24 | 24/24 | 1485/1536 | 13 |
| 16 | 15/24 | 23/24 | 1466/1536 | 4 |
| 64 | 0/24 | 0/24 | 0/1536 under strict alignment | 1 |

Five/sixteen use256 output tokens; singleton/64 use1024. Therefore comparisons
are operational strategies, not identical-budget interventions. The64 row's zero
aligned score does not mean every generated label was semantically wrong: arrays
were malformed or had wrong cardinality, and44/48 calls across both weights reached
the output cap. Representative outputs repeat a label far past the required length.
Singleton calls compound occasional contract failures across64 responses. Sixteen
cuts logical input248804 to86372 per arm versus five, with a small semantic/contract
trade-off. Actual cache, output and wall costs remain in every attempt artifact.

The exact-cardinality schema control is now complete and separates two failures.
For the trained singleton model it changes strict counts from5/24 to16/24, while
all1536 first labels are identical to the unconstrained condition. It admits28
correct predictions previously masked by29 extra-answer arrays. This is unusually
clear contract repair, not evidence that the first-label semantics improved.

At64 items, grammar makes every array valid but both models still score0/24 counts.
The trained model gets698/1536 labels right; accuracy falls from374/384 in positions
1–16 to81/384 in positions49–64. It predicts entity366 times in those final384
slots, despite only80 being gold entity. All96 original/trained free/schema inputs
contain the full64 questions in order, at only1321–1361 prompt tokens. The weakness
is not input truncation. Original weights also collapse, so narrow SFT did not
demonstrably cause it. This completed-only audit is sealed separately at
analyses/leaf-batch-shape-2026-09-08/REPORT.md.

Immediate falsifiable followups, already running/preparing:

- Full mixed-size SFT A and B are complete. Both
  start from the original adapter and see the same5065 groups twice. A practices
  sizes1/5/16/32; B practices1/5/16/64. The fixed final second epoch tests whether
  training repairs correspondence and whether A extrapolates to64. These are
  record-exposure-matched but not optimizer/compute-matched to original all5 SFT.
  Greedy HF/vLLM probes bothgave0/6 valid64-arrays with the old selected adapter;
  their semantic messages match but tool-key serialization changes actual IDs.
  Final A/B64 evaluation matches the HF probe's exact physical prompts, not a
  claimed backend-only control. Small fixed5 competence is measured alongside it.
- Hold the improved child fixed and train only the coordinator's own native actions
  from fresh mixed-reward groups. The first actual step is complete:16 episodes,
 30 root turns,10500 credited tokens,23.866seconds optimization, nonzero gradient
  and adapter change. An8-round fresh-rollout campaign with persistent Adam started
  automatically00:25:36 for a longer learning curve. Its initial validation is2/8;
  first fresh training32 gives12strict successes,0null,7mixed groups before update.
  Child observations never receive root
  loss; the pilot's unchanged validation result is not a reason to fabricate a win.
- If moderate batches remain best, test an explicit batch-selection/split operator
  on fresh task families and document sizes. Compare fixed versus adaptive choices
  with all attempts charged. Do not call generic model/scaffold co-adaptation novel;
  the interesting question is whether matching the scaffold to a learned component's
  reliable operating range transfers across problems.

Evidence: trec-leaf-sft-v1/analyses/attempt-001; analyses/leaf-role-composition-fixed-
2026-09-08; fixed-leaf-composition-v1; fixed-leaf-batch16-v1;
fixed-leaf-batch-extremes-v1; fixed-leaf-batch-schema-v1; root-only-credit-v1.
Joint trace and batch audits are sealed; no test-driven
relabeling or original-artifact overwrites are authorized by this synthesis.

The native-versus-Chat direct MRCR control now independently verifies identical
output bytes for all six examples:2/6 exact, mean.3522015294, input36063/output1904,
raw cached input80. This resolves that narrow client concern, not the separate
RLM/direct whole-system comparison or long-context scaling. See the sealed report
under mrcr-native-direct-six-v1/analyses/converted-typed-models-attempt-001-vs-chat6.

## Interface behavior can look like a lack of reasoning ability

On matched tasks and the same frozen Qwen3-4B model, the old training client
executed Python in 0/24 episodes. Using the actual nonthinking model's prompt
format raised this to 16/24. No weights changed. Evaluation-client totals stayed
18/24 across the two runs. This is a concrete confound in interpreting an apparent
training-temperature or planning failure, not a novel learning algorithm.

Evidence: strict-rlm-client-qualification-v2/analyses/baseline-native-2026-09-08.

## A written procedure is not the same as usable decomposition skill

In one development context, minimal task instructions gave 6/14 correct answers
and an added procedure gave 1/14. The procedure used 4.61 times as many output
tokens. Neither condition produced actual recursive calls. The two repetitions
and seven questions are not fourteen independent documents. The source-heldout
context is reported separately and does not guide intervention design.

The completed twelve-episode comparison answers the first mechanism question:
the original zero-update weights make recursive calls in5/6 executable-example
episodes and0/6 abstract-procedure episodes. The SFT and RLVR checkpoints make
recursive calls in3/6 and5/6 example episodes, respectively. Thus the example
activates behavior already available to the base model; these weight updates did
not create the demonstrated recursion. This is one development context, not a
transfer or independent-task significance claim. One original abstract episode
has a null provider error (8193 prompt tokens versus8192 capacity), not reward zero.

Evidence: plan-hint-crossover-v1/analysis/PRE_UPDATE_RESULT_SEAL.json.

## Final-answer rewards can reinforce the wrong intermediate method

The fresh training collection has 6 strict successes among 40 attempts. All six
read the full context, but their category assignments use crude keyword/default
rules. Two successful comparisons count literal label words in headers rather
than correctly classify the questions. They have correct terminal outcomes, not
verified intermediate reasoning. Keep their predeclared training admission intact
and test the consequences instead of quietly cleaning the data after inspection.

Questions this enables:

- Does positive-only self-SFT improve terminal accuracy while preserving or
  amplifying these shortcuts?
- Can counterfactual documents preserve the task structure while reversing the
  answer that the shortcut predicts?
- Does exposing a small record-level verification tool help more than a longer
  instruction? Compare its cost with ordinary recursive classification.
- Where is the error: interpreting a record, combining correct subanswers, or
  deciding which evidence to collect?

Evidence: strict-rlm-client-qualification-v2/analyses/fresh-positive-evidence-2026-09-08.

The later authoritative-label audit makes this concrete. All89 training-context
questions uniquely match two primary source files with agreeing labels; all16
training aggregate answers recompute correctly. In a successful abbreviation count,
the recursive program includes record29 incorrectly and omits record75 incorrectly.
It still returns the gold count4. Its false positive and false negative cancel.
Canonical record-label accuracy is32/89 after self-SFT and34/89 after the RLVR pilot
for that paired example; both produce36 labels outside the requested six-label set.
An explicitly separate alias-collapsed sensitivity analysis does better, but does
not repair the exact-contract failure or establish correct aggregation evidence.

The executable-example probe now has complete three-weight comparisons. Completed
SFT results are abstract4/6 correct with0/6 actual recursion versus example5/6 with
3/6 recursion. Completed RLVR results are abstract3/6 with0/6 recursion versus
example3/6 with5/6 recursion. In the RLVR example arm there are77 committed child
calls and77 returns. More recursive work is clearly not by itself a success metric.
Some programs adapt batch sizes after failures; another counts85 returned labels
for89 questions without checking coverage. The original example arm is5/6 strict
correct with5/6 recursive episodes and82 committed calls+returns; its abstract
arm is3/5 observable correct plus one null error. All three weights reproduce
the same abbreviation false-positive/false-negative cancellation. Original-weight
canonical accuracy in that episode is32/89, the same as the SFT example.

Evidence: trec-train-process-audit-v1/CHILD_PROCESS_AUDIT.json and
recursive-call-example-v1/analysis/THREE_WEIGHT_REPORT.md.

A separate fresh native training-client capture now proves trainable recursive
actions, with12 complete episodes,159 sampled turns and12423 action tokens. The
only mixed-reward group's positive is especially informative: Python computes
the least-common label as human being, but the final model answers abbreviation,
matching gold. The positive's33/89 canonical child-label accuracy is not better
than the negative trajectories'35/89,36/89 and32/89. Leave declared rewards and
exports intact; do not call another all-action outcome update process supervision.
Evidence: recursive-train-capture-v1/analyses/attempt-002/REPORT.md.

Next probes: a train-only leaf contract factorial (clear label definitions and
enforced JSON labels varied separately), plus a queued counterfactual comparison
removing the identified false positive or false negative from the document. These
test specific failure mechanisms, not a generic claim that recursion is ineffective.

Prospective predictions before leaf72 runs: schema should mainly repair output
vocabulary/cardinality, while definitions may improve class interpretation. A gain
in canonical accuracy from replacing a DESC synonym is a useful interface repair
but not necessarily a gain in underlying semantics; report both canonical and
explicitly separate alias sensitivity. If neither arm helps meaningfully, do not
build a generic constrained-child feature just because it is technically possible.

Conditional next direction: train only a child classifier on trustworthy source
labels, freeze the root, then evaluate fresh multi-record aggregation documents.
This distinguishes worker competence from planning competence. It requires question-
level split audits: raw official TREC train/test share11 normalized question groups,
and OOLONG's loader does not establish disjointness from its split argument. Do not
call an old public dataset uncontaminated with respect to base-model pretraining.
Grammar-constrained leaf outputs are not eligible for our current full-softmax
RLVR estimator without separately capturing/handling their changed sampling support.

## Neighboring projects suggest useful controls, not requirements to inherit

rlm-bootstrap motivates the clean positive-only self-training control: use the
same model and fixed harness, with loss only on its actions. It does not establish
that outcome-filtered trajectories contain a good method.

The structured-decomposition benchmark separates whether an answer uses an
intermediate report from whether that report is true. Its small development
experiments also show that a learned decision to revise is unhelpful if the
available revision procedure cannot repair errors. For RLM work, first test whether
the proposed tool or decomposition action can improve an answer at all.

evolved-integrators offers a useful design pattern: search over restricted,
inspectable components and count every proposal/evaluation cost. For harness search,
compare fixed and adaptive choices, train-only feedback, and total calls including
candidate generation. Generic model/harness co-adaptation is already studied;
novelty would require a specific intervention and a convincing transfer comparison.

## Current claim boundary

Prior SFT evidence supports learning synthetic routines, including lower recursive
input cost. It does not establish open-ended planning. Prior direct RLVR completed
four updates without improved strict heldout accuracy. The first current RLM RLVR
attempt stopped before its optimizer step on serving/training numerical mismatch.
The separately declared token-TIS retry completed one real update with finite
gradient, changed weights, exact starting tensor audit, and checkpointed optimizer/RNG.
Self-SFT completed six updates on six verified terminal successes. The predeclared
primary heldout result is2/14 for the starting weights and both trained checkpoints,
with every paired outcome unchanged. These are tiny pilots, not evidence that
longer training cannot work; they establish an operational learning path but no
primary heldout improvement. Do not inflate secondary changes on the known
answer-revealing question.
