# RLM capability-boundary factorial

Status: design checkpoint; no outcomes observed under this design and no GPU launch yet.

## Why this study exists

The first action-masked RLVR calibration used four simple 64-record tasks with six broad semantic
labels. It produced 66 valid trajectories and all 66 were correct. The next sealed curriculum made
the easiest rung 96 records with eight finer labels. Its first rung produced 0 valid trajectories in
24 attempts under the same four-turn, one-subcall budget. Most attempts did not submit a final answer;
some tried to make a second subcall.

That is a real capability cliff, but the comparison changes three things together:

1. context length (64 versus 96 records),
2. ontology size and semantic granularity (six broad labels versus eight finer distinctions), and
3. distance from the controller's SFT distribution.

The next screen should identify which change causes the cliff and whether a modest execution-budget
increase exposes valid but mixed-success trajectories suitable for RLVR.

## Questions and hypotheses

Primary question: which controlled task and execution setting gives the current SFT controller a
high valid-completion rate but only 20--80% strict exact success?

- **Length hypothesis:** increasing records alone exhausts the four-turn routine.
- **Semantic-granularity hypothesis:** splitting familiar broad categories into finer distinctions
  breaks the learned classification/decomposition strategy even at the familiar context length.
- **Execution-budget hypothesis:** six turns and two subcalls rescue completion, but may reveal mixed
  correctness rather than simply moving directly from zero to perfect performance.

The screen must measure validity and correctness separately. Invalid executions are never converted
into reward-zero training examples.

## Frozen factors for the screen

Use a simple facet-conditioned single-label count query throughout. Cross:

- ontology: the SFT-matched six broad categories versus an eight-category fine-grained ontology;
- records: 64, 80, and 96;
- execution budget: four turns/one subcall versus six turns/two subcalls.

This gives 12 cells. Use two independently generated prompt groups and three paired rollout seeds per
cell (72 total exploratory episodes). Run the two budget arms on separate A100s when possible. Keep
model weights, adapter, temperature, sampler, verifier, output schema, server build, and task seeds
fixed across cells. Balance semantic classes mechanically before sampling surface forms, and seal all
tasks and seeds before the first rollout.

The initial screen is for promotion, not for a learning claim. Promote cells with enough valid
executions to plausibly reach the confirmatory gate and at least one correct and one incorrect strict
answer. If no cell is mixed, use the observed factorial pattern to add one interpolating record count
or execution budget; do not manufacture variance from invalid traces.

## Confirmation and one-update gate

For at most two promoted cells, generate four new calibration prompts and six rollout seeds per prompt.
A cell is eligible for one action-masked LoRA update only if all of the following hold:

- all 24 planned episodes are terminal;
- at least 20 are valid;
- strict success among valid episodes is 20--80%;
- at least two prompt groups each contain four or more valid trajectories and both reward values;
- raw action token IDs align exactly with selected-token log-probability IDs.

Select the first eligible cell under a predeclared order. Train only on valid controller-action tokens,
using the already-tested one-step update. Leaf output, prompts, observations, and environment output
remain masked. Evaluate 24 paired, disjoint held-out trajectories before and after the update. For the
primary held-out endpoint, invalid counts as terminal failure; also report jointly valid accuracy and
validity separately.

## Required artifacts and analysis

Record exact repository commits, model/base/adapter hashes, task-generator and task hashes, Python and
`uv` lock provenance, CUDA/vLLM versions, GPU UUIDs, ports, process groups, sampler parameters, and all
phase timestamps. Store one immutable episode record per trajectory plus append-only phase markers.

For every cell report:

- valid completion rate and strict exact success both overall and conditional on validity;
- failure reasons, especially no-final-answer, subcall exhaustion, turn exhaustion, malformed output,
  timeout, and action/log-probability misalignment;
- turns, leaf calls, generated tokens, wall time, and task-group variation;
- paired differences between the two execution budgets using identical task and sample seeds.

The factorial interaction is itself a research result. In particular, a fine-ontology penalty at 64
records supports a compositional-semantic generalization failure, while a length penalty under the
matched ontology supports a context-management bottleneck. Rescue by extra turns/subcalls distinguishes
an execution-budget bottleneck from an inability to form the correct local decisions.

## Stop and pivot rules

- If all 12 cells are at ceiling, increase semantic novelty or query composition while retaining the
  factorial controls.
- If all 12 cells are mostly invalid, test an intermediate five-turn/two-subcall budget before changing
  task semantics.
- If valid trajectories exist but remain all correct or all wrong, interpolate only along the factor
  implicated by the observed main effect.
- If no stable mixed coordinate emerges after one interpolation, pause weight updates and study the
  invocation/termination behavior directly; the immediate training bottleneck is then strategy control,
  not reward optimization.

