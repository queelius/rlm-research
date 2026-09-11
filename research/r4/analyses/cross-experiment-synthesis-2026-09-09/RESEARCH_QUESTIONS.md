# Questions worth pursuing, and what would make them less interesting

The ranking favors comparisons that distinguish explanations. It is not a request to run all of them, and does not replace the live GPU queue. Read the newly completed controls before commissioning work they already answer. Each question connects to findings and a bounded design in [Next experiments](NEXT_EXPERIMENTS.md).

## 1. Can we preserve the link between each input and its answer?

**Q1 — Correspondence as a learned interface capability.** Related: F1, F3; candidate N1.

The old child classifies early items well, then produces valid but mostly repetitive labels. Mixed-size training changes lengths without fixing complete output. That creates a sharper question than “does batching work?”: does an explicit record identifier or repeated input anchor maintain correspondence, and can the model learn it without losing small-batch semantics?

The completed controls now favor the representation branch: indexed and echo outputs greatly improve aligned labels, and early-position strength persists under rotation. Test the indexed representation on fresh permutations and a new vocabulary before any training; do not repeat the old cells unchanged. The scope comparison adds a related distinction: shorter requested output with the whole input still visible does not help much, whereas local input does. Selection neglect remains an alternative to an attention-capacity explanation.

Potential contribution: a reproducible separation of syntax, cardinality, semantic decisions and record correspondence, followed by a mechanism-targeted intervention with an accuracy/cost frontier. Novelty is limited: batched inference and input/output indexing are established, and BatchPrompt already studies order variation. The contribution must be the controlled mechanism and its transfer, not “add IDs to prompts.”[^40][^41]

## 2. When the child improves, why does the root fail to use the gain?

**Q2 — Evidence consumption versus planning.** Related: F2, F7, F9; candidate N2.

The fixed classifier/aggregator exposes useful information that the free root often fails to convert into an answer. Observed errors include incomplete coverage, string/list confusion, malformed tool calls and incorrect final commitment. But nominally paired root trajectories diverged before the child changed, so their endpoint difference cannot isolate evidence consumption.

A common root prefix followed by controlled, separately identified child evidence can distinguish three possibilities: the child still supplies insufficient information; the root receives sufficient evidence but parses/uses it wrongly; or the root computes the correct result then fails to submit it. This is a diagnostic intervention, not an on-policy rollout and not a license to fabricate training log probabilities. The already running computed-commit MRCR comparison addresses one final-submission seam; do not duplicate it before reading its terminal result.

Potential contribution: a causal bottleneck map connecting component improvements to downstream gains. RLM work already trains roots and recognizes brittle final submission; this study would need a more exact intervention and measurement than that observation alone.[^39]

## 3. What exactly should a correct aggregate reward certify?

**Q3 — Reward definitions that expose cancellation and ignored evidence.** Related: F6–F8; candidate N3.

An exact count can be right with many wrong labels, and a root can return a correct answer while ignoring its reports. Before adding dense reward, ask whether a small set of counterfactual queries on the same latent labels distinguishes faithful solutions from accidental success. Examples are a count plus its complementary count, per-facet counts, or a report-implied answer alongside original truth. Some are redundant; the verifier must be chosen to detect an observed ambiguity, not merely add more numbers.

The smallest next test is an offline discriminating screen of frozen completed trajectories with authoritative local labels. Measure how often a proposed process criterion rejects genuinely useful plans or accepts cancellation. Only a criterion with useful selectivity should become a separate RL objective. Rewarding a mandatory recursion shape is specifically disfavored: prior shape filtering lost legitimate policy negatives, and some tasks do not need recursion.

Potential contribution: task-grounded reward identification and failure decomposition for programmatic agents. Process versus outcome supervision is established prior work; a new score is not novel just because it contains intermediate checks.[^44]

## 4. Is a root-only learning signal larger than unchanged-policy trajectory variation?

**Q4 — Reproducible learning with a fixed capable child.** Related: F5–F6; candidate N4.

The three-step campaign establishes fresh rollout capture, persistent Adam and root-only credit. It does not establish a learning curve, and the unchanged replay shows why an eight-trajectory before/after comparison is too weak. The next informative learning campaign needs a contemporaneous unchanged-policy reference, two independently initialized optimizer/rollout-seed runs, a validation rule fixed before scores, and new context compositions after selection.

The intended uncertainty is not whether an optimizer can execute or whether a larger model is stronger. It is whether training changes tool validity, coverage and evidence use enough to exceed baseline trajectory variation at a fixed budget. Final answer, conditional process metrics and cost tails must all be retained. A narrow admission amendment may avoid the known HTTP400 classification stop; it must not quietly convert policy-induced overlength into random infrastructure noise.

Potential contribution: a controlled role-specific training result with exact native action credit and a negative-control learning curve. Role-specialized adapters, root distillation and RLM RL training already exist; the claim must be stronger than implementation availability.[^39][^43]

## 5. Can input exploration lower cost without changing the semantic problem?

**Q5 — Scope reduction under a stable task contract.** Related: F4, F8; candidate N5.

Synthetic adaptive routing reduced input and performed well, whereas replacing the six-way mapping with target/other semantics was harmful. Test whether a root can identify relevant input on a previously unseen layout while preserving the child task, rather than assuming any shorter prompt is easier. Separate visible metadata from semantic content; do not reward the model for reading private labels or for an oracle's scope decisions.

Potential contribution: a matched distinction between information selection and task reframing, with an end-to-end cost/accuracy result across layouts. This could be valuable even if input filtering works and binary reframing consistently fails. It would not prove that the controller discovered a general algorithm when it was explicitly trained on the same routine.

## Secondary questions and lower-priority ideas

| Question | Why it remains useful | Current decision |
|---|---|---|
| Q6 — When should a root trust, verify or ignore a report? | Binding and selective verification have different error propagation; correct consensus can hide shared errors. | Calibrate natural error/repair headroom before another expensive revision loop. Reuse exact report-implication solvers. |
| Q7 — Can symbolic harness search and weight training help each other? | Current failures depend on concrete prompts, tool serialization, output contract and weights. | First qualify one representation/mechanism, then compare fixed-weight harness search, fixed-harness training and alternation at equal acquisition budgets. Do not start a general search framework now. |
| Q8 — Can exploration learn when not to recurse? | The 8B routine has no root reward variance; some tasks are directly visible. | Prefer a task mixture with measurable useful/needless-call tradeoffs over mandatory recursion rewards. |
| Q9 — Are corrections available before we build a selector? | SDB revision damaged correct reports and produced zero wrong→correct implied tuples. | Retire selector development on that exact candidate pool; screen a genuinely different repair operator first. |

GEPA provides existing primary evidence that reflective prompt search is a substantive competing method. It motivates a fixed-weight control for Q7, not a claim that any new harness search procedure will win or that GEPA's reported gains transfer to these tasks.[^45]

## Contributions that are plausible, but not yet established

1. **A measurement contribution:** an authenticated, reusable diagnostic suite showing where semantic accuracy fails to survive correspondence, aggregation or commitment. Requires a clear unit of analysis and cross-task replication, not just more traces.
2. **A mechanism contribution:** a matched intervention recovering late-batch correspondence without changing the task's answers, transferred to an untrained vocabulary and fresh grouped data.
3. **A learning contribution:** root-only training that improves faithful orchestration beyond unchanged replay noise with a fixed child, selected on validation and tested once on fresh contexts.
4. **A negative-result contribution:** evidence that standard format constraints, task simplification or report revision fail for a specific identifiable reason, supported by positive controls that demonstrate available headroom.

No novelty search can prove these ideas unpublished. The targeted primary literature rules out broad novelty claims already contradicted by known papers; it is not a systematic review of every related method. A paper-level claim would need a fresh targeted search at submission time.

[^39]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Recursive"
[^40]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Batch"
[^41]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [BatchPrompt](https://arxiv.org/abs/2309.00384)."
[^43]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [MapCoder-Lite](https://arxiv.org/abs/2509.17489)."
[^44]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Let's"
[^45]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [GEPA](https://arxiv.org/abs/2507.19457)."
