# MAIN launch boundary

Preparation is CPU-only and does not reserve or probe a GPU. MAIN must first review
`DESIGN.md`, `CAMPAIGN.json`, `GROUP4_QUALIFICATION.json`, and the focused test output.
If approved, MAIN writes a one-time `MAIN_REVIEW.json` binding the exact campaign
identity, then runs `seal.py` once. `READY.json` must not exist before that review.

Under the existing MAIN GPU lock, assign exactly one MIG/GPU identifier in
`CUDA_VISIBLE_DEVICES` and invoke the owner with the qualified native environment:

```sh
/project/alex_phd/envs/prime-rl-5990b1b/bin/python terminal_owner.py run \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-question-sensitive-terminal-rlvr-recovery-v2/outputs/attempt-003
```

The parent launcher owns an inclusive 7200-second envelope. The owner alarm fires at
7170 seconds, leaving 30 seconds for parent termination bookkeeping. There is no
automatic retry or overwrite. If zero optimizer updates commit, `rl_last` is exactly
the QS6 start and the report must describe the run as no intervention/no trained gain.

Before reading scientific outcomes, verify `OWNER_TERMINAL.json`, service release, and
the exact parent EXIT/completion record. Retain all 336 planned inventory rows and all
partial/native evidence.
