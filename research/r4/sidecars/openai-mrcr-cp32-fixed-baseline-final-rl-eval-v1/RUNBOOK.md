# Fixed cp32 + one final-decision RL step: held and long readouts

MAIN-only launch. Both stages evaluate the fixed new checkpoint-0001, without a train-readout accuracy or manipulation gate. No endpoint selection. The original qualified cp32 controls are reused: short `openai-mrcr-procedural-sft-terminal-strip-disabled-v1/outputs/held-checkpoint32-001`; long `openai-mrcr-long-transfer-eval-v1/outputs/checkpoint32-002`. Long attempt001 failed service startup and is not a comparator.

Short has 16 context units × two original seeds =32 episodes. Long has 16 distinct context units × one original seed =16 episodes. Preserve all planned denominators and separately report correct/wrong/unavailable, paired available wins/losses, official unnormalized string scores, actual Python selection/clean stdout versus final-copy errors, and full physical native usage/failed/start-only calls. Neither repeated seeds nor individual tokens create independent context units. These panels are research-exposed; base pretraining is unknown.

The exact original schedules, task JSON, external context bytes, host-only gold, root-prefix tokens, system/tool template, T.5/top_p1/top_k-1/min_p0, 2048 per action, six total actions, zero-child configuration, renderer and terminal-strip-disabled hooks are reused. No T1 changes. Both service startup boundaries point to accepted runtime-an22/service_wrapper_v2, including the long V2 dependency repair. This is a cross-service comparison, not bitwise native generation or a matched total-cost claim. New model weights can change tool calls, not just the final answer.

```
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-cp32-fixed-baseline-final-rl-eval-v1/owner.py verify --phase held
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-cp32-fixed-baseline-final-rl-eval-v1/owner.py verify --phase long
```

MAIN uses the corresponding `owner.py run --phase held` and `owner.py run --phase long` under the shared lock, with its assigned CUDA device and private credential. Short caps600science/900owner/1000external seconds; long900/1100/1200. Output paths are `outputs/held-001` and `outputs/long-001`; never reuse either. Run long regardless of short accuracy. No retries or answer fallbacks.

Checkpoint eligibility authenticates the exact trainer READY, successful/reaped owner, RESULT and commit, source input SHA and fixed ±.5/32 objective, all 32 saved replay pairs, recomputed capped token-TIS weights, actual initial tensors against cp32, saved gradient/Adam first moments and second moments, step counters, exact optimizer hyperparameters, final tensor identity/delta, RNG files and actual root/child binding. It does not rerun HF scoring independently. All source-to-final artifact hashes are frozen, including the now-completed endpoint; no fabricated future adapter hash.

Primary comparison is new versus cp32 on both fixed panels. Teacher-forced training likelihood and the smaller wrong-final likelihood are not heldout gains. A decrease in newline-copy errors with preserved clean retrieval supports a narrow learned terminal-fidelity improvement; procedure changes, copy failures and unavailable episodes remain visible. Shared LoRA weights prevent a claim that only the final policy changed.
