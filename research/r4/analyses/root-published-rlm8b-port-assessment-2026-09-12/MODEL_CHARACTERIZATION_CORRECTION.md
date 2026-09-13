---
status: additive_correction
supersedes: cached_model_characterization_only
gpu_calls: 0
---

# Correction: cached Qwen3-8B is post-trained

The original assessment incorrectly called cached `Qwen/Qwen3-8B` a Base checkpoint after reading the model-card `base_model: Qwen/Qwen3-8B-Base` field as the model identity. That field names its parent. The pinned model card identifies the cached checkpoint as `Qwen/Qwen3-8B`, states “Training Stage: Pretraining & Post-training,” and documents thinking/non-thinking instruction use. The local manifest also records model ID `Qwen/Qwen3-8B` at revision `b968826d9c46dd6066d109eabc6255188de91218`.

Therefore the claim that no instruction-capable cached 8B endpoint exists is withdrawn, and the immediate eight-call B05 calibration is no longer retired. The original protocol-mismatch caveat remains: the completed published-reference comparison changed model checkpoint, both root and child weights, template, sampling, context/output budgets, and scaffold, so it was not a matched capacity test.

The authorized new calibration uses cached Qwen3-8B in non-thinking mode for only the four frozen B05 direct calls and four frozen exact-report oracle-synthesis calls. It retains the current B05 V3 prompts, seeds, true-source grader, and output clarification. It is a model-alternative calibration—not a pure parameter-size, post-training, or architecture effect.
