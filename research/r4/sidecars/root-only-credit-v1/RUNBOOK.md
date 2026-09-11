# Root-only credit Phase1

Ready for the coordinator to run against the currently bound original-root/selected-child dual service. No server startup or optimizer is included. Inherit the assigned API-key environment variable without printing it.

```bash
env CUDA_VISIBLE_DEVICES='' HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  /project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/capture.py run \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/outputs/attempt-001
```

After terminal collection, export separately without GPU:

```bash
env CUDA_VISIBLE_DEVICES='' HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  /project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/root_export.py \
  --attempt /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/outputs/attempt-001 \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/exports/attempt-001
```

Collection is40 episodes:32 root-training episodes on8 tasks/four contexts/four seeds, then logically separate8 root-validation episodes on4 tasks/two contexts/two seeds (dispatch is hash-shuffled). All six contexts contain64 unique source-train question groups; none overlaps leaf validation/test or the384 composition-transfer groups. Source-train questions were seen by the child SFT, intentionally. This does not assert absence of base-model pretraining contamination.

Both roles use native TrainClient, Qwen3 renderer `enable_thinking=True` without an empty-thinking prefill, T=.5, top_p1/top_k-1/min_p0,2048 requested tokens, depth1 and no compaction. The public definitions-enabled executable example and strict count reward are unchanged. Gold is host-only; only public prompt/context text is provisioned to the owned rootless runtime. The inherited collector uses four workers, a1800-second cap, atomic per-episode output and an execution-error stop above50% after8 episodes. Unique runtime names and owned-container cleanup are inherited; no broad cleanup is performed.

The exact native wire and graph are retained per call, with trusted depth, invocation, request ID, actual role alias and adapter hash. The current append-only serving-log prefix proves `processed_logprobs`; stale endpoint metadata is not substituted for that evidence. Runtime verifies both advertised alias/root/parent bindings and both adapter files/configs. Original root is the exact PEFT-key-converted original504-FP32-tensor checkpoint; child is the validation-selected checkpoint-0128. Serving may cast stored FP32 adapters to BF16; disk identity is not live-memory dtype attestation.

Exports preserve all recorded episodes and every role's evidence. `turns` contains only depth0 current actions, with their true physical prefix masked. Earlier root/child actions and observations never receive root loss. `all_role_evidence` is diagnostic only and must not be fed to the trainer. No message retokenization or alias falsification is used. Completed observable wrong/malformed answers retain reward0; infrastructure/incomplete-capture failures have rewardnull. The inherited collector can discard partial traces on failure; this remains an explicit limitation. A complete collection with actual mixed training groups produces `training-group.json` and authoritative within-task standardized advantages. Validation never enters that file. Without mixed groups, no learning group is manufactured.

Verification: four focused red→green tests; F-rule static checks; actual owned rootless runtime → native client/renderer → CPU fake provider → child → root proof with3 calls,2 credited root calls and1 evidence-only child call. Exact physical prefix/native-wire token and logprob equality passed. Fixture probabilities are explicitly synthetic, not model measurements. No real model/GPU calls were made during preparation. Frozen spec/source verification passed after source stabilization.

SPEC SHA256: `bc38dadf55e6a45cd7c9a417cdafbc52a50494c3bfb6991752e7d0e500a8c4ed`.

Coordinate plan SHA256: `e8c0725149efb72a3fa2514432ed2f1e390ad2cc4b1238c98ffe4c8ccab937c5`.

CPU proof SHA256: `8d73f4951837a9d4bdb7b0e6656230d3e2662184cc70c2d02b4d411248d40779`.
