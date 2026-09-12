# MAIN-only launch

The sealed seed2 source executes the exact reviewed predecessor numerical code with
new native seeds20260912900000..20260912901023 and initial HF seed20260912910000.
It uses the SAME1024 records/eight blocks, c32, policy and caps. RNG is seeded once
at step1, then full Adam/RNG restore after model construction each subsequent step.
Endpoint is only step8 on the SAME exposed512; neither data nor checkpoint selection.

MAIN supplies ADMISSION.json with authority MAIN, training_ready_sha256,
decision APPROVE_TRAINING_SEED_REPLICATION, endpoint
fixed-step8-versus-c32-on-same-exposed512, start
fresh-original-c32-not-seed1-continuation, prior_seed1_heldout512_consulted true,
replica_checkpoint_evaluated_before_training_complete false, exact
data_manifest_sha256, seed_namespace agnews-broader8-seed2-20260912, nonempty reason,
and reviewed_evidence_sha256 for the original READY_V2, FINAL_RESULT and RAW_AUDIT003.
CPU_FIXTURE_ADMISSION.json is synthetic and explicitly refused on a visible GPU.

CPU check: CUDA_VISIBLE_DEVICES='' NATIVE owner.py check-admission --admission-json ADMISSION.json.
Under MAIN's existing shared GPU flock/credential scrub/environment and external
timeout --signal=TERM --kill-after=30s 5200s:

    NATIVE owner.py run --owner-seconds 5000 --admission-json ADMISSION.json

Native Python is /project/alex_phd/envs/prime-rl-5990b1b/bin/python. One GPU only.
Stage caps remain600 owner,350 native,40 masks,180 HF,40 cleanup reserve. No retry
or automatic incomplete-step recollection. An explicit MAIN-approved committed-step
resume may use --resume-after N; prior full-chain gates remain. Record aborted dose
separately, never treat setup/likelihood failure as zero reward or choose earlierstep.

Output: outputs/attempt-001/step-008/checkpoint-0008. State/STEP_COMMIT structure,
raw native exact request/response captures, every-step importance/replay and Adam
checks are unchanged. FINAL_RESULT must UPDATED_STEP8, complete8, no errors,
eligible true, endpoint equal parent_for(9). Conditional evaluator must also rerun
the original full per-step raw/masks/order/IS/optimizer checks, not merely this owner
endpoint summary. The forthcoming separate eval READY binds these exact files.

Full owner seed1 measured2094.99s; identical provisional5000/5200 caps retained.
The known seed1 outcome prompted this prospective seed test; no claim of untouched
data or generalization beyond this training seed and panel is made.
