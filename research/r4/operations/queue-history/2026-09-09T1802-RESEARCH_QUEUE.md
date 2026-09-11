# Live GPU research queue

Updated September 9, 2026, at 18:02 UTC. MAIN owns GPU launch and cleanup.

## CURRENT: resumed allocation5780 on an27

User resumed this same conversation at17:54UTC. One exclusive A10040GB full MIG
`MIG-d3fcfaa9-e5d5-59f3-854c-01f98007d465`, CPUs0..15,64GiB, driver580.159.04.
Lease ends September11 17:32:38UTC (1789147958). GPU initially empty; Torch CUDA
check passes with the inherited new driver library. Original complete-SFT READY
verifies freshly on this node. Old node-local runtime is absent; runtime_port
prepares a new bounded cache and native CPU fixture at
`sidecars/runtime-an27-5780-v1`, while MAIN prepares accepted SFT parent
`operations/2026-09-09-an27-complete-sft`. No new GPU job has launched yet.
Record time to actual first COMMAND as startup cost, not training or inference.

CPU parallel work: bridge_audit has preliminary64actual-native endpoints from two
completed variants; full audit is pending. reducer_prepare implements the approved
fixed-RL4 actual-map/oracle-map × ordinary/count_labels comparison,32episodes plus
four real-map acquisitions,1350outer. This corrects the new brief's low66c/raw-context
misstatement. It is preparing, not READY. New session plan and allocation metadata:
`operations/2026-09-09-allocation-5780/`. The stop instruction below is historical
and superseded by the user's resume; continue useful GPU-first research here.

## Historical transfer snapshot at17:53 UTC
The [15:05 snapshot](2026-09-09T1505-RESEARCH_QUEUE.md)
preserves the previous chain, evidence and recorded scheduling losses. Accepted
study sources, failed attempts, raw outputs and sealed analyses remain immutable.

## Allocation and running work

One exclusive A100 40GB full MIG on an21, Slurm5771; ends **19:07:17 UTC**
(epoch1788980837). Eight logical CPUs32–35,96–99 and64GiB host memory.
**User-requested transfer:** the user already has a new48-hour A100 allocation
and will resume this same Codex conversation there. Stop the old allocation's
loop now; the earlier instruction to continue until19:07:17 is superseded.
No experiment or accepted waiter remains running. Read the
[transfer handoff](../2026-09-09-to-48h-allocation/HANDOFF.md).

| State | Question and actual authority |
|---|---|
| COMPLETE: fixed higher-rate SFT8 bridge32 | `operations/2026-09-09-after-bridge-rl4-highlr`; ended17:37:29.4825904UTC,506.365s,exit0,GPUempty. TERMINAL644533b3…/STATUS80dbd379…. Parent99453 is absent. Exact same32 coordinates with root0ba42364. Outcome audit pending, not an accuracy claim. |
| CPU READY, NOT LAUNCHED: matched complete-demonstration SFT | `sidecars/root-complete-demonstration-sft-v1`; READYc9fc3194…/RECIPE50015b9d…/DATA_READY6590fbac…. Same16authored actions, actual c32 capture, action-only versus added0.1terminal loss; fresh4Adam per arm, unchanged plus2fixed4arms48new-panel readouts.3600outer, checkpoints every complete update.2533unique source/input hashes and actual launch verify pass. No outputs or launch acceptance created. Launch only after new-node checks in the handoff. |
| COMPLETE: first evidence-catalog slice and local replay audit | `analyses/research-factory-2026-09-09`:9sealed reports,8questions,13claims,6decisions,3publication candidates. Local replay REPORT6db99a0a…/FINALa9ae9fa1… sealed separately after catalog cutoff. |
| CPU PENDING: two bridge variant outcome audits | `analyses/root-child-representation-bridge-panel-live-2026-09-09/RESUME_CHECKPOINT.md`.96-slot source-only panel/method frozen; RL4/highLR outcomes remain unread by the independent analyst. No GPU rerun required. |

There is one prepared GPU successor and no accepted waiter. On the new allocation,
rediscover hardware, allocation deadline and node-local runtime; old PID/MIG
ownership is historical, never authority on the new node. Prepare supplied-map
reduction and cross-partition diagnostics alongside SFT, not before launching it.
Those successors are proposed designs, not executable READY jobs yet.

## Newly completed evidence

- Fixed-RL4 bridge32 completed536.035s,exit0/GPUempty. Actual
  COMMAND1788974402.5309718=17:20:02.531,exit1788974938.572261.
  TERMINAL51d4f894…/STATUSfaedaf5f…. Independent outcome audit pending.
  High-rate successor launched about4.54s later automatically.
- [Original bridge32 audit](../../analyses/root-child-representation-bridge-live-2026-09-09/REPORT.md)
  is sealed REPORTb0758413…/FINALada5f372…. Checksum0/8both, count1/8both;
  all32 actual available finals. Checksum has only3/8paired uptake, no eligible
  batch above8. Count uses matched requests; dataset-label agreement567→593/628
  improves but final success does not.744 native calls and354 broker projections
  corroborate. A selected program counts final-batch labels instead of accumulated
  all_labels, then faithfully reports its wrong scalar. No final-copying defect.
- Local cue replay finished all32 units/288candidate forwards,101.745souter,
  exit0/GPUempty, STATUSdd3fa770…. Independent audit sealed REPORT6db99a0a…:
  matching−constant mean correct-label probability+.49684 AG,+.27689 SST.
  Finite candidates/fixed supplied history, not sampled accuracy or attention.
  ActualCOMMAND1788973401.40522,exit1788973503.157261=17:05:03.157.
  Next CPU study was not ready: **899.373711s (14m59.374) avoidable idle scheduling
  gap** before RL4 COMMAND. Preserve this cost; no useful science ran in that gap.
- Shifted72 completed all72 valid calls,276.775s outer,exit0/GPUempty;
  [independent report](../../analyses/leaf-shifted-cue-live-2026-09-09/REPORT.md) is sealed,
  REPORT37bcb4cf…/SEALd6b90fd7…. TREC/SST/AG displayed-position correct
  matching491/484/407, constant230/309/194, shifted115/253/119 of512 each.
  Shifted named-record alignment487/483/415 is a separate diagnostic, never a
  repaired score. On predeclared unequal-gold positions, named375/398 versus
  displayed3/398 TREC;247/264 versus17/264 SST;320/380 versus24/380 AG.
  All12 context means favor matching over each control. Contradictory forced
  cues redirect labels; not hidden attention or free ID retrieval.
- Paired-plan SFT48 finished1258.628s,exit0/GPUempty, TERMINAL39bddba9….
  [Independent audit](../../analyses/root-plan-sft-live-2026-09-09/REPORT.md) sealed,
  REPORT88c7b9d0…/FINAL33371d44…: canonical1/16, filter-first1/16, unchanged4known/15available+1NULL;
  primary0wins0loss16ties. Both trained arms cover all relevant records but
  request all32 query/all128 length records: no learned query filtering.
  Format4/16 and3/16 versus10/16; eleven decimal finals per trained arm are
  invalid, and many numerically wrong too. One unchanged endpoint is a broker
  NULL in sensitivity. All32 trained endpoints graph-clean;4Adam steps/9888
  targets each authenticate. No failed-primary decimal-answer repair.
- [Query failure taxonomy](../../analyses/root-query-failure-taxonomy-2026-09-09/REPORT.md)
  reexamines all32 query trajectories from highLR/RL. Fifteen contain the same
  q0009 frozen-label disagreement;14 correctly reduce and copy that map.
  All19 displayed integer scalars are copied faithfully. Six failures display
  a correct scoped map but never execute its count. This does not demonstrate
  a final-copying bug or broad failure of scope reasoning. Preserve gold;
  no evaluation-item memorization/removal. REPORT6eefa1b9… also adds one
  historical highLR-low broker-NULL sensitivity without changing old scores.
- Bounded-refill RL completed four real updates and all48 before/after readouts,
  exit0,2127.852s, empty GPU at release. [Sealed independent audit](../../analyses/root-bounded-refill-rl-live-2026-09-09/REPORT.md):
  endpoint strict7→11/24,6gains2losses; query0→0/8, validation5→6 and length2→5.
  One pre-update empty terminal has a broker timeout, not a sampled negative;
  availability-safe sensitivity gives5gains2losses16ties1unknown, net[3,4].
  All four windows already had two mixed groups: **neither extra refill nor NOOP
  occurred**. Do not attribute gains to refill. REPORT0fc257ce…,
  FINAL_MANIFESTbe2db699…; all34,116 root tokens/504 Adam states authenticated.
- [Fresh96 independent audit](../../analyses/leaf-fresh-correspondence-live-2026-09-09/REPORT.md) completed both released-model48-call stages,
  exit0,714.285s, TERMINAL0fdd851b… and empty GPU. Actual command16:16:18.023,
  exit16:28:12.315. Same frozen512 records/96requests, no scientific reroll.
  Matching beats constant in all32 seed-pairs/all16 context means, all96 valid.
  Qwen3 AG417vs172/SST468vs301; Qwen3.5 AG425vs211/SST471vs275 of512.
  No whole64-perfect output. Fresh only against25 named historical catalogs;
  SST43short units retained, underlying dataset licenses unresolved.
  REPORT58ae42f0…/FINAL_MANIFEST8234a639…. Successor started2.628s after exit.
- [Larger updates to the same successful-example training](../../analyses/root-success-sft-lr-live-2026-09-09/REPORT.md):
  frozen primary low8/24 to high14/24, nine paired gains and three losses.
  Additive query audit finds one pre-update empty was a broker failure, not a
  sampled negative; availability-safe overall net[5,6], not an all-clean claim.
  Format16→24/24 and relevant returned-label coverage21→24/24.
  Most gain is on longer inputs (1→6/8); new question patterns stay2/8.
  First worked-example copying remains22/24. All eight Adam/checkpoint states
  independently checked. Training589.929s; science1399.086s/outer1399.630s.
  High uses fewer calls overall, but **more** on the five jointly correct cases.
  REPORT42c0f127…/FINAL_MANIFEST3ea749d2….
- [Coverage-summary comparison](../../analyses/root-coverage-first-live-2026-09-09/REPORT.md) completed all48 endpoints; independent raw audit
  reports success-SFT8 map4/8, always_counts2/8, coverage_first5/8; efab2/8,0/8,2/8.
  Coverage versus always has3gains0losses for SFT and2gains0losses for efab.
  Costs rise, including16→20 calls on two jointly correct SFT pairs.
  All352 native calls and125 observation projections reconcile. One completed
  empty reply is strict0, with a broker runtime error; it is not an unavailable
  endpoint and its missing coverage evidence is unknown. The audit is sealed:
  REPORT935be163…/METRICS4e628d1a…/SEALab177567…;13 independent tests pass.
  Parent exits0,780.310s,TERMINAL32e1ef0e….
- [Prior complete-success SFT and separate RL7 readout](../../analyses/root-success-trajectory-sft-live-2026-09-09/REPORT.md):
  baseline5/24, low-SFT8 9/24, RL7 9/24. The newer low8/24 is a different paired
  sampling seed set; do not pool or overwrite the earlier result.
- [Same-record reminder-phase192](../../analyses/reminder-phase-live-2026-09-09/REPORT.md):
  all192 valid; matching-ID advantage is greatest at the reminder and declines
  over the same records at later positions. All12 context means show the
  predeclared decline; not hidden-attention proof.
- [Released-model correspondence144](../../analyses/leaf-qwen35-identity-live-2026-09-09/REPORT.md):
  matching beats constant in all48 model/task/context/seed pairs without our SFT.
  [Sparse field-order plot](../../analyses/leaf-sparse-cue-order-main-review-2026-09-09/REPORT.md)
  shows that moving the ID after a label moves its strongest benefit forward.

## Decisions and ranked follow-ups

1. Finish independent audits of the completed RL and fresh-record comparisons.
   The RL gain is modest and not query transfer; no extra support acquisition
   actually occurred. Fresh records address repeated-source uncertainty, not
   pretraining exposure or comprehensive novelty.
2. Compare explicitly authored query-sensitive plans with a matched general
   classify-everything routine. Distinguish learned filtering from correct output
   syntax, helper uptake, or cheap but wrong answers.
3. Probe source-cue following with deliberately wrong IDs, then test whether
   child representation changes improve whole-RLM count/checksum answers.
   Different outcomes distinguish a component mechanism from root bottlenecks.
4. Independently replicate the stronger SFT update signal or target faithful
   returned-evidence aggregation. Flat query transfer and correct maps followed by
   wrong counts motivate these choices; do not simply raise LR again.
5. Replicate the coverage-summary contrast on more contexts or fixed high-LR
   weights before claiming a generally better harness. Current coverage policy
   restores losses relative to premature counts, with little evidence of gain
   over ordinary maps and higher cost.

The paired-plan LR decision is explicitly **outcome-informed and prospective**:
`ideas/2026-09-09-root-plan-sft-lr-amendment.md` applies1e-4 to both arms before
READY or any training/readout. Starting checkpoint66cce remains unchanged.
The earlier RL approval is not retroactively changed to the high-LR winner.

## Failed launch, ownership and opportunity cost

Fresh96 first command exits1 after4.307s at1788967893.0243394. Reused launcher main
records its old source hash, while lifecycle expects the actual fresh wrapper.
All other binding fields match. Normal release hits the same mismatch. Inference
initialization continues asynchronously after parent exit, so its early empty-GPU
snapshot did not prove lasting release. No scientific client COMMAND/output exists.

MAIN authenticated saved UID/PID4119052/start1077170473/PGID4119052 and released
only that owned group by SIGINT. Separate BEFORE/SIGNAL/AFTER artifacts are in
`operations/2026-09-09-fresh96-orphan-release`. No files or checkpoints were
deleted. The repair preserves strict ownership validation and records the correct
actual wrapper identity; it does not bypass the check.

High-LR→coverage handoff3.302s. Coverage→fresh96 handoff below1s (exact command
timestamp should be taken from COMMAND, not inferred from elapsed).
Fresh96 failure→bounded-RL COMMAND: **556.526s =9m16.5s without useful science**,
including orphan startup/release, review, acceptance and preparation. This is
research-operation loss, not productive training. An oversized tool transfer
also inserted truncation text into a parsed hash string; on-disk artifacts were
unchanged. Full684-file verification and small strict64hex chunks resolved it.
A failed JavaScript orchestration cell made no filesystem changes.

Earlier21m28.6s,9m12s,6m18.1s and other scheduling gaps remain in prior snapshots.
Do not erase them or claim loaded GPU memory as utilization. No cache cleanup,
live relocation, shared-environment mutation, Git commit or push in this segment.

[Plain-language summary](../../analyses/CURRENT_SUMMARY.md) ·
[Promising findings](../../analyses/PROMISING_RESULTS.md) ·
[Analysis index](../../analyses/README.md) ·
[Session checkpoint](../../../../ARTIFACTS.md#unpublished-files "Not published: operations/2026-09-09-continuous-allocation/SESSION.md").

