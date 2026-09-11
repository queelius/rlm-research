# Independent root-RLVR seed replication: source-grounded recipe and preparation plan

September9,2026. Goal: replicate the eight-update root-only result from the
original root with genuinely fresh rollout and trainer RNG seeds, keeping the
fixed c32de child, task splits, objective and selection rule. This brief precedes
any new replication implementation or outcomes. No root96 outcomes are consulted.

Source evidence is analyses/root-continuation-live-2026-09-09/REPORT.md plus
sidecars/root-rlvr-campaign-v1/{campaign.py,campaign_common.py,campaign_native.py,
campaign_train.py,prepare.py,RECIPE.json} and the completed continuation's
native_amendment.py/train.py/driver.py. The successful result combines original
campaign updates1–3 and continuation updates4–8. Starting from inherited step3
would not be an independent eight-update seed replicate.

## Fixed choices

- New namespace: sidecars/root-rlvr-independent-seed-v1 only.
- Proposed seed981265001; no collision found in existing non-output
  SPEC/READY/RECIPE/PLAN JSON. Derive all rollout seeds from new namespace,
  seed, phase/round, task and repeat. Audit against all original campaign seeds.
- Start: original root857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6,
  original converted adapter bytes, step0, empty Adam moments, no inherited RNG
  state. Seed Python/torch/CUDA with981265001 before initial training load;
  later generations restore only this replicate's exact predecessor state.
- Child remains c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3;
  it never enters the trainable model. Qwen3-4B base and model environments remain.
- Copy the original frozen training/validation task compositions and exact six
  transfer contexts, rather than rerunning seed-dependent dataset selection.
  Four training contexts/eight tasks, four samples per task =32 new episodes
  per generation, eight generations =256. Validation is the same two contexts,
  four tasks×two fresh seeds =8 coordinates at steps0,2,4,6,8. Transfer uses the
  same six contexts/twelve tasks×two new paired seeds =24 original/selected pairs.
  All344 planned episode coordinates are fixed before collection. These are
  exposed developmental contexts, not new confirmation or unseen child questions.
- Match original/selected task+seed and dispatch order within the new transfer.
  The unchanged coordinator still runs original then selected serially; this
  does not provide an unchanged-policy replay or reverse stage-order control.
  Those would be separate additions, not hidden extra calls in this seed run.
- Reward is exact observable binary strict task success; complete/capture-valid
  within-prompt mixed groups only, population-standardized advantages. Failed
  or unanswered episodes remain separate nulls. Reuse the narrow existing
  authenticated unsampled-child HTTP400 context-overflow exclusion from the
  continuation from generation1 onward; no recovered negative is newly admitted.
  Unknown failures stop. No behavior-logprob or depth/alias mask fabrication.
- Loss/math unchanged: native rollout action logprobs, temperature0.5/full support,
  root actions only; zero child/observation credit; equal episode then equal root
  turn then mean action-token loss; conditional token importance cap2,
  PPO epsilon0.2, no batch normalization of IS weights, existing guards.
- AdamW learning rate5e-5, weight decay0, clip norm1, disabled dropout,
  BF16 base/FP32 LoRA, nonreentrant gradient checkpointing, SDPA,
  max causal8192. Exactly one full-batch optimizer increment per generation;
  save adapter/config/Adam/RNG/state every update1–8. Earliest maximum strict
  success over fixed8 validation selects among0,2,4,6,8; also retain final8.
- Eight concurrent episode pairs; same per-episode/tool/decoder contract and
  existing stage limits. Work cap5880seconds, hard owned envelope6000seconds
  including120seconds reserved for final cleanup. Prior completed envelopes sum
  5484.34seconds, including467.10seconds recorded service startup; optimization
  itself297.32seconds. A100-minute inclusive cap is about90minutes plus startup/
  cleanup and modest variation. It may censor the run; no extra seed or retries.

## Minimal implementation plan

Architecture: reuse the pinned initial coordinator and trainer through private
import shims with a new common ROOT/SEED. Reuse the pinned lifecycleV2 process
ownership checks and the continuation's exact exclusion-only exporter through
new identity wrappers. No optimizer/loss/exporter algorithm or scheduler rewrite.
Existing training/native Python environments are reused without mutation.

- [ ] Add focused failing checks for fresh step0/zero optimizer state, seed
  disjointness, exact dataset preservation, matched transfer coordinates,
  unchanged recipe math and rejection of fabricated/stale generation metadata.
- [ ] Create common/prepare and small campaign/native/train entrypoint adapters.
  Copy immutable public/host data; freeze plans, recipe, source pins and manifest.
- [ ] Qualify native task reconstruction and step0 binding without service calls;
  run a small real CPU Adam/root-action math check in the existing trainer
  environment and the inherited narrow exclusion checks. No synthetic behavior
  likelihood may be promoted to a training artifact.
- [ ] Publish CPU READY only for actually exercised seams and exact bounded
  launch argv; record any remaining dynamic first-rollout dependency explicitly.
  Parent alone integrates and accepts launch. No process/service/GPU action here.

If the identity wrappers require a core refactor or readiness exceeds roughly
10–15minutes, stop with the exact interface dependency and smallest CPU-ready
alternative. Do not weaken evidence authentication to force a READY claim.
