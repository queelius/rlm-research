# Launch the additive lifecycle V2, not the unused V1 entrypoint

The frozen V1 campaign data, recipe, source seal and READY remain unchanged. A narrow parent review
identified a real service issue after that seal: Prime entrypoints/inference.py sets PRL::Inference
before config parsing. Whole-argv equality can reject that same process at claim or shutdown.
The V1 campaign was not launched. Use only the V2 command below.

V2 replaces the in-process ownership/stop functions in the imported immutable V1 coordinator and
adds executed-source provenance to its binding/spec functions. It does not disable any V1 source,
task, model, native-mask, generation, optimizer or TIS authentication. It accepts only the exact
qualified launcher argv or the inspected PRL::Inference title at initial claim. The stable identity
remains PID, uid, process group and kernel start ticks, tied to the authenticated SERVER_START time,
command, unique config path, request, frozen launcher hash and role binding.

Only descendants observed beneath that authenticated owned process are recorded. Shutdown checks
those same stable identities and waits for every captured parent/worker to exit; a closed API port
alone is insufficient. Detached observed descendants can be signaled individually after grace.
Changed identity, missing initial worker ownership proof, or lingering workers/ports stops the
campaign for diagnosis. There is no broad process cleanup, source rewrite, or automatic retry.

EXECUTION_V2.json binds the original RUN and actual amendment/entrypoint hashes. Every actual role
binding carries that amendment identity; every capture source manifest adds its executed source and
amendment hash while retaining CAPTURE_SPEC_V1_BASE.json. Exports/checkpoints inherit that exact
capture/role provenance. The original namespace, seeds, tasks, eight-worker choice, global4h budget,
per-phase caps, persistent-Adam recipe, strict/null rewards and checkpoint policy are unchanged.
The full experimental schedule and limitations remain in RUNBOOK.md.

Five additional focused CPU regressions passed: known-title transition, wrong PID/uid/group/start
rejection, lingering owned-worker detection, shutdown despite dead parent/closed ports only after
the worker exits, and executed-V2 source in the preserved-V1 capture manifest. All process signals
in these tests are fake; no live model/service/GPU call was made. Parent independently read the full
V2 lifecycle source and found no additional blocking issue within that bounded review.

CPU-only verification:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-campaign-v1/campaign_lifecycle_v2.py verify
```

After the parent frees the sole GPU and its owned service, inherit the qualified driver environment,
one assigned CUDA_VISIBLE_DEVICES value, and STRICT_RLM_CALIBRATION_API_KEY without printing it:

```bash
PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-campaign-v1/campaign_lifecycle_v2.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-campaign-v1/outputs/attempt-v2-001
```

Resume only the same authenticated V2 run/device/deadline after an eligible orchestration interruption:

```bash
PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-campaign-v1/campaign_lifecycle_v2.py resume --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-campaign-v1/outputs/attempt-v2-001
```

The existing coordinator lease excludes both V1 and V2 concurrent runs. No GPU authority is granted
to a worker by this readiness publication; the parent sequences the campaign after its SFT jobs.
