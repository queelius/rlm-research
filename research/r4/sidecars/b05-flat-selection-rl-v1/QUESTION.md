---
question: Can a single balanced-accuracy policy-gradient update improve actual eligible-ID selection beyond the all-ID prior?
status: CPU_preparation_MAIN_admission_required
start: released_Qwen3_4B_Instruct_2507_plus_fresh_seeded_zero_B_LoRA
train: frozen_width_flat9_prompts_two_original_replies_each
reward: mean_recall_over_present_positive_negative_classes
groups: 9
group_size: 2
denominator: 18
nonzero_actions: 8
zero_actions: 10
learning_rate: 0.0001
updates: 1
gradient_clip: 1
token_TIS_cap: 2
token_TIS_unbiased: false
held: nine_new_outcome_blind_stages_two_decodes_each
readout: fresh_base_and_step1_on_train18_and_held18
readout_calls: 72
GPU_authority: MAIN_only
---

All18 native flat replies from the completed width experiment are retained; no favorable-group selection. Reward is .5(TPR+TNR) when both classes occur and the observed class recall otherwise. Every known-ID and empty-ID baseline is recorded. G2 RLOO advantage is reward minus the other reply's reward. Equal-reward pairs have zero gradient and stay in denominator18. Binary exact gives zero advantages on all nine groups and is a CPU-known negative control, not a filler GPU arm.

Loss is only over native token positions overlapping the sampled eligible_ids array, including commas and list termination. Constant object key/prompt and trailing outer-object/EOS positions outside that span receive zero loss. This is an explicitly partial-policy/shared-weight objective: it learns probabilities of selected IDs and ending the list, not supervised gold copying; ordering can move incidentally although reward ignores order. Token boundary overlaps are recorded and never determined from gold IDs. Full native prefix/action IDs and chosen logps are preserved and independently revalidated.

Initialize a new rank8/alpha16/zero-dropout LoRA using the existing adapter configuration, but never load cp32/SFT weights. Fixed seed202609320001, fresh AdamW at1e-4, clip1, weight_decay0. Save exact initial tensors/RNG. Require every LoRA B tensor zero, A inventory nonzero, and pre-update disabled-adapter versus enabled-adapter HF equality. Initial native/HF chosen probabilities are audited via the existing prospectively biased capped token-IS route (not exact sequence IS); gradient replay retains1e-5 token/1e-4 sequence tolerance. No update on nonfinite qualification, replay failure, zero/nonfinite gradient or cap. Save all qualification, gradient, Adam, RNG, delta, checkpoint and commit receipts.

Freeze nine new stages before the update using stock widths6/12/20, three per width, fixed metadata-only seeds202609320000+100*width_index+stage_index. Exclude original eight roots and current nine roots/all candidate IDs. Same original local policy/history/rendering; held responses never select examples, reward, LR or checkpoint. Fixed final checkpoint only. Fresh base and newcp1 each answer train18 and held18 regardless training accuracy, same paired seeds and actual caps. Strict format, unordered set exactness, balanced accuracy, TP/FP/FN/TN, all-ID/empty baselines and measured costs reported; held n9 material units. This asks whether local selection learns/transfers, not learned delegation/depth or benchmark novelty.

Smallest reuse: existing B05 public/native request builder and validator; existing selected-position HF logprob/replay/token-TIS/fresh-Adam/RNG helpers. New code only binds the18 rows, array mask, zero-B initialization and finite one-step owner. The native learned-adapter evaluator is a separate conditional arm using already qualified LoRA service machinery, not a modification of the no-LoRA B05 owner. No new framework, install or further dose pipeline. Initial proposed training caps900 science/1100 owner/1200 external; expected much shorter, but exact total measured after run. CPU preparation target20–30min; stop/escalate if binding requires a broad adapter port.
