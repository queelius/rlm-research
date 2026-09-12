# Fixed fresh8 RLOO endpoint: three panels

Primary: 32 short-held outputs on EXACT new replica coordinates/seeds202609270000..31, compared with both newly sampled cp32 and fixed-baseline-RL controls. This is a recipe comparison: source batches and reward baselines differ, so it does not isolate RLOO versus fixed-baseline REINFORCE.

Secondary: the original 16 long-context schedules versus their saved qualified cp32 control. Third: the original 16 four-needle ordinal-transfer schedules versus their saved qualified cp32 control. All three phases run regardless accuracy. No old short seed controls are substituted. Each panel has 16 context units; two short repeats are not independent tasks. Panels are research-exposed, not three newly held-out generalization tests.

All native task bodies, tokenized initial prompts, external context bytes, seeds, temperature .5, 2048 tokens/action, six total actions, zero children, four workers and terminal-strip-disabled hooks stay unchanged. The only new model queried is the fixed fresh8 RLOO step1. Complete, incorrect, malformed, unavailable and action-cap outcomes remain separate. Do not infer identical generation paths or lossless recovery when weights differ.

Checkpoint eligibility verifies actual original cp32 initial tensors, source input/READY, all saved state/commit/result references, twelve credited HF replay arrays/token-TIS weights and twenty zero-skip rows, gradient/Adam moments, updated tensors/delta and RNG files. No old32-replay assumption is retained. This is saved-evidence qualification, not an independent rerun of the HF gradient.

Input fixtures can run before training ends. Final sealing requires actual UPDATED step1 and terminal reusable controls:

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python prepare.py
```

MAIN alone launches each fixed phase under the shared GPU lease:

```sh
/project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py run --phase held
/project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py run --phase long
/project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py run --phase fourneedle
```

Caps science/owner/external: held900/1100/1200s; long600/700/800s; fourneedle600/700/800s. Outputs held-001/long-001/fourneedle-001. No optimizer, retries, answer fallback, extra seeds, model selection or automatic admission. Pending checkpoint means no READY, not a failed result.
