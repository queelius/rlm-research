---
schema: agnews-eightstep-sft-comparator-design-v1
status: proposed-main-approval-required
created_utc: 2026-09-12
question: Does the frozen broader AG corpus contain supervised signal that the same c32 LoRA can express after eight matched optimizer updates?
recommended_arm: full-vocabulary-answer-only-sft
starting_policy: exact-c32
optimizer_steps: 8
learning_rate: 1.0e-5
unique_training_records: 1024
teacher_maps: 256
heldout_records: 512
owner_cap_seconds: 900
external_cap_seconds: 1000
gpu_launch_authority: MAIN-only
implementation_authorized: false
---

# Matched eight-step SFT comparator

## Recommendation

Use one ordinary full-vocabulary, answer-only SFT arm. At each of the eight frozen AG steps, construct one gold JSON map for each of the 32 existing four-item groups and accumulate all 32 maps into one AdamW update. Start from the exact c32 adapter, use fresh AdamW, LR `1e-5`, weight decay zero, clip one, dropout off, BF16 base/FP32 LoRA, the same initial RNG seed (`202609125000`), and carry optimizer/RNG state across all eight updates. Save a committed checkpoint after each update; checkpoint 8 is the only endpoint.

This is the smallest useful positive control for **whether these data and prompts carry learnable supervised signal**. It is deliberately not described as a pure SFT-versus-RL objective ablation: SFT scores the gold answer under the full vocabulary, whereas RL samples and replays under a grammar-masked policy and uses reward contrast plus importance weights.

Do not duplicate each gold map four times to imitate four RL rollouts. With dropout disabled and loss normalized, four identical copies add compute but no independent supervision and give the same idealized average gradient. Do not add a grammar-masked SFT arm now. That arm would better match action support, but it introduces a separately qualified loss implementation before the simpler data-signal question is answered. Queue it only if ordinary SFT moves the endpoint while RL does not and objective/support attribution becomes decision-relevant.

## Frozen construction

- Source only `helper-agnews-broader-data-v1`, manifest SHA256 `b5e9cc22161959fc09f5e1f15afd03e722a32818bca692a01f9e265fd6c81c2d`.
- For each step, collapse the four schedule repeats by `context_id`; require exactly 32 distinct contexts and identical prompt text, requested-ID order, and schema across repeats. Preserve the first schedule occurrence order; do not shuffle or select by labels/outcomes.
- Reuse the exact AG system/user messages and four IDs. Append a compact JSON object whose keys follow `requested_ids` and whose values come from that step's host-only gold. Include the native assistant end-of-turn token.
- Mask every prompt and padding token with `-100`. Full-vocabulary cross-entropy applies to the entire assistant response, including IDs, JSON structure, label values, and end-of-turn. Log loss sums separately for label-value spans versus structural/ID tokens, but do not change their weights.
- Reject any prompt-prefix mismatch, missing/extra/reordered ID, absent end token, over-context example, nonfinite loss/gradient/state, unexpected trainable base tensor, or optimizer counter other than the completed step. No truncation or substitution.
- One loaded model and persistent optimizer span all eight steps. Save adapter/config, complete Adam state, RNG, exact data cursor, per-step input/target hashes, supervised-token counts, loss decomposition, gradient norm, adapter delta, elapsed time, and peak memory.

CPU tokenization of the proposed compact targets found 256 maps and 1,024 label decisions. The gold content contains 20,335 tokens (71–89 per map); adding one end-of-turn token per map yields **20,591 supervised tokens**. Step content-token totals are `2551, 2547, 2557, 2521, 2552, 2539, 2547, 2521`; preparation must independently reproduce these counts with the pinned tokenizer before sealing.

## What is and is not matched

| Dimension | SFT comparator | Broader RL |
|---|---:|---:|
| Starting adapter | exact c32 | exact c32 |
| Unique records / step | 128 | 128 |
| Frozen four-record groups / step | 32 | 32 |
| Adam updates | 8 | up to 8, subject to unchanged gates |
| LR / weight decay / clip | `1e-5` / 0 / 1 | `1e-5` / 0 / 1 |
| Sequences / step | 32 gold maps | 128 sampled maps |
| Label decisions / step | 128 | 512 sampled decisions, four attempts per record |
| Gradient denominator | supervised answer tokens in 32 maps | fixed 128 sampled sequences |
| Action support | full vocabulary | ordered JSON grammar mask |
| Signal | teacher likelihood | reward-contrast policy gradient with IS |

Thus the clean matches are source records, grouping, start, optimizer-step opportunity, and optimizer hyperparameters—not sequence count, token count, supervision entropy, action support, or objective. Report actual RL committed steps and sampled tokens rather than assuming all eight updates occur.

## Endpoint and decision

Evaluate c32, qualified RL checkpoint 8, and SFT checkpoint 8 once on the untouched frozen heldout512 using the exact same B4, temperature-zero schedule and scorer. No intermediate heldout evaluation, checkpoint selection, or example-specific tuning. Report 512 fixed-denominator accuracy, macro/classwise accuracy, valid-map and missing counts, paired wins/losses by 128 request clusters, and physical training/evaluation cost.

A net SFT gain of at least 8/512 with macro accuracy moving in the same direction is a useful exploratory supervised-signal result; require later replication before a stable-effect claim. Interpret outcomes narrowly:

- SFT moves and RL does not: the data/prompt contain usable supervised signal; prioritize reward/objective/support/credit diagnosis.
- Both move: the broader data are useful; effect-size comparison remains descriptive because the objectives and exposure counts differ.
- Neither moves: eight low-LR updates are inconclusive about learnability; inspect saved label-span loss/gradient before spending on more mechanics.
- RL moves and SFT does not: do not claim RL superiority; full-vocabulary syntax loss and the low matched LR remain confounds.

## Compute anchor and implementation scope

The closest completed full-vocabulary helper SFT receipt used the same Qwen3-4B family and took `705.625 s` for 128 optimizer updates with 16 five-record maps/update (`trec-leaf-sft-v1`, result SHA256 `9ab06fc2ea090d1ddf1c6fac2313b55019049ba5d68f7f645cbdf8607bfc8f91`). The completed AG one-step RL HF phase took `76.352 s` for one model load plus 128 policy replays/update; its full owner took `257.138 s` (result SHA256 `7b4324c7edcbf60638d73095e364d6ffa81e2cdd80a33f4f114388fe9ca2d869`). These are timing anchors, not a runtime prediction: AG prompts are longer and the work differs.

Use a 900-second owner cap and 1,000-second external cap for one model load, 256 teacher-map forwards/backwards, eight updates/checkpoints, and final release. A timeout preserves the last committed step but is not an eight-step endpoint. Implementation, if approved, should be a thin new external sidecar reusing the proven answer-only collation/checkpoint machinery; no native service, rollout collection, extra training arm, or heldout query is needed.

No GPU run or implementation is authorized by this design.
