# Training complete routines and testing output correspondence

September9,2026,12:54UTC. Focused primary-source reading, not an exhaustive survey.
This note connects literature to ready experiments and possible follow-ups. It is
not evidence that any of our methods are novel or that a new experiment succeeded.

## The most useful training distinction

The original RLM paper trained its root model from filtered multi-turn teacher
trajectories, with each root turn paired with its preceding history. It removed
zero-scoring and single-turn trajectories, then applied context filtering and
template corrections. Nonzero benchmark scores do not necessarily mean every
retained answer was exactly correct. Our32 short interface demonstrations are
therefore not a close reproduction of that richer training recipe.
[Zhang, Kraska and Khattab, RLM v2, AppendixA](https://arxiv.org/html/2512.24601v2).

Our inference: before blaming the model size or terminal-reward objective, test
whether examples demonstrate a complete usable routine—inspect, choose relevant
records, ask helpers, combine evidence and submit the answer. Merely increasing
the weight of short terminal examples tests a different hypothesis. That control
is already accepted, so a future complete-trajectory study should remain separate.
Do not silently repair evaluation responses or pretend repaired teacher actions
were sampled from the policy being trained.

Algorithmically generated recursive supervision is another established option.
A separate recursion paper generated SAT-solving traces with DPLL, trained on
easy/medium problems and evaluated held-out difficulty levels. Its supervised
call/return traces support a narrow algorithmic task; they do not establish that
an arbitrary general-purpose decomposition policy will emerge.
[Yang, Srebro and Li, AppendixB](https://arxiv.org/html/2603.02112v1).

Our inference: if too few current successful rollouts have auditable reasoning,
a small set of executed, source-verified teacher programs is a legitimate SFT
starting point. The comparison must disclose the hand-written strategy family,
the task scope and which decisions remain learned. Such demonstrations are not
on-policy RL data and must not receive fabricated behavior likelihoods.

## The output-ID result needs narrow positioning

Output/input indexing in batched prompting predates this project. Batch Prompting
uses indices to connect multiple returned answers with their respective inputs.
We should not claim that returning IDs or batching classifications is new.
[Cheng etal., EMNLP Industry2023](https://aclanthology.org/2023.emnlp-industry.74/).

BatchPrompt studies batch size and position/order sensitivity, and uses permutation
ensembling plus an early-stopping procedure to trade calls/tokens against accuracy.
Generic position sensitivity and permutation-based recovery are therefore also
established research directions.
[Lin etal., BatchPrompt v3](https://arxiv.org/html/2309.00384v3).

Our narrower empirical question is whether specific source-matching cues improve
correspondence beyond structurally valid constant or disjoint ordinal outputs,
and how this changes across cue positions, density and models. The prospective
overlap control, third task, sparse-cue profile and accepted two-model/order tests
make that question more informative. They still do not identify an internal
attention mechanism, show a whole-RLM gain, or replace independent held-out data.

## Decisions linked to experiments

| Next question | Smallest informative comparison | Resource shape and decision |
|---|---|---|
| Did long code demonstrations dominate short final answers? | Same32rows/start/order/foursteps, equal-row versus original token-weighted loss;48 fresh paired readouts. | Already accepted; one A100,3330s outer cap. If syntax changes without correct counting, separate formatting from complete-task competence. |
| Does reward training improve the newly taught interface? | Active fixed-eight-update root-only run with paired baseline/final readouts and fixed child. | One A100 already working; checkpoint every update. Interpret strict answers, coverage and map-to-count failures separately; no checkpoint shopping. |
| Is there a good success-imitation dataset already available? | Fixed completed trainingrounds01–05; strict success plus native evidence, coverage and auditable reduction. | CPU-only feasibility, no evaluation candidates. Promote only if enough diverse complete trajectories exist; otherwise prepare executed teacher routines. |
| Does moving a sparse ID shift its local benefit? | Cadence4, matching/constant×ID-before/ID-after, identical order-pair prompts;96 fresh calls. | Already accepted; one A100,930s cap. Positive interaction tests a local behavioral prediction, not internal attention. |
| Does the identity effect extend to another released model? | Qwen3-4B versus Qwen3.5-4B, without research adapters;144 fixed calls. | Already accepted; one A100,2670s cap. Startup failures remain failures of this qualification, not model-quality scores. |

## Reading provenance and limits

Read on September9 using primary publisher/arXiv pages. Selected scope:
RLM v2 (January28,2026), framework and AppendixA/negative-results sections;
Recursive Models v1 (March2,2026), AppendixB data/training/implementation;
EMNLP2023 publisher page and relevant indexed-output PDF sections;
BatchPrompt v3 (July15,2024), abstract/introduction/position and ensembling sections.
No claim of full-paper replication, code execution, dataset acquisition or license
verification for reusable training assets. No downloads/installations displaced a
ready GPU job. These are literature notes; exact run inputs live in accepted
sidecar manifests. Other recent synthesis/structured-output papers screened earlier
are not promoted here without a concrete experiment they would change.
