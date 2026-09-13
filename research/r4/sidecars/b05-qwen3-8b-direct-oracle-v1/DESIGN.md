# Cached Qwen3-8B B05 direct/oracle calibration

Question: under the frozen B05 V3 task prompts, contract clarification, true-source grader and seeds, does cached post-trained Qwen3-8B produce valid/source-correct answers on four direct and four exact-report oracle-synthesis calls?

This is a model-alternative calibration, not a pure capacity, parameter-count, architecture or post-training effect. It changes checkpoint and uses that checkpoint's own chat template in non-thinking mode. The 4B V3 controls are retained, not rerun. There are no child or recombination calls, optimizer steps, gold answers in prompts, outcome-selected examples, or retries.

Sampling is temperature .5, top-p1, top-k−1, min-p0, root cap1024, context8192, four concurrent roots. Primary grading is true-source correctness; consistency with host exact reports is secondary. All eight calls remain in the denominator.
