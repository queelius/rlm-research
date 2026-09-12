# Fixed-model short-panel decoding replication

MAIN-only launch. All16 original short-held contexts, two NEW seeds per context, both fixed released-cp32-SFT and cp32+one-fixed-baseline-RL-step adapters:64 planned episodes. The seed is exactly202609270000+2*original_row_index+repeat, paired between models. No prior baseline outputs are reused for this comparison. Both arms run irrespective of scores. This is repeated decoding on the same16 research-exposed context units, not64 IID examples, a new dataset, or a training-seed replication.

Only coordinate/task names and seeds change. Original task text, external context bytes, initial token prefixes, system/tool template, terminal-strip-disabled hooks, T.5/top_p1/top_k-1/min_p0,2048 tokens/action, six TOTAL actions,zero children, four workers and8192 service context are unchanged. Model and optimizer states are fixed; no new training. Exact cp32 and RLcp1 parent/state/Adam/replay qualification is inherited and re-executed before admission.

```
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-cp32-fixed-baseline-final-rl-decode-replica-v1/owner.py verify --phase cp32
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-cp32-fixed-baseline-final-rl-decode-replica-v1/owner.py verify --phase updated
```

MAIN invokes corresponding `owner.py run --phase cp32` then `--phase updated` under the shared GPU lock with its assigned CUDA device/private credential. Each arm is900science/1100owner/1200external seconds. Outputs: `outputs/cp32-001`, `outputs/updated-001`; never reuse them. No model-score gate, retries or answer fallback.

The owner projection changes precisely the model binding argument and collector arm argument from literal updated to the current fixed arm. It preserves the qualified finite service-start/release implementation, using runtime-an22 at both startup boundaries. The collector is the original raw native collector with all study/checkpoint aliases explicitly bound; it has no T1 modifications or wrapper tower.

Readout: primary raw exact C/W/U and paired wins/losses at all32 coordinates per arm, with16 context-level summaries. Also preserve actual first-action programs/prefixes, clean target stdout versus returned-copy errors, malformed/no-final outputs, physical tokens/calls and owner costs. Compare the magnitude/direction to the prior two short wins descriptively, never choose a winning seed or combine the old and new seeds as independent contexts. A surviving small positive remains exploratory; a null/reversal would point to rollout sensitivity and constrain further training claims.
