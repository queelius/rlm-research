---
schema: bounded-research-decision-note-v1
id: qsr-sparse-reward-response
as_of_utc: "2026-09-09T22:46:02Z"
status: proposals_only_active_campaign_unchanged
primary_methods_examined: 3
read_depth:
  retool: "arXiv2504.11536v1 sections2.1–2.3 and3.1; no code execution or reproduction"
  harness_1: "arXiv2606.02373v1 sections2.1–2.3, reward table5 and ablation AppendixM opening; existing local provenance receipt, not a new full-code audit"
  tool_rl_collapse: "arXiv2606.26027v1 sections4.2–4.4,5.3–5.4, limitations; official Tool-RL-Box README only, no commit-pinned code reuse"
  local: "targeted results/mechanism sections of receipt/interface/complete/corrective/clarity reports; current qsr_native.py prompt and frozen design"
current_qsr_evidence:
  origin: "MAIN preliminary first2window report; not independently reaudited here"
  planned: 48
  native_available: 43
  correct: 0
  adam_updates: 0
  window1_child_calls: 0
  window1_strict_wrong: 13
  window1_prose_or_empty: 9
  window1_correct_numbers_in_invalid_prose: 5
  primary_rescoring: forbidden
immutable_boundary:
  qsr_groups_sha256: 99984ddb15ac2b15ccf86a2cdcfa40016ff86507b5448b1ab29695187e9765c6
  qsr_provenance_sha256: 6c1bce9e30f48f159ba24450883e7a1c036869eb3ae33d5bcddacc29f4d09c4b
  qsr_native_source_sha256: 02aea033ef02a215577af03e18769adda0d9994e947900b310b1a7ee8356441c
  source_groups: "QSR192 training /256 readout; never mix; child-training-exposed; prior/adaptive research exposure disclosed"
  transfer48_groups: "separately sealed64 outside QSR448; never borrow for proposed training"
ranked_jobs:
  - id: diagnostic_contract_x_actual_evidence
    rank: 1
    root_endpoints: 24
    source_acquisitions: 2
    gpu_shape: "one4B root plus fixedc32 child on existing A10040GB"
    outer_seconds: 1200
    episode_seconds: 120
    launch_requires_main_approval: true
  - id: matched_native_operator_sft_then_rl
    rank: 2
    teacher_trajectories: 36
    maximum_training_child_calls: 90
    sft_updates: 4
    rl_planned_endpoints_per_arm: 96
    rl_maximum_updates_per_arm: 4
    final_readout_per_policy: 24
    final_policies: [rl_only, sft_only, sft_then_rl]
    outer_seconds: 5400
    work_seconds: 5100
    owned_seconds: 5280
    launch_requires_main_approval: true
mutations_performed: "new note only; no model/service/lock/queue/campaign/source changes"
---

# Sparse exact reward: test reachability before changing the objective

Zero Adam updates means the reported early failure **cannot be attributed to this run's RL-induced collapse**. It is evidence about the starting policy and reward accessibility. Zero child calls also does not prove missing computation: roots may classify directly. Five correct numbers in invalid prose identify an output-contract gap, but remain observed0 under the frozen scorer. The43/48 availability and bounded nonreturns remain separate; later QSR windows may change this preliminary diagnosis. Do not stop, repair or reshape the active campaign on this note.

## Three primary methods: useful principles, limited transportability

- **ReTool** uses tool-executed cold-start SFT followed by outcome-reward RL; interpreter observations are excluded from policy loss. Its format/answer-filtered math corpus teaches executable trajectories, not merely copying a displayed scalar. It is a32B math study, not evidence that the same small recipe works for our4B hierarchical classifier/reducer. [Methods2.2–2.3](https://arxiv.org/html/2504.11536v1).
- **Harness-1** keeps bookkeeping in explicit environment state and uses the same renderer for teacher trajectories, SFT, RL and evaluation. However, its reward includes retrieval/answer-evidence shaping, tool diversity and turn costs; its component ablations are inference-only on trained weights. It motivates a faithful-state diagnostic, not silently adding rewards or auto-answering our task. [State/training methods and ablation](https://arxiv.org/html/2606.02373v1), [existing commit8ac4012 provenance](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/repos/harness-1-8ac4012167858f6478fb2a8fd840e4550e2af161.PROVENANCE.json").
- **Multi-step tool-RL collapse** reports post-update control-token degeneration, SFT/RL stability benefits and substantial format/content-OOD weaknesses. That supports monitoring native structural trajectories, not diagnosing every zero as lost competence. Its hint-removal/off-policy formulations must not be imported as authentic on-policy logprobs under our stricter native-history contract. The official repository also advertises process rewards; those are a different experiment. [Analysis4.2–4.4 and5.4](https://arxiv.org/html/2606.26027v1), [official README](https://github.com/hypasd-art/Tool-RL-Box). No repositories, dependencies or model/data weights were acquired or executed in this review.

## Local evidence rules out easy slogans

Receipt72 went21/24 familiar-prompt correct versus0/24 in both new packages, with no children in either new package: compatibility can dominate capability. Later receipt-uptake confirmed actual helper use, yet both child completeness and root consumption failed. [Receipt72](../analyses/receipt-ablation-live-2026-09-09/REPORT.md), [uptake audit](../analyses/receipt-uptake-live-2026-09-09/REPORT.md).

Interface SFT increased child use but only1/24→2/24 exact;22/24 first actions copied the four-record example. Complete-demo SFT regressed8/16→1/16 in both treatments; added scalar-copy loss was already almost saturated, while roots usually stopped after maps. Corrective SFT produced acquisition loops and context-related NULLs, demonstrating a mismatch between teacher starting states and free reachability. These retire narrow recipes, not SFT as a category. [Interface](../analyses/root-interface-sft-live-2026-09-09/REPORT.md), [complete-demo](../operations/2026-09-09-allocation-5780/complete-sft-audit-report.md), [corrective](../analyses/root-corrective-reduction-sft-live-2026-09-09/REPORT.md).

Accurate schema wording removed field errors in clarity96, but map loading was not map use, and wrong child evidence limited final correctness. Current QSR already names actual `id/user/text/weight`, predictions and strict final syntax correctly; simply repeating that old fix is not a new hypothesis. [Clarity audit](../analyses/root-map-contract-clarity-live-2026-09-09/REPORT.md), [actual QSR prompt](../sidecars/root-query-sensitive-rl-v1/qsr_native.py).

## Rank1 — smallest discriminating native diagnostic

After QSR release, freeze the **initial low66c**, first two QSR training contexts and their original three supported operator queries: six query blocks, one fresh paired seed, four arms =24 native roots. This is an exposed-training diagnostic, not a held-out score. Two factors:

1. Current native coding-role system versus a compact task-solving system role: “Solve the user's task. Tools are optional. When finished, return only Answer: N with a nonnegative integer.” Keep identical task/query text, native tool inventory and executable runtime; do not add example code, an algorithm or grammar. This is a disclosed system-role intervention, not a public-harness capability claim.
2. Free raw records versus the same records plus one complete **genuine c32 prediction map** visible inline before action1. Acquire once per context with the already-qualified final-only classifier contract, freeze raw bytes/errors, and do not select by semantic correctness. A structurally failed acquisition makes its six state-supplied coordinates NULL; raw arms still run. This intervention supplies evidence, not a host count or gold label. Charge each supplied-state pipeline its whole acquisition, separating two physical acquisitions from12 hypothetical charges.

Primary remains strict dataset correctness, with availability/bounds and operational success. Diagnostic endpoints: strict map-consistent answer, actual scoped/count/distinct/weight program and output, chosen child calls, control-token/tool-parser failures, and correct-number-in-prose (never a rescue score). All four arms preserve raw traces and matched caps. Balanced order;1200s outer,120s/root, four workers, unchanged2048-token action/8192-context caps. Two contexts are mechanism probes, not independent confirmation.

Interpretation: a role gain with the same evidence supports contract compatibility. High map-consistent performance across all three operators but poor free performance implicates acquisition/reachability. Format-valid wrong answers despite complete evidence and actual field access implicate scope/operator/state-use failure, not necessarily inability to execute an operator. If both supplied-state arms still fail, perform trace-level primitive analysis before further end-to-end training. A ≥2/6 paired strict gain across both contexts is an exploratory promotion trigger for a larger fixed test;5/6 map-consistent answers spanning all operators is a useful conditional-capacity signal, not a theorem or gold-accuracy substitute.

## Rank2 — native operator warm-start followed by unchanged-reward RL

Conditional on the diagnostic identifying a teachable transition, use first six QSR **training** contexts and their original supported operator/scope cells:18 queries × two acquisition layouts =36 complete native teacher trajectories. Vary query-dependent record selection, accumulation names, batch4/16 and three genuinely different reductions. Every root target follows a real native prefix, actual c32 acquisition and executed observation; no copied map literals, held-out gold or operator-specific answer shortcut. Preserve erroneous child labels/scalars and all failed attempts. Require the predeclared corpus, not a success-selected subset or rerolls. Avoid adding redundant terminal loss as the proposed mechanism.

Train root-only four fixed updates from low66c, with fresh Adam, current-action suffix masks, child/observation masking and explicit producer/reduction/stop masses (.40/.55/.05). Authenticate checkpoints and meaningful nonliteral decision/reduction NLL before gradients; terminal NLL alone cannot pass the gate. This is proposed operator/trajectory breadth plus a loss recipe, not an isolated token-budget-matched causal factor. Audit all exposure and costs.

Then compare matched **RL-only** and **SFT→RL** branches on four later, predetermined QSR training windows,24 roots/window. Keep exact original sparse terminal reward, advantages, native behavior histories/logprobs and zero-variance skipping. Cap each branch at96 planned samples/four actual updates; report skipped updates rather than fabricate signal. Save fixedSFT4 and every committed RL checkpoint; final readout compares RL-only last-committed, SFT4-only and SFT→RL last-committed, never best-validation checkpoints. Freeze four QSR readout contexts ×three held-out operator/scope cells ×two seeds =24 endpoints/policy, group-disjoint from all training. QSR may already expose their results to researchers; disclose adaptive follow-up and do not use those outcomes for selection. Transfer48's64 groups remain separate.

Budget: one existing A10040GB;5400s outer,5100 work,5280 owned; acquisition600, SFT600, RL720/branch, final readout480/policy, service readiness≤180 each, all intersecting the shared clock. Full planned inventories survive cap exhaustion. New physical work and sunk prior training stay separate; attempts, returned completions, unknown usage and billing remain distinct.

Promote only if the warm start creates mixed exact rewards on multiple training groups **and** held-out operational/strict gains with actual query-dependent reductions; compare SFT→RL to SFT-only to establish any RL increment. If only formatting improves, state that narrow result. If reward stays all-zero, copying/looping rises, or the gain disappears across operators/contexts, retire this recipe and revisit interface/task decomposition—not more blind epochs or a retroactive partial-credit reward. Interleaved SFT is a later separately authorized experiment if post-update instability actually appears, not the default remedy for0Adam.
