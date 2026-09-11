# Exact-conversion native MRCR control

Ready for the coordinator to launch against the original alias on the assigned dual-adapter service. This is an additive amendment, not a replacement of the unused v1 source or spec.

```bash
env CUDA_VISIBLE_DEVICES='' HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  /project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/mrcr-native-direct-six-v1/driver_converted.py run \
  --endpoint /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-role-routing-v1/service-attempt-001/endpoint-original.json \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/mrcr-native-direct-six-v1/outputs/converted-attempt-001
```

Inherit the assigned `STRICT_RLM_CALIBRATION_API_KEY`; do not print or persist it. The driver does not start a server and requests no local GPU. Parent owns endpoint scheduling. Six requests, concurrency four, 120 seconds per call, 300-second batch cap, no retry.

The only amendment is the adapter binding: accept the one pinned PEFT-key conversion `857a7ce6…f9fcb6`, not arbitrary different weights. Fresh CPU proof compares all 504 original/converted tensors, including FP32 dtype, shape, numeric equality, and byte hashes. It verifies that the mapping is solely the `base_model.model.` prefix and agrees with the sealed conversion manifest. The original rollout adapter identity remains `e5be32e8…a8e05a8` in the spec. Exact adapter path, original alias, role-binding hash, config, and base identity are also checked. The delegated driver retains disk hashes and the runtime `/models` root/parent check. This is not live-memory tensor attestation; serving declares automatic BF16 adapter casting from FP32 disk tensors.

All six input prompts, full rendered IDs, question concatenation, seeds, T=0, full-support sampling, requested 2048 output cap, Qwen3 thinking-enabled native renderer, no-tools/no-additional-instructions policy, scoring, and raw token capture are unchanged. No input truncation or cap adaptation is introduced. Three full prompts have less than 2048 tokens of headroom under the existing 8192 service context limit; resulting length/provider errors remain separately recorded with null score, without retry. Native sampled logprobs are engine-returned evidence, not calibrated probabilities at greedy temperature. Cache/uncached counts remain unknown.

Verification: seven focused unit tests pass; F-rule static checks pass; independent full504 CPU proof and a fresh sealed-spec verification pass. The existing real TrainClient/Qwen3Renderer six-request synthetic-transport probe is retained unchanged. No real inference was run during this amendment.

Spec ID: `618a4caf115f4d0df6f3f82731410cafcfcd65de199598f68ed1a07469476782`.

Source SHA256: `3aef8d85abbb40c3c0e10e7d23e84c3686c1b377f88bf58edbeb0e8656c969c4`.

Proof SHA256: `205183a20b09a7b85d71202b219b4779368e052aef8a9e5288a5e999e9ef24c9`.
