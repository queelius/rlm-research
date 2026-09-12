---
schema: same512-seed-replication-endpoint-plan-v1
fixed_endpoint: replica_step8_only
primary: c32_vs_rl_seed2_step8
secondary: seed1_vs_seed2_descriptive_paired_contrast
records: 512
request_clusters: 128
owner_seconds: 900
external_seconds: 1000
---

# Conditional fixed-step8 readout

No new baseline query: reuse only the exact qualified c32 fresh512 source run,
redecoding its raw requests/responses again and matching all runtime fields to the
new run. Same512 is already research-exposed after seed1; this is training-seed
replication, not new-data confirmation. The original full128-call scorer, decoder,
owner, ordered schemas, temp0 seeds and batch-invariant runtime are reused without
numerical changes. Every call saves exact raw request/response bytes and metadata.

Full eligibility must authenticate original c32→eight replica commits, raw native
actions/masks/order, recomputed importance, all replay tolerances, positive finite
updates and actual serialized Adam counters. The existing per-step loop is retained
verbatim. Only predecessor launch-metadata checks are replaced by exact seed2 READY
and actual MAIN admission/segment-start checks. No earlier checkpoint is eligible.

After final fixedstep8 exists, MAIN can call:

    CUDA_VISIBLE_DEVICES='' NATIVE owner.py qualify

Then write ENDPOINTS_FIXED.json with authority MAIN, fixed_step8,
prior_seed1_panel_consulted true, replica_checkpoint_consulted_before_fix false,
training_ready_sha256 abafc45c35a038aee97ccb7a4dce4dee8c2ce03b111a9430bd2c17022ac20853,
data_manifest_sha256 b5e9cc22161959fc09f5e1f15afd03e722a32818bca692a01f9e265fd6c81c2d,
and trained_endpoints.rl_seed2_step8 containing qualifier checkpoint, state_sha256,
step_commit_sha256 and binding_sha256. MAIN supplies one GPU/private credential
under the shared lock and timeout --signal=TERM --kill-after=30s 1000s:

    NATIVE owner.py run --arm rl_seed2_step8 --outer-seconds 900

Output outputs/rl_seed2_step8-001. CPU compare.py redecodes replica and both saved
c32/seed1 reference outputs, with the SAME scorer and128-shared-B4 cluster bootstrap.
Report all512 planned, available/unavailable, changed labels, perclass, paired
gains/losses, physical usage and full owner cost. Failed/incomplete/runtime-mismatched
arms cannot support the primary comparison; missing is never wrong. Training cost
is separate; c32 is128 reused physical calls, not another128 newly charged calls.
Seed1 reference is descriptive only, not best-seed selection or pooled confirmation.

Expected endpoint owner about7.3min from all three measured predecessors;900/1000
caps remain sufficient with observed startup included. No GPU launch by preparer.
