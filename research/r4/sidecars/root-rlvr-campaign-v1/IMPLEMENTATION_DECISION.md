# Approved exploratory campaign implementation

Coordinator decision,2026-09-08 22:56 UTC. Implements the bounded design in
../../ROOT_CAMPAIGN_DRAFT.md under the user's standing autonomous research authority.
No launch is authorized to a worker; the main coordinator owns the single GPU.

Question: can repeated fresh-policy updates teach the root more reliable use of
the scaffold when the child policy is fixed? The pilot collection is complete:
9/32 training successes,2/8 validation successes,2 infrastructure-excluded training
episodes. Four actual mixed groups yield16 eligible root episodes. A separately
repeated unchanged validation run already has4 successes among7 completed episodes,
so tiny before/after deltas are not clean evidence of learning. The pilot optimizer
has not run yet. Implement the campaign while that pilot and independent leaf
batch-shape experiments run; do not wait for a tiny noisy pilot validation gain.

Choose an independent eight-round campaign from the exact original root adapter,
not an implicit continuation of the pilot. Keep selected child c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3
unchanged throughout. Initial root857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6;
base and qualified native renderer remain exactly as in the pilot. No grammar,
extra prompt hint, silent child change or intermediate-reward relabeling.

Eight rounds,32 new training rollouts each on the same four pilot root-training
contexts/eight tasks. Four seeds/task/round, derived as in the draft but with
namespace root-rlvr-campaign-v1 and numeric seed981260800. Validate uniqueness and
no pilot/campaign collisions. Use new validation seeds on the two existing root-
validation contexts, frozen before campaign collection,8 episodes at checkpoints
0/2/4/6/8. Select earliest maximum strict validation checkpoint and report final8
separately. Freeze six additional source-training64-record contexts before launch,
disjoint by normalized group from all384 pilot root questions and prior composition
questions, for the later original-versus-selected root comparison48. They remain
child-SFT-supported; do not describe them as unseen child knowledge.

One full-batch AdamW update per fresh rollout generation, constantLR5e-5,wd0,
clip1,FP32 root LoRA/BF16 base,T=.5,TIScap2 and existing distribution guards. Carry
Adam moments and step counter from checkpoint to checkpoint. No multiple updates
on a stale rollout group. Keep authoritative native processed probabilities,
trusted actual role identity, physical-prefix reconstruction and current-root-only
credit. Every completed malformed policy outcome is0; missing/failed capture stays
null. Select mixed within-task groups using all recorded outcomes, never only
successful trajectories or a required decomposition shape.

Use existing serial service lifecycle; no co-resident inference/training, no new
weight-update transport. Use eight concurrent pair workers (coordinator refinement
before campaign readiness,23:13 UTC) versus the pilot's four, with the unchanged
sixteen-sequence serving limit. This spends available CPU/RAM to better batch useful
inference; it does not assume identical-seed trajectories are deterministic. Record
actual throughput and long tails. Four-hour global envelope, round collection1800seconds,
training600seconds, service-ready180seconds, validation600seconds, transfer1800.
Record the long-tail risk: two pilot trajectories greatly exceeded the median;
changing episode termination/reward semantics would be a separate protocol. On
no mixed group, bad role/mask/identity, failed distribution guards or resource cap,
retain evidence and stop this campaign. Do not manufacture a completed eight-step
curve. Coordinator may later diagnose and start an explicitly amended experiment.

Implementation must be small additive research code, not a generic framework.
Reuse frozen capture/export/math/serving helpers while parameterizing immutable
per-round binding and source manifests. Keep every existing sidecar unchanged.
Write raw episodes and current-round manifests atomically, checkpoint immediately
after each actual step, retain optimizer/RNG/cursor, and recognize an already saved
step after an orchestration interruption rather than applying it twice. Verify
initial and resumed tensor identities and the unchanged child hash.

One focused CPU qualification of two tiny fresh generations, persistent optimizer
steps1/2, no child gradients, stale-generation rejection and crash-after-checkpoint
recovery is sufficient before parent review; no broad repository suite. Publish a
sealed READY last, exact run/resume commands, expected artifacts and measured versus
estimated cost. Worker preparation makes no GPU/model calls and does not stop or
alter the active owned service. Questions go into metadata, not to the AFK user.
