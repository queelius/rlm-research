# Recovered-child exclusion-only continuation

Prepared for parent-owned launch; no GPU calls during preparation. This is an additive continuation of the stopped V2 campaign, not a restarted experiment or a new admission policy.

Round04 retains the exact 29 previously admitted episodes; 19 belong to the original mixed-reward training groups. All original row fields are canonically identical after removing the one added `admission_metadata` field. The authenticated unsampled child HTTP400 overflow remains excluded from training, but its completed strict-zero endpoint is reported separately. Across the 32 source episodes, endpoint outcomes are 12 correct, 18 wrong, and two unobservable. Unknown or ambiguous failures still stop execution.

The adapter, Adam state and RNG resume from exact committed step3 (`6cd68cb764ea1dc46f2e0adf1a5d692d53ebc12cd5e5ef9d9c6dbd7d949fffcb`). The untouched original coordinator/loss continue steps4–8, fixed validations4/6/8, inherited validations0/2, earliest-max selection, and the original fresh transfer pair. Round04 is not rerolled. Prior source/output files and the original STOP are unchanged; new output includes a hash-checked path map. Each actual step checkpoints. The new global envelope is 10,800 seconds from the future launch, with original per-stage caps retained.

CPU evidence: `FOCUSED_GREEN.xml` (20 tests), `CPU_RECLASSIFICATION.json`, actual inherited state-machine interception in `FIRST_STAGE_PROOF.json`, and the actual HF/native exporter authentication in `TRAINER_PREFLIGHT.json`. The first dispatched stage was training4, with zero services or subprocesses launched in the interception.

The parent must assign one exclusively owned GPU through `CUDA_VISIBLE_DEVICES` and supply the existing `STRICT_RLM_CALIBRATION_API_KEY` without exposing it. Launch:

```sh
PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-recovered-child-continuation-v1/driver.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-recovered-child-continuation-v1/outputs/attempt-001
```

CPU verification uses the same command with `verify` instead of `run` and `CUDA_VISIBLE_DEVICES=''`. A parent-authorized resume uses `resume --output` on the same namespace and preserves the existing deadline; it does not allocate another three hours.

Statistical limitation: policy-induced context-overflow exclusions censor failures from the training distribution. This amendment deliberately admits no recovered root actions and preserves the original validation selection rule. A future separately designed comparison could train fully authenticated recovered root actions on their observed strict-zero outcome; that larger amendment is not implemented here.
