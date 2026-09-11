CPU-only audit found canonical names but FP32 checkpoint values rounded by the frozen v2 loader.
All504 LoRA tensors changed with autocast_adapter_dtype=False; maximum absolute tensor delta was
6.103515625e-5. With True all504 values and dtypes were exact. All252 B matrices are nonzero.
Both loads had zero missing/unexpected keys and no warnings. See RESULT.json for the exact inputs.

The inherited8B vLLM command also left logprobs_mode at raw_logprobs, while the trainer divided
logits by0.8. This was a probability-contract mismatch, distinct from numerical backend drift.
The additive8B revision explicitly uses processed_logprobs and unrestricted sampling support.
CPU bundled ResponsesRequest→SamplingParams verification returned(.8,1,-1,0) for
(temperature,top_p,top_k,min_p), and neutral penalties. Actual8B numerical drift remains unmeasured.

New ready artifact: /project/alex_phd/runs/rlm-research-r4/sidecars/single-gpu-rlvr-8b-v3.
The original8B attempt, current4B treatment, self-SFT source, and all checkpoints were preserved.
