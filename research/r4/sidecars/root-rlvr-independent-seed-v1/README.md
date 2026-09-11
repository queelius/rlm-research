# CPU-prepared independent root seed

Read DESIGN.md and the source-grounded ROOT_SEED_REPLICATION_BRIEF.md. No new
root96 outcomes were read while choosing or preparing this replicate.

Verify without GPU or endpoint calls:

```
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-independent-seed-v1/campaign.py verify
```

Proposed main-owned launch, inheriting exactly one reserved GPU and the existing
STRICT_RLM_CALIBRATION_API_KEY:

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-independent-seed-v1/campaign.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-independent-seed-v1/outputs/attempt-001
```

This has a6000-second inclusive cap and requires QUALIFIED_READY.json. The
original frozen common helper chooses the existing native Python for collection
and the original qualified training Python for gradient updates; no install or
environment mutation is needed. Main owns scheduling and launch acceptance.
Raw outputs, failure accounting, every checkpoint and selected/final comparison
remain within the new outputs/attempt-001 namespace. Existing source runs stay
unchanged. A failure retains artifacts and stops; no implicit retry is offered.
