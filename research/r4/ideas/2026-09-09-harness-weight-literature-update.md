# What recent harness–weight research changes for our experiments

Reviewed on 2026-09-09. This is an additive literature and decision note, not a
revision of the [dossier's fixed evidence cutoff](../analyses/cross-experiment-synthesis-2026-09-09/README.md).
The comparisons below are proposals, not launched jobs or measured effects.

## Main decision

We should not present “improve the model and its harness together” as our novel
contribution. Recent work already does this explicitly. Our more specific question
is whether the interface preserves the connection between each piece of evidence
and its source, and whether training teaches a reusable skill or only a familiar
interface. The current anchor comparison and indexed-output training are small
steps toward answering that question, not demonstrations of general decomposition.

## Four relevant primary sources

### Alternating model training and harness search is established prior work

[WHALE, version 1](https://arxiv.org/html/2609.00196v1), submitted August 31, 2026,
alternates supervised updates on verifier-accepted model trajectories with search
over executable harness code. Each phase fixes the other component. Its search,
mathematics and chess experiments use small Qwen3.5 models. It studies fixed and
adaptive switching schedules. Its headline comparison reports best test mean@8;
that is a different reporting protocol from a fixed-final or validation-selected
checkpoint. This distinction is not an allegation about training-data leakage.

**Our inference:** a useful next comparison crosses both weights with both
interfaces. Merely comparing an old model/old harness against a new model/new
harness cannot identify which change helped or whether they depend on each other.

### Training on changing interfaces can target brittle memorization

[Harness-Aware Training, version 3](https://arxiv.org/html/2608.15763v3), dated
August 26, 2026, trains a live-commerce agent across variations in skills, tool
definitions, prompts and execution hooks. Its pipeline includes augmented
demonstrations, general-domain distillation and reinforcement learning in a
simulated environment. The authors motivate this as learning to use the currently
provided interface rather than memorizing one configuration. Its application and
change envelope differ from our recursive classification experiments.

**Our inference:** if indexed-output training works, test unfamiliar ID names and
orders before claiming general correspondence. Training with varied IDs is a
separate intervention. Our queued run resets sequential IDs within each batch;
it does not already test arbitrary identifier generalization.

### Batched reward training is related, but its task and reward differ

[Batched Contextual Reinforcement, version 1](https://arxiv.org/html/2604.02322v1)
trains mathematical problem groups under a shared output budget with GRPO. Its
reward combines mean per-problem correctness with a format component; it is not
simply a terminal all-or-nothing batch reward. It uses no explicit length penalty.
The reported evidence concerns 1.5B and 4B mathematical reasoning models, not
classification correspondence or recursive evidence consumption. The arXiv
submission date is April 2, 2026; the rendered title page gives August 24, so this
note pins the version rather than inferring a revision history.

**Our inference:** per-record correctness is worth comparing with an exact final
count, which can conceal cancelling errors. First establish that a faithful label
map is observable. Our current one-full-batch TIS update is not a GRPO replication.

### A harness improvement may not transfer to another model

[HarnessDev, version 1](https://arxiv.org/abs/2609.01437v1), submitted September 1,
2026, evaluates building and evolving executable harnesses. Its abstract reports
unstable evolutionary gains and limited transfer to held-out tasks and different
runtime models. This note reviewed the abstract, not the complete implementation
or benchmark protocol, and makes no stronger claim about its results.

**Our inference:** retain cross-interface and cross-weight readouts. A local gain
may be useful even if it is specific, but its specificity must be measured rather
than described as broad compositional generalization.

## Small experiments these sources motivate

These estimates assume the existing 4B model on one A100. They are not measured
runtime guarantees. Every promoted comparison needs frozen inputs, source-group
splits, seeds, caps, checkpoint policy and an artifact directory.

| Question | Smallest useful comparison | Compute and decision |
|---|---|---|
| Is the gain in the interface, weights, or their interaction? | Cross old/new weights with anonymous/indexed outputs on identical tasks and physical prompts within each interface. | The queued SFT readout already crosses three weights and two formats, without constrained decoding. Its 90-minute overall cap includes training and readouts. If only one matched pair works, report interface-specific adaptation. |
| Does correspondence survive new identifier conventions? | Freeze old and indexed-trained weights; compare familiar IDs, hash-like IDs and reordered IDs on the same 12 source contexts. | At most 288 leaf calls, one loaded base, 30-minute collection cap, immutable per-call records. Promote varied-ID training only if an interpretable robustness gap remains; do not tune on this readout. |
| Can a reward distinguish correct totals from correct evidence? | First audit frozen traces with pass/fail/unobservable coverage and cancellation diagnostics. Only then compare terminal-count versus per-record reward in fresh training. | CPU screen first. If evidence is observable, provisionally two four-update root runs, at most three GPU-hours total, checkpoint each update. Retire or redesign if the proposed score mostly measures serialization or rewards a preferred decomposition. |
| Does an evolved harness travel with its model? | Freeze two candidate harnesses and cross them with original and trained weights on development-selected, subsequently fixed tasks. | At most 96 bounded root continuations, 60-minute cap; same environment and verifier. Promote a broader co-adaptation study only if the interaction survives a separately frozen readout. |

The identifier test is deliberately different from the queued transfer study:
the queued study changes question arrangements and task vocabulary while retaining
one identifier convention. These proposals must not silently modify a frozen run.

## Official implementation acquired, not executed

The [official WHALE repository](https://github.com/krafton-ai/WHALE/tree/fbe125eb7abea7f760c99ab9acc1a6261e708fc6)
is stored outside Git-managed research source at:

`/project/alex_phd/research-cache/repos/WHALE-fbe125eb7abea7f760c99ab9acc1a6261e708fc6`

Its README, data/reproduction notes, NOTICE and shared alternation script were
inspected. The Apache-2.0 repository vendors separate training-framework copies
for the three domains. The reproduction notes say the released launchers were
checked with stubs but not run end-to-end on GPUs; the paper used their predecessor
scheduler scripts on eight H200s. We therefore should not assume a drop-in,
one-A100 reproduction. No dependency installation, model execution, paid proposer
request or dataset acquisition from this repository was performed.

[Acquisition metadata](../../../ARTIFACTS.md#unpublished-files "Not published: 2026-09-09-WHALE-acquisition.json") records its exact commit,
tree identity, inspected-file hashes, licensing boundary and retrieval date. The
data notes describe separate roles for weight training, harness search and test;
actual split membership has not been regenerated or independently audited here.
The clone's displayed disk use was 18 MiB. No existing environment was modified.
