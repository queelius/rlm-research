# Parent-owned launch and resume

This is an independent original-root campaign, not continuation of the one-step pilot.
Initial root857a7ce6…; fixed childc32de129…; persistent AdamW across exactly eight fresh
generations if all resource/data/numerical conditions succeed. No GPU call occurred in preparation.

After the parent finishes its current GPU clients and stops its own service, inherit the already
qualified CUDA library environment, one assigned CUDA_VISIBLE_DEVICES value (device index or MIG
UUID), and STRICT_RLM_CALIBRATION_API_KEY. Do not print the key. The coordinator refuses occupied
ports18601/18611/18621; it never stops a different service to make room. Only this command authorizes
its serial service start/stop operations. No co-resident training/inference is budgeted.

CPU verification:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-campaign-v1/campaign.py verify
```

New campaign (the inherited CUDA_VISIBLE_DEVICES must already name the sole assigned device):

```bash
PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-campaign-v1/campaign.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-campaign-v1/outputs/attempt-001
```

After an orchestration interruption, same output and same device assignment:

```bash
PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-campaign-v1/campaign.py resume --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-campaign-v1/outputs/attempt-001
```

Resume authenticates the original RUN deadline/device/campaign and contiguous committed checkpoints.
An already saved adapter/Adam/RNG/state advances the cursor even if RESULT was not written; a
changed correction capture, group, or input binding is rejected. Completed rollout records can be
exported without model reruns. Incomplete pre-step attempts and STOP records require diagnosis and
an explicitly amended/new attempt; this command never retries their model calls, adds seeds, or
reuses a completed generation for another optimizer step. Global time is never reset by resume.
An INTERRUPTED_AFTER_COMMIT record is resumable because the valid actual step has been retained.

The process lock prevents a second campaign coordinator even with another output path. Service
termination uses only the captured PID/process-group/start-time/command identity and its unique
config path; PID reuse or lingering occupied ports causes a stop, not broader cleanup. New service
config/log files can contain the local API key and are restricted to owner access; do not paste them.

## Fixed schedule and budgets

Checkpoint0 validation8 → fresh training32 → update1 → fresh training32 → update2 → validation8,
then the same pattern through checkpoints4/6/8. The service just loaded for validation also collects
the next generation. Every root update reloads exactly its rollout adapter and carries Adam moments
and RNG from the previous checkpoint; the child adapter is never loaded by the trainer.

One full-batch current-root-only action objective, LR5e-5, wd0, clip1, FP32 LoRA/BF16 base, T.5,
token TIS cap2, unchanged guards. Child/tool/prior-root prefix tokens are masked observations.
Completed observable malformed/wrong policy outcomes are0; failed/incomplete capture isnull.
Selection uses all genuine mixed within-task groups without requiring recursion or any action shape.

Eight training workers were explicitly approved by the parent before READY. The inherited collector
dispatches two-row queue items: training32 has up to8 active episodes; validation8 has only4 queue
items and hence at most4 active episodes. vLLM max_num_seqs16 is unchanged. No budget/reward change
was made to accommodate long tails.

Four-hour global envelope includes transitions, validation and transfer. Caps: service-ready180s,
collection1800s, training load+optimization600s, validation600s, paired transfer1800s total including
its two service cycles. No new training collection starts below900 remaining seconds. The global
deadline wins; a completed optimizer step may finish immediate checkpoint serialization. The
inherited collector reserves60s for finalization and can discard partial traces; those remain
infrastructure/budget exclusions, not policy negatives. Any capped collection stops this campaign.

Select the earliest maximum strict success count among checkpoint0/2/4/6/8 on the same eight frozen
validation coordinates; show all eight planned coordinates and excluded counts, not a cherry-picked
success denominator. Report final8 separately. Only after selection, compare original versus selected
root on the frozen24 transfer pairs with the same child. The new384 question groups are disjoint from
pilot/root validation and prior composition questions but are source-training/child-SFT-supported.
They are not a claim of unseen leaf knowledge or absence of base pretraining contamination.

## Artifacts and interpretation

- RUN.json: original start/deadline/device and campaign hash.
- services/*: immutable binding, actual endpoint/base/adapter hashes, image/service evidence and
  authenticated service ownership. Native role audits retain actual request/alias/depth and wire IDs.
- round-NN/GENERATION.json: current root/config/optimizer/RNG/state hashes plus fresh coordinate hash.
- round-NN/collection: actual native episodes, exact root-only EPISODES/GROUP and export MANIFEST.
- round-NN/training: authenticated INPUTS, correction captures/guards, STEP_STARTED, checkpoint-N
  adapter/config/optimizer/RNG/state; COMMIT is reconstructed from a valid state when necessary.
- validation-NN: eight unchanged coordinate replays; SELECTION.json records the fixed tie rule.
- transfer-original and transfer-selected:24 each on the exact paired questions/seeds.
- FINAL.json or STOP-*.json: actual completed update count, final/selected identity or reason for stop.

The grouped action counts are exact native IDs; sampled logprobs are not entropy and conditional
capped correction is not exact trajectory correction. Per-episode raw native wire records retain
cache/usage detail for additive compute audits; inherited derived usage fields must not be read as
zero compute. Training reports exact credited action tokens, gradient/update norms and peak memory.

Planning estimate:2–4GPUhours, not a measured guarantee. Prior service startup70.28s; parent-reported
pilot trainer update23.866s, root40 collection970.5s, unchanged validation8 replay746.4s. Those runs
used different service contention/collection concurrency; they warn that the fixed validation600s
cap can stop the campaign. No completed eight-step curve or transfer result is promised in advance.
Numerical/data/resource failures retain evidence and stop; next experiments require a separately
recorded amendment, not performance-driven edits inside this campaign.
