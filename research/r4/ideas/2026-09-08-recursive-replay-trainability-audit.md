# Original-weight executable-example replay and recursive training capture

2026-09-08; CPU-only preparation/audit. Parent owns the sole MIG and all service lifecycle.

## Ready replay

`sidecars/recursive-call-example-v1/FROZEN_REPLAY_SPEC.json` is a new immutable 12-episode replay of `SELF_SFT_SPEC.json`: three development tasks (12000008, 12000009, 12000025), two identical sampler seeds per task, abstract/example paired conditions. Exact equality checks passed for plan, tasks, environment, example code, image, split provenance, concurrency and wall cap. Only endpoint/request model, endpoint provenance/source seals and weight condition differ. EvalClient, temperature 0.5, top_p 1, top_k -1, min_p 0, max_tokens 2048, depth 1, four paired workers and 1800-second study cap are unchanged.

The new descriptor `operations/2026-09-08-resume/frozen-replay-planned/endpoint.json` explicitly says `planned_not_loaded`. It declares port 18601 and alias `strict-rlm-qwen3-4b-frozen-replay`, the original Prime step0 adapter, zero updates, and the sole assigned MIG. It does not assert a currently loaded policy. Both CPU preflight and original base/adapter hash validation passed without contacting an endpoint. No frozen source or SFT specification was edited.

After the parent loads/verifies that alias, launch:

```sh
/project/alex_phd/envs/prime-rl-5990b1b/bin/python -B \
  /project/alex_phd/runs/rlm-research-r4/sidecars/recursive-call-example-v1/driver.py \
  --endpoint-descriptor /project/alex_phd/runs/rlm-research-r4/operations/2026-09-08-resume/frozen-replay-planned/endpoint.json \
  --spec-path /project/alex_phd/runs/rlm-research-r4/sidecars/recursive-call-example-v1/FROZEN_REPLAY_SPEC.json \
  --weight-condition pre_update \
  --output-dir /project/alex_phd/runs/rlm-research-r4/sidecars/recursive-call-example-v1/outputs/frozen-replay-001
```

This completes the weight-by-example contrast; it is not a training collection.

## Child inheritance and export conclusion

Pinned nano-rlm `supervisor.py:328` creates children with a copy of `parent.runtime_config`, changing only `invocation`; model and provider URL/secret are inherited. Verifiers `harnesses/rlm/harness.py:101` supplies the model and per-rollout interception provider. `interception/server.py:270,483,498,680,722` resolves that secret to the same session, imposes `ctx.model` and `ctx.sampling` on each request, uses the same session client, commits responses into the same trace and records each call. Thus children of a native TrainClient rollout use TrainClient, not an implicit EvalClient. Sampling also reuses the episode's seed; child calls are not separately seeded independent rollouts.

`clients/train.py:112,150,324,426` captures prompt IDs, sampled completion IDs and completion logprobs for every intercepted call. This code path has no root-only exclusion. The exporter `causal_turns()` already traverses all official physical `WireTrace.branches`, deduplicates sampled node identities, keeps each call's actual prompt prefix, masks earlier actions/observations, and audits actual model, temperature, support and usage. Semantic call/return links identify recursion but must not be concatenated into causal token prefixes. No recursion-specific change to this core algorithm is indicated; two bounded existing CPU branch/capture tests passed (3.17 seconds).

However, **existing example12 records cannot train all calls unchanged**: all are EvalClient. The completed self-SFT example artifact contains 94 model calls, with 64 committed child-call and 64 return edges across three episodes (10, 18 and 36 children); every call has the correct alias, temperature 0.5 and full-support sampler, but no node has exact token IDs or logprobs. This verifies shared routing/sampling empirically, not recursive TrainClient token capture. A separately declared native TrainClient collection would be the smallest empirical capture qualification. Its additive export provenance must bind the actual new serving log/descriptor: the frozen `export_attempt()` currently reads the original `inference-attempt-002/inference.log`. Do not silently reuse that historical evidence for a new service.

All-call credit remains one terminal episode reward applied to all captured actions, not independent correctness supervision of child answers. Completed malformed policy actions with complete capture may legitimately receive reward zero. Infrastructure errors or unpreserved actions remain untrainable with reward null. Intermediate child-schema validity is a separate metric; terminal success does not establish it.

## Source seals

All relative paths above are under `/project/alex_phd/runs/rlm-research-r4/`.

- Replay spec: `eaece2b36ded2ec3880b14bca36289de1e4cf136a9f449230c26859e2795a18e`; planned descriptor: `2168bba4f7366617481f955b190cc1f53847a30c267e8493c71ed9e2c3f8410a`.
- Shared plan: `fb9576dca3b6e810a9b122f3646ac69fdb82d739f2d18d2beac90553f20fba85`; unchanged SELF_SFT_SPEC: `714b27605e2a28a1a3cb3c23a5a8eec25c5ce23e71a0fe03d3aa1449af5fc351`; unchanged recursive driver: `45a839de6790f0ee710fcc171af768b7e2b19b160bad7ef9aba524aee6ec31b3`.
- Original adapter model: `e5be32e83aa00893f7c75074d79843b8a7f88cc4cf794fab75ca00c7b48e05a8`; config: `e6828a7cbb97028a871958e71ba6b8a75ac4887c25008ac4dbf7366bd298fbc4`. Full paths/base manifest are sealed in the descriptor.
- Nano source: `/project/alex_phd/research-cache/2026-09-08-literature/recursive-example.6xBrmx/src__rlm__supervisor.py`, SHA `1b9a1b303b7c2a389d8981d0c7ea9d3e5603b49f8a420f354220c6a28c9cc78e`, upstream revision `4ef3438d55fdd39b18d34035833c73e13b006733`; adjacent PROVENANCE.json records public URLs and MIT license.
- Verifiers sources under `/project/alex_phd/research-cache/repos/prime-rl/deps/verifiers/verifiers/v1/`: harness `7256f1efe1d0b44c8488e62edc93c41fa2da1fae95620bc6de4dea2e7d517bfc`; interception server `d96061ec740017cc10bcbe63ba2d378b67558f22b07b0c1303399d9f4787da08`; TrainClient `87356166967c2cd283e6212dc32f955590e6722bc7636f2af13df301f6e53705`; chat dialect `fe932c3696df7e25e22b4ff4b5ba002adba3efeb26527912f47d0b3cae23d665`; trace `6c1faba764aacf7bccdbb41d717271706f5f02ad2c411dce02788b60ed7eb099`.
- `sidecars/strict-rlm-client-qualification-v2/export_causal_turns.py`: `47beb310b1089603a84c0b1ef9f311c2a5f92197f76daac9728af60c3e9145c2`.
- Recursive empirical records under `sidecars/recursive-call-example-v1/outputs/self-sft-001/episodes/`: `7f5ec67a...json` SHA `52fb4c59c6a4b9e69fcf361469e5d38dfbf4a4da2e2c1f690af1ca191f51fdc7`; `8c3111d9...json` SHA `4ae3b348432b2d81bceb7ce8c826ff1b8fbcb759991fd420f76a0b6f5b455761`; `bbeb8d19...json` SHA `cb4169fe50d55702db07c4bce5f9b6b4da9cd6d3d5d5e9b1b7b71ff345ef61b9`. Full episode IDs are the unique matching filenames; aggregate analysis SHA `f5520b9c9dc4951d236b17add8dda472cd1842157b96be410ae6ad4cae66767e`.

## Separate bounded 8B estimator review

Read-only review found no estimator defect in additive `single-gpu-rlvr-8b-v3/source/run_8b.py` (SHA `2de96c888d99a7ce73f284631ed07defd8054b0e14476a11844ed8a729445910`) and `rootless_worker.py` (`c296bbe4fa90a52412e590ebe093b2de7275e2900fa34f72c947b7812254af4c`). Exact loaded FP32 adapter audit precedes forwards; dropout is off; detached cap2 token correction and same-forward HF-old are used only for one full-batch update. Actual 8B correction diagnostics and distribution-health checks precede the update. Actual controller request sampling is verified and serving explicitly requests processed logprobs. These checks are exploratory health checks, not an unbiased-trajectory or improvement guarantee. Frozen original v2 SHA `76d49edecb5780fb0027317a96c334c11afe3d773645d0bcfe9a3ea872455a0f` and TIS helper SHA `eff526cf496d3896e220d5aa0694bed3b703114e4a19d6f7c9e4f73de6240bd9` remain unchanged. No files edited, GPU invoked or heldout outcomes inspected for this review.
