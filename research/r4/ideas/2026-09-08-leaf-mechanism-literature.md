# Leaf semantics, role-specific training, and misleading outcome rewards

Snapshot: 2026-09-08 UTC. Bounded primary-source check prompted by the
[three-weight recursive-call comparison](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/recursive-call-example-v1/analysis/THREE_WEIGHT_REPORT.md"),
not a general novelty survey. Existing queue and September 8 literature memo were read first.
No GPU/model call, installation, dataset acquisition, shared-source change, or admission-rule change
was made. Source versions, official-code revisions, licenses and SHA-256 hashes are in the
[acquisition manifest](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/2026-09-08-literature/leaf-mechanism-literature.j9hVwD/PROVENANCE.json").

## Decision

Keep the already-frozen [schema72 probe](../sidecars/trec-leaf-contract-probe-v1/README.md) first.
Then, if semantic errors remain, test a small leaf-SFT adapter with the **root held fixed**.
Training on leaf outputs and deploying the resulting adapter at every node is not the same
intervention as changing only leaf weights. Record the adapter identity at each semantic node.

Our narrow opportunity is attribution: distinguish delegation activation, output-shape compliance,
record-level semantics, and aggregation reliability under controlled root/leaf identities. Role
specialization, structured decoding and process supervision are already established directions.
This search did not verify an existing study combining our exact recursive TREC-label audit and
role-isolated weight comparison; that is not a claim of exhaustive novelty.

## Five sources and the smallest useful comparison

### 1. Recursive Language Models — test its explicit root-bottleneck hypothesis

[Zhang, Kraska and Khattab, arXiv:2512.24601v3](https://arxiv.org/html/2512.24601v3#A1),
revised May 11, 2026. Appendix A constructs SFT samples from **root turns**, hypothesizing that
root REPL/delegation competence is the main hurdle while leaf requests resemble ordinary LM tasks.
This is an empirical training choice and hypothesis, not proof that leaf competence is sufficient
on every dataset. Native RLM SFT and MRCRv2 RLVR already exist in this paper.

The [official release](https://github.com/alexzhang13/rlm/tree/854e688fbba9d8f8989e3da9989812e4b6dfe270/training)
provides a depth-one training harness; its README routes subcalls to the trainer inference server
and executes Python on the host. It does not establish a tested leaf-only training ablation.

**Our addition:** freeze root weights, prompt and budgets; compare base versus supervised leaf
weights on three development aggregate tasks × two fresh seeds: 12 episodes. Measure committed
recursion, aligned label accuracy, cardinality, exact aggregate answers and cost. This tests a
local leaf bottleneck; it would not refute the paper's broader long-context results.

### 2. MapCoder-Lite — role-wise adapters and component ablations are prior work

[Lee, Cho and Choi, arXiv:2509.17489v2](https://arxiv.org/html/2509.17489v2#S5.SS3),
revised February 4, 2026, is titled *Distilling Multi-Agent Coding into a Single Small LLM*
(the older title says *Squeezing*). Four role-specific rank-32 adapters share a frozen 7B backbone.
Its component ablation improves xCodeEval from 13.21% to 18.87% by tuning retrieval alone;
further roles change format failures, initial solutions and debugging success. Thus neither
role-specific LoRA nor selective-component tuning is an original claim for us.

[Official code](https://github.com/aiha-lab/MapCoder-Lite/tree/b5ed53cdfe8607529036420abf1d46fcf67e3f41)
contains separate trainers and adapter-aware serving. It is not plug-and-play: read-only AST
validation finds a syntax error in `train/retrieval/train_sft_lora.py:65`; data extraction is marked
TBD and serving paths are machine-specific. The paper used an A100 80GB, not our 40GB card.

**Our addition:** reuse the *same* leaf-SFT adapter in leaf-only versus all-node deployment.
Six additional all-node episodes, paired to the six leaf-only episodes above, isolate root
interference without changing training data, optimization or adapter capacity.

### 3. Divide and Cooperate — role separation does not settle credit assignment

[Park, Cho and Lee, arXiv:2606.10684v1](https://arxiv.org/html/2606.10684v1#S3),
June 9, 2026. DAC jointly trains separate searcher/generator LoRA policies. The generator's
abstention decision helps reward useful evidence without blaming search for every generation
failure. Role-separated answer-reward baselines and cross-verification ablations show these are
distinct interventions. This is search QA, not recursive record classification; its verification
mechanism is not a ready replacement for our exact label oracle.

No author-linked DAC implementation was verified: the paper's GitHub link is a Search-R1 baseline;
the [author publication page](https://www.parkjaewan.com/) links the paper but not DAC code.

**Our addition:** before a new role-aware RL objective, replay the same 18 frozen leaf requests
at base and leaf-SFT weights, then compare their errors with requests actually generated by the
fixed root. This separates leaf competence from changes in partitioning/request distribution.
Keep semantic labels distinct from inherited final reward; improvement on one is not evidence
of improvement on the other.

### 4. JSONSchemaBench — constrained decoding can change semantic accuracy too

[Geng et al., arXiv:2501.10868v3](https://arxiv.org/html/2501.10868v3#S6),
revised February 27, 2025, evaluates efficiency, schema coverage and answer quality separately.
It distinguishes compilation, over-constraint and under-constraint failures. On its three
Llama-3.1-8B reasoning tasks, constrained decoding matches or improves unconstrained accuracy;
for example, GSM8K is 80.1% unconstrained versus 83.7% with XGrammar. Therefore grammar is neither
a guarantee of semantic correctness nor necessarily a format-only intervention.

The [paper-linked repository](https://github.com/guidance-ai/jsonschemabench/tree/ba103c73756198dd9b149ddc7db7867da7a077f6)
now points to [EPFL's code](https://github.com/epfl-dlab/jsonschemabench/tree/8003e8405c4d8d8b327b1eb472c9856297d75493).
Inspected code validates schemas and integrates XGrammar; the quality-task scripts were not
identified in its tree. No code LICENSE was found there. Do not port or relicense it by assumption.

**Our addition:** schema72's exact 2×2 definitions × enum/cardinality constraint measures whether
semantic clarification and enforced shape fix different errors. Keep invalid labels wrong,
wrong-length alignment unscored, and confusion matrices separate from schema validity. The
existing vLLM API/CPU qualification suffices; no benchmark-framework installation is needed.

### 5. Let's Verify Step by Step — positive final labels can conceal wrong processes

[Lightman et al., arXiv:2305.20050v1](https://arxiv.org/html/2305.20050v1#S4.SS1),
May 31, 2023. Sections 2.5 and 4 explicitly identify correct-answer/incorrect-reasoning false
positives. On identical small-model datasets, the paper compares final-answer outcome labels,
process-model-derived outcome labels and process labels. Better outcome labeling helps, while
process supervision still wins in that setting. These are reward-model selection experiments,
not a demonstration that every recovered tool error should invalidate an RL trajectory.

The [official PRM800K release](https://github.com/openai/prm800k/tree/7ecc794703b2877f63226f2477a49b34f9b25163)
contains step annotations, labeling instructions and answer grading; it is not a full turnkey
training pipeline. No dataset was downloaded.

**Our addition:** the already-proposed six-episode original/drop-FP29/drop-FN75 comparison targets
our observed cancellation. Gold abbreviation counts become 4,4,3, whereas replaying the erroneous
assignment would imply 4,3,4. Two fresh seeds test whether the program responds correctly after
breaking the cancellation. This is stronger local evidence than reporting a rewarded count of four;
it is not a novel general discovery that outcomes can hide intermediate mistakes.

## Ranked follow-ons and claim boundaries

1. **Run frozen schema72 when the operator assigns the 4B service.** One A100 40GB, ≤72 calls,
   temperature 0.5, 256 output tokens/call, 600-second rollout cap, checkpoint every call.
   No change to its existing specification based on this literature check.
2. **Retain cancellation6 as the smallest causal failure probe.** Proposal only; use the existing
   rootless harness and fresh seeds, ≤15 minutes, per-episode checkpoints. No new framework.
3. **Conditional leaf-SFT plus role-isolated evaluation.** Use the existing 4B completion/action-
   masked trainer, a small predeclared label-supervised corpus, one adapter, 6–20 updates with a
   30-minute cap and saved step0/final checkpoints. Do not simultaneously change definitions or
   decoding constraints. Fixed leaf-request replay precedes 12 live root/leaf episodes; add the
   six all-node episodes only if a leaf effect exists. Root/leaf adapter routing requires an
   explicit implementation check; it is not currently declared ready.

All 89 mapped questions belong to one previously inspected development context. Fitting all 89
and rescoring them measures resubstitution/headroom, not generalization. Any within-context
train/untrained-record split must be frozen before fitting and remains a development diagnostic;
fresh source-context or dataset transfer requires a separately defined split. Do not select
labels or prompts from source-heldout context6. Do not feed gold labels into evaluation prompts.

The local evidence also warns against an overly strict opposite rule: failed syntax followed by
valid recovery is not the same as an incorrect label used in a final aggregation. Preserve terminal
reward, process accuracy, recovered execution errors and trainable action evidence as separate fields.
Constrained-generation outputs are not automatically admissible under unconstrained RL logprob
contracts. None of the five sources justifies silently changing current training admission.

Acquisition: 19 complete new small artifacts total 1,868,471 bytes. A capped 2 MB recursive GitHub
metadata response was retained as explicitly incomplete and unused; two missing LICENSE URLs are
recorded as 404, not treated as permissive licenses. Existing RLM snapshots were reused read-only.
