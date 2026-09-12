# Paired raw fixed-baseline RL audit

CPU only. The fixed source is the accepted48-episode evaluator READY c7de2ad7… with32 short-held episodes (16 contexts ×2 seeds),16 long episodes, and already-qualified cp32 controls. The new trained weights are fixed before this readout. No generated program is executed and no model is queried.

```
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/analyses/openai-mrcr-fixed-baseline-rl-paired-2026-09-12/analyze.py check --output /project/alex_phd/runs/rlm-research-r4/analyses/openai-mrcr-fixed-baseline-rl-paired-2026-09-12/readout-001.json
```

One check only. If either accepted owner is pending, save PENDING and stop; MAIN can call again with a new output filename after both terminate. Terminal failed/partial owners retain fixed denominators and explicit unavailable/missing cases. No missing-as-wrong scoring. Both complete and incomplete paired context counts are shown; repeated seeds are not independent contexts.

Independent computations: exact raw root string, unchanged marker/SequenceMatcher score, physical token array/usage/seed/cap validation, original initial prefix match, renderer decode plus actual native response conversion, clean target stdout versus copy/invalid/no-clean-target taxonomy, paired changes and context summaries, physical start/error/orphan inventories, attributed root/child policy costs and full owner/training costs separately. Costs lacking returned usage are explicitly unknown.

Reviewed reuse: causal mapping and failure availability from the source collector; official score/clean-stdout definitions from the previous independent long audit. The native conversion intentionally serializes object arguments and filters nameless invalid tool blocks; those raw invalid parser statuses are not treated as valid final text. Token arrays and terminal text are never stripped or normalized for primary scoring. Edge-whitespace equality is diagnostic only.

Model weights differ. Even identical observed prompt/action token arrays do not justify a lossless-transport or clamp-only causal claim. Changes after clean stdout support a terminal-execution association, not proof of internal reasoning or a final-policy-only intervention. All panels are research-exposed, and base pretraining remains unknown. Training-state likelihood changes are not heldout gains.
