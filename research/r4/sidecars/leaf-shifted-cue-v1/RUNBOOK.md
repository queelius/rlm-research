# Parent-owned launch

Do not run a model during preparation. `READY.json` is published last and requires MAIN acceptance. Verify using the native interpreter with CUDA hidden:

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-shifted-cue-v1/owned.py --verify
```

Only the accepted parent may run READY.launch_argv with its actual single MIG UUID, inherited LD environment and existing API-key environment. Do not replace that assignment with CUDA=0. The owned directory and `outputs/attempt-001` must not exist. The parent outer cap is900 seconds; owned870, work750, collection600, cleanup reserve120. No retry or fallback study.

The wrapper uses unchanged authenticated suite/start_service and the original actual `leaf-role-routing-v1/source/serve.py`; its launcher SHA therefore refers to its own real source, not a rebound `__file__`. It binds one exact old-c32de adapter. `--verify` authenticates source and weight closure without starting a service. The small process-absence helper is reused with its original pinned source; it does not permit releasing unrelated processes.

Outputs preserve raw per-call responses and errors, wire request UTF8/ordered hashes, actual prompt/output token IDs, timestamps and returned usage. `STATUS.json` retains all72 planned slots. `analysis.json` is an implementer projection, not an independent audit. An allowed request attempt is not proof of provider completion. Missing cache-token usage remains unknown. A completed invalid array scores0; infrastructure/unrun staysNULL.

Compare primary displayed-position scores; never substitute shifted named-record alignment. Report four context clusters per task, two seeds per cluster, actual validity and cost. No cross-task pooling, no equal realized output-token claim, no training or whole-RLM conclusion. Future independent analysis must authenticate each completed immutable stage once rather than rehash weights per call.
