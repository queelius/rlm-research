# Literature that changes the next experiment

September 9, 2026, 07:22 UTC. This is a targeted primary-source triage, not a claim
to have exhaustively reviewed these papers. GPU training continues independently.
Read depth and acquired-code limits are explicit below.

## Binding: the most immediate connection

Gur-Arieh, Geva and Geiger study how models recover entities associated with other
entities. Their experiments distinguish positional, lexical and reflexive retrieval
and find that these mechanisms mix; position becomes unreliable in longer lists.
This is mechanistic prior work, so our behavioral output-ID results must not be
presented as discovering a new attention mechanism. Read: abstract and main
binding/intervention sections, with parts of results; not every appendix.
[Mixing Mechanisms, v2, May 28, 2026](https://arxiv.org/html/2510.06182v2).

Our inference: the unexpectedly high source-numeral agreement in the ordinal arm
is a more specific lead than “numbering helps.” But our labels reuse only a few
semantic classes, unlike unique-entity retrieval; shared class labels can make
agreement look stronger. The already approved 384-call comparison removes numeric
overlap, swaps prefixes, retains exposed contexts and declares all alignment
diagnostics before new outcomes. If the effect disappears, interpret the earlier
counter as identifier interference, not a neutral position aid. If source-matched
tags remain useful with disjoint numbers, test another context group/model before
attempting activation interventions. These are our proposed experiments, not
results from the cited paper.

The [official code](https://github.com/yoavgur/mixing-mechs) is cached at commit
c53372c606e7cadf2494d2ac7b08e466042052df. Root license is MIT. It is source-only:
no dependencies installed or downloaded code executed. The requirements file has
unresolved conflict markers and a prompt helper slices rendered text blindly.
Do not run its launcher or treat it as a validated replacement for our runtime.
[Acquisition and checked files](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/repos/mixing-mechs-c53372c606e7cadf2494d2ac7b08e466042052df.PROVENANCE.json").

## Training through a changing harness

Harness-RL captures interface calls into per-session prefix trees and aligns
trainable tokens with outcomes. Its optimization separately handles action labels
and arguments using parameter partitions, and it studies central-only as well as
joint training. Read: abstract plus trajectory and optimization method sections;
not a reproduction or full benchmark audit.
[Harness-RL, August 30, 2026](https://arxiv.org/html/2608.29641v1).

Our inference: retain exact actual prompt/action tokens and root-versus-child
credit boundaries when adapting the helper interface. The current experiments
already provide the first tool-call prefix; they do not test learning a free
action decision. A future syntax-controlled comparison could remove that
constraint, but it should not displace the active broader-training or ready
identifier control. No new optimizer is justified by this abstract alone.

## Harness optimization is prior work, not our novelty claim

Recursive Harness Self-Improvement refines prompt-level agent-loop specifications
using pairwise feedback on revision history. It treats harnesses as both execution
scaffolds and producers of potential training traces. The abstract attributes
reported improvements largely to task-specific context management. Read depth:
abstract only; numerical claims and evaluation protocols not independently checked.
[Recursive Harness Self-Improvement, July 17, 2026](https://arxiv.org/abs/2607.15524v1).

Recursive Agent Harnesses makes the recursive unit a fuller agent environment
with tools, code execution and planning. It reports a fixed-backbone long-context
comparison. Read depth: abstract only; no claim that our current runtime reproduces
its implementation or results.
[Recursive Agent Harnesses, June 11, 2026](https://arxiv.org/abs/2606.13643v1).

Our inference: “co-evolve model and harness” and “recurse with a full tool-equipped
agent” are research directions with existing precedents. A tighter contribution
would measure when changes that improve a helper fail to help its coordinator,
then show a reproducible training/interface intervention that repairs that gap.
Receipt72 currently failed at interface uptake, before returned-answer validation.
The next sentinel therefore teaches the API and separates a restored procedure
paragraph from that teaching. Only observed uptake and a remaining decision-relevant
failure should promote helper-specific SFT or a new reward-training comparison.

## Queue consequences

1. Finish broad16 without changing its endpoint after interim outcomes.
2. Run the approved numeric-overlap/prefix control (384 native calls, one A100,
   approximately 20-25 minutes, 40-minute owned cap).
3. Run a bounded interface-uptake sentinel once its concrete design is accepted;
   use its call/consumption evidence to choose between prompt teaching and training.
4. Prepare tasks whose useful plan actually depends on the question; first check
   source-group headroom and fixed-plan baselines on CPU.
5. Activation work and open-ended harness search stay conditional. They must answer
   a surviving specific uncertainty, not merely consume the remaining allocation.

These rankings are adaptive. Negative controls revise explanations; they do not
retroactively change scores or turn exploratory contexts into held-out confirmation.
