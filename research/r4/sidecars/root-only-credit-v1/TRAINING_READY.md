# Phase2 root-only one-step trainer

Ready for coordinator review and CPU preflight after Phase1 finishes; no GPU work was performed during preparation. Published 2026-09-08 22:41 UTC after source stabilization and the final focused tests. A real-data preflight has deliberately not been claimed while collection is active.

## Immutable choices and identities

TRAINING_RECIPE.json was frozen at 22:27:01 UTC before Phase1 outcomes were inspected. SHA256 `f1c226b08de69f29250efc69cc0634fd17db1ffd88c0f1ef0ab2edb8a91bdb96`.

Final source/train_root.py SHA256 `131bf68610ed54b102cb6aae4b0c73635877811d887039ea8ca4a3002c701a26`; tests/test_train_root.py SHA256 `5fbed7865598134ba98cf2a739211b90f52583e4046851e95c74c2f7b9d84ef0`. Both source files are read-only. Phase1 specification is pinned to `bc38dadf55e6a45cd7c9a417cdafbc52a50494c3bfb6991752e7d0e500a8c4ed`; exporter is pinned to `70f8bc7e9897dbdfc6ac14179db476d3d626c2a8e7fe5f9e835348276b7814b5`.

Exactly one full-batch optimizer step, LR 5e-5, AdamW weight decay 0, gradient clipping 1, seed 981260500, temperature .5, TIS cap 2, unchanged v2 distribution guards. Equal episode weight, equal root-turn weight within each episode, mean action-token loss within each turn. Within-prompt population-standardized mixed binary rewards only; nonrecursive valid root trajectories remain eligible. All forwards/backwards precede the sole optimizer step, so the authenticated existing TIS math's detached current HF conditional probabilities are valid old-HF probabilities for this one update only. No resumption or second step on these captures is supported.

Exact original converted root disk adapter `857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6` is loaded with the proven exact tensor audit. BF16 base, FP32 trainable LoRA, SDPA, dropout disabled, non-reentrant activation checkpointing. The fixed child adapter `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3` is hash-checked as rollout provenance but never loaded into the training model. Child/tool/prior-root context remains masked; only each current native root action is credited. No retokenization, truncation, probability fabrication, or recursion-shape admission filter.

## Commands

Run CPU authentication once the complete 40-episode export contains a mixed training group:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/source/train_root.py --group /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/exports/attempt-001/training-group.json --preflight
```

After the coordinator explicitly frees and assigns the GPU, inherit its already qualified CUDA driver/library environment and run:

```bash
CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/source/train_root.py --group /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/exports/attempt-001/training-group.json --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-only-credit-v1/training/attempt-001
```

The training command repeats CPU authentication. It authenticates frozen source/data/model files, full collection coordinates and raw records, rebuilds mixed-group selection/advantages, and invokes the existing qualified `/project/alex_phd/envs/prime-rl-5990b1b/bin/python` with CUDA hidden to replay native export and strict outcomes. This avoids installing Verifiers into the training environment. All 40 native outcome metrics are rechecked; exact physical prefixes, actions, processed logprobs, role audits, and admitted rewards are replayed for every selected episode. Original source and exporter files remain untouched.

Stop if no mixed group exists. Existing output paths are rejected. The 600-second signal cap covers model loading and optimization, beginning after CPU authentication; it is disabled immediately after the actual update so the adapter/optimizer/RNG checkpoint can be retained. Full wall time additionally includes CPU authentication and checkpoint serialization. Native replay has a separate 180-second CPU timeout. The fixed 8192-token native causal limit is a rejection bound, not a truncation policy; no launch has established real-sequence GPU memory use yet.

## Evidence and retained outputs

Final verification: six focused tests passed in 7.73 seconds with CUDA hidden, and Ruff checks passed. Tests cover root-only masks and role/weight identity, native logprob sentinel rejection, mixed-group eligibility without recursion requirements, actual tiny Qwen3+PEFT update with unchanged base tensors and FP32 adapter serialization, one saved optimizer step, and distribution-guard failure retaining correction capture without any parameter update. The sixth test replays the existing real rootless native root-child-root CPU fixture: two credited root calls and one uncredited child call. Fixture probabilities are synthetic CPU test values, never research measurements. The benign PEFT save warning concerns the tiny test model's intentionally absent pretrained config path.

The real run records INPUTS.json with immutable input/execution identities and exact adapter load audit, runtime versions/device, correction-capture.json with token-level native/HF logprobs and TIS diagnostics, checkpoint-1 adapter/config/optimizer/RNG/state hashes and input cursor, and RESULT.json with actual optimizer step, gradient norm, parameter delta, counts, peak allocated/reserved GPU memory and elapsed times. Failures retain available capture/checkpoint artifacts and an explicit FAILURE JSON. No leaf-action or observation loss tokens are reported as training credit.

Preparation changed only the four assigned Phase2 files. No shared clone, active service, Phase1 source/output, prior TIS/SFT source, or environment was modified. This readiness publication is the final source-preparation operation; subsequent fixes require coordinator acknowledgment and a new recorded source identity.
