---
date: 2026-09-11
status: advisor-facing evidence brief
scope: child-interface adaptation, compositional transfer, and RL credit assignment
---

# What is publishable, and what is still missing?

## The strongest result today

The clearest result is that the interface used to supervise a recursive child model materially
changes what it can do at inference time. Starting from the same fixed 4B child, 24 updates using
only the compact A/B/other contract raised compact-interface accuracy from 590/768 to 680/768, but
reduced six-class accuracy from 725/768 to 707/768. Training only the six-class contract produced
the opposite specialization. A deterministic half-and-half curriculum avoided that trade-off: it
reached 734/768 on six classes and 665/768 on the compact contract, gains of 9 and 75 labels over
the common starting model. All 192 mixed-policy readouts and all reused controls were available and
native-decoded.

In plain language, the child had much of the underlying classification knowledge, but it did not
automatically express that knowledge through a new contract. Balanced exposure taught the new
contract while retaining the old one. The intervention is a bundle of prompt, output schema, and
target changes, so this is evidence for interface co-adaptation, not proof that target-token format
alone caused the effect.

The supplied-plan bridge gives a useful boundary on the claim. With the root plan held fixed, the
mixed child improved true six-class decisions by 19/1,280 and projected A/B/other decisions by
20/1,280. However, exact final counts improved by only one episode, from 0/8 to 1/8, and total
absolute error worsened from 117 to 130. Three of four context clusters improved, but one degraded
enough to dominate the total. The frozen promotion gate failed. Better local predictions therefore
transfer to the composed system, but not yet reliably enough to claim better end-to-end reasoning.

## What the reinforcement-learning evidence says

The present RL evidence is negative for this particular recipe, not for RL training of recursive
models in general. After the first terminal-reward update, the paired semantic audit found more
losses than wins: strict correctness had a known-pair net change of -2, faithful execution of the
requested operator/scope/threshold had net -3, and grounded faithful-and-strict execution had net
-5. At checkpoint 2, the root still acquired complete 16-record child maps on all 43 available
composed examples, but only 32 executed the requested operation faithfully. Six programs stopped
after errors, while others counted the wrong category, used a global rather than per-user test, or
counted records instead of weights. Five faithful programs nevertheless returned the wrong scalar
because child labels were wrong.

That pattern separates two bottlenecks. Child-interface training can improve the observations made
available to the root. Terminal-only RL must additionally teach the root to transform those
observations correctly. With groups of four, many training groups were homogeneous, so centered
terminal rewards supplied no gradient at all. The completed high-learning-rate continuation made
six genuine Adam updates, but its fixed readout fell from 55/72 at the unchanged start to 47/72;
paired missing-outcome bounds remain negative, from -9 to -5. Among 45 available composed cases,
42 acquired the child map, 32 performed the requested calculation, and 26 were both faithful and
correct; four exact zero answers were coincidences from wrong computations. The prepared 1e-5
ablation remains a fixed-dose diagnostic and should not appear as a performance conclusion until it
is sealed, run, and terminal-audited.

## Relation to prior work

[Recursive Language Models](https://arxiv.org/abs/2512.24601) establishes recursive inference over
long contexts, but does not establish our training-time interface-transfer result. Steno's 2026
[cost-aware RLM thesis](https://essay.utwente.nl/fileshare/file/110199/master-thesis.pdf) is the
closest training precedent: it applies group-relative RL to Qwen3-4B with rank-64 LoRA, LR 1e-5,
64 rollouts per step, shaped correctness/cost rewards, and up to 150 steps. Its reported 270-example
score rises from 27.0 to 37.6, but this is a single-seed, selected-checkpoint result under a much
larger and different recipe; we have not reproduced it. Its [official configuration](https://github.com/lsteno/prime_run/blob/2d57d15916f5fa0deed64c21d2e83f02a394afda/configs/rlm_rlvr/ablation_rank_lr/qwen3_4b_instruct_sanjaya_depth1_llmonly_r064_a128_lr1e-5_s150_8xa10080_bal35f40v1.toml)
makes the mismatch explicit.

[JSONSchemaBench](https://arxiv.org/abs/2501.10868) already studies structured-output compliance,
so “models benefit from structured output” is not a sufficient novelty claim. The plausible new
contribution is narrower: matched evidence that recursive child interfaces are learned behaviors,
that mixed-contract curricula mitigate specialization, and that local interface gains can fail to
compose monotonically into a root answer. Recent [SRLM work](https://arxiv.org/abs/2603.15653) also
argues that program selection matters, reinforcing the need to separate child quality from root
execution rather than attributing all gains to recursion itself.

## The smallest decisive missing comparison

The next decisive child experiment is a fresh paired end-to-end bridge, not another score on the
current research-exposed panel. Freeze new source groups that were absent from training and prior
analysis, then run the same supplied root plans with c32 and the mixed checkpoint using identical
requests, order, and stochastic seeds. Score true six-class labels, projected labels, exact final
answers, absolute error, availability, and physical cost separately. A practical minimum is eight
new context clusters with both context sizes and two paired seeds, about 320 child calls. It should
be feasible to prepare, run, and audit in one to two days on one A100. Promotion should require a
predeclared cluster-level improvement and no availability loss, not merely a gain in pooled labels.

For RL, the smallest mechanism test after the LR-only ablation is a matched credit comparison on
the same frozen windows: terminal correctness versus a prospectively defined execution-grounded
signal that distinguishes successful map acquisition, faithful operator execution, and final
correctness. Before spending GPU time, retained traces should demonstrate that the proposed signal
creates within-group variation where terminal rewards are homogeneous. This comparison needs fresh
readout endpoints and at least two seeds before supporting more than a mechanism claim.

## Publication path

The current evidence is suitable for an advisor discussion, workshop submission, or short empirical
paper framed around recursive interface co-adaptation and failure to compose. It is not yet a strong
generalization or RL-algorithm paper.

Within two to three days, the fresh paired bridge can decide whether the end-to-end transfer survives
new source groups. Within one to two weeks, three training seeds and a second child task or domain can
test whether the mixed-curriculum effect is stable and broader than this label system. A fuller
conference paper would likely require three to six weeks: fresh held-out contexts, matched exposure
and cost accounting, multiple seeds, at least one additional domain, and the terminal-versus-
execution-credit RL comparison.

The likely contribution type is an empirical methods and diagnostic paper: recursive systems must
co-adapt their internal communication contracts, and improvements at a component interface need
explicit compositional validation. A new RL algorithm claim would require substantially more
evidence than the current sparse-reward runs provide.

## Evidence ledger and caveats

The child panels and the eight supplied-plan episodes are research-exposed, not outcome-pristine.
The primary child panel is optimizer-disjoint, but it has been repeatedly analyzed. The supplied-plan
episodes are nested in four clusters, so eight endpoints are not eight independent contexts. Reused
c32 controls were not rerun, which preserves cost and exact historical receipts but does not estimate
new sampling variance. NULLs were kept unknown in the RL comparisons rather than scored as zero.

Audited source reports used here:

- Pure-interface child audit: SHA-256 `04a0a39698565e48d9d4dcc6c69958a745328d679f78d4f0e8c2bad200448a86`.
- Mixed-interface child audit: SHA-256 `c66201d836918caab6e726ef6976e08e59d5dce5e160bf3e95e0d7dfbe5eca6d`.
- Mixed-child supplied-plan audit: SHA-256 `fd757fb7f889cc20a4b8c5521cc91f02585c293cd7da7d477829983edd8662eb`.
- Checkpoint-2 semantic audit: SHA-256 `d6a990ba0ae6262269cfd7a9b1087b8be92b311b5e14521e8355830ba7157316`.
- Paired RL semantic counts: SHA-256 `bd9c8e3808f825714fbef0b48e48943d67f523b062bf30d728de3f58d97e1fe4`.
- Six-update continuation advisor takeaways: `analyses/root-composed-rl-continuation-live-2026-09-10/ADVISOR_TAKEAWAYS.md`.
- Steno primary-source question card: SHA-256 `a2007e36d1cc226be5bfb0c036791cc918b3efaadb32b717ab6763156cbb25f0`.
