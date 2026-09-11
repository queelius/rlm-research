# Live single-A100 research handoff

Updated 2026-09-09 00:36 UTC. The user is AFK and requests continued autonomous
research, not blocking questions. This is not an instruction to stop at this file.

## Allocation and scope

- an21, Slurm5771, GPU MIG-43a3375a-1942-592d-accf-d0884164dcb8, one A10040GB.
- Current allocation end epoch1788980837, approximately September9 19:07UTC.
- Repo /project/alex_phd/repos/rlm; research store /project/alex_phd/runs/rlm-research-r4.
- Existing root repo main is ahead5 and clean; no push requested this turn.
- Home and project each report separate1TiB Ceph quota. Last usage home109GiB,
  project414GiB. Home migration is explicitly deferred; no home files moved/deleted.
- Honor GPU-first AGENTS.md and docs/RESEARCH_OPERATIONS.md. Prepare two followons.

## Current GPU ownership

**00:36 authoritative status:** A/B COMPLETE. A206steps/1151.455trainingseconds,
fixed5 477/489; B204steps/1142.028seconds,fixed5 476/489; both98/98 valid small arrays.
Final64 A0/6 valid/5truncated; B0/6valid/0truncated, closed canonical arrays short
62/58/62/57/62/58. Neither gives usable64-item output. New report and hashed
post-hoc diagnostic at`analyses/mixed-size-prefix-diagnostic/REPORT.md`.
Never resume these completed SFT attempts. B final adapter SHA59ad854293142161f6b5e613dd5d1e3630fed600637106d5eae2cbcd764e9200.

Campaign V2 is RUNNING in live session39335 (operational parentPID1643395). Source
`operations/2026-09-09-succession/B_to_root_campaign.py` binds B parent1629704 /
start_ticks1071458275, waits for exit and empty GPU, then invokes native Python
on`root-rlvr-campaign-v1/campaign_lifecycle_v2.py run --output .../outputs/attempt-v2-001`.
It launched automatically00:25:36, RUN00:25:39, deadline04:25:39 UTC. DO NOT manually
launch that campaign while the waiter is live. It does not depend on B weights/success.
Parent freshly verified V2 in session53956 EXIT0;8 fresh
32-rollout rounds maximum, persistentAdam, original root, fixed c32de child,4hcap.
V2 handles actual PRL::Inference process titles and owned worker shutdown; unused
V1 remains sealed but is not the launch target. All stage checkpoints retained.
At00:36 validation00 is complete2/8 and round01 export12/32,0null,7mixed groups,
28selected episodes/63root turns/23130credited tokens. First optimizer pending.
Service PIDs rotate each step; only campaign should start/stop its current workers.

After campaign: warm two-service suite of correspondence56/SST-2 480/mixed-SFT
schema control64 is READY and AUTOMATICALLY QUEUED via session56459,
`operations/2026-09-09-succession/after_root_campaign.py`. Binds predecessor1643395 /
start1071664442 and empty GPU; suite`.../leaf-post-sft-suite-v1/outputs/attempt-001`,
2hcap. All subjobs READY; optional64 is frozen at suite start. Parent read full
suite source and fresh CPU verify31491 EXIT0. Do not manually launch a duplicate.
current_literature now prepares B-only HF template replay12/15mincap, exact same
six64contexts and model, saved training-template vs frozen-probe physical IDs.
leaf_sft_prepare analyzes first2rootupdates/validation2 or STOP, watcher80837;
snapshots under`analyses/root-campaign-live-2026-09-09`.
storage_audit prepares6 paired computed-string vs final-restatement MRCR branches,
20mincap, additive rootless nano overlay. Existing core FINAL_TEXT already has
direct-commit semantics; do not call that a new core API. No worker GPU authority.

Root-only pilot training COMPLETED1step,23.866seconds, checkpoint
00ad756b609950f3873ae8c3e49ea917be1b207a369d1be7f95933eda78110c9.
Post validation8 COMPLETED2/8, versus initial2/8 and unchanged replay4/8.
The actual updated-root/unchanged-child service1609904 was stopped23:34 after
client37483 EXIT0; worker1610040 and parent bothgone, GPUempty beforeA launched.
NO old inference endpoint is live. Matched-semantic HF/vLLM six64-item probes
both0/6 valid; token IDs differ due tool JSON key order, so not pure backend causality.

Batch audit SEALED at analyses/leaf-batch-shape-2026-09-08,7056 requests,7386files,
seal578c5f18... . Rootpilot three-way audit also complete (2/8,4/8,2/8); all physical
first-root inputs match but unchanged action replay matches only2/8. No validated
learning gain from the one-step pilot. Current agent tasks are listed above.
Record17-minute approximately23:16:36–23:34 loaded-but-unused gap as scheduling
loss, not GPU work. Prefer continuous campaign coordinator after A/B finish.

All entries below are historical; consult the top live RESEARCH_QUEUE.md as well.

**23:02 authoritative override:** all inference clients finished; group1472413 and
worker1472547 were stopped/released before GPU root training launched, session21913.
`root-only-credit-v1/training/attempt-001` is the sole GPU job. One full-batch TIS
update,16 episodes/30 root turns/10500 action tokens, LR5e-5,cap2,600seconds;
checkpoint immediately after actual step. No result yet. CPU real-data preflight
passed, group SHA893b46a86b9478c9630bca162a6ea03734e7cf6849b57415392e1ba9fd65550e.
After it exits, run READY matched HF greedy6 via leaf-mixed-size-sft-v1/probe.py hf,
then authenticate trainer RESULT with root-credit-validation-replay-v1/post_replay.py,
reload existing dual serve.py using POST_BOUND_WEIGHTS and perform post validation8.
RUNBOOK_POST.md has exact commands. Old service endpoints are not live.

Root40 COMPLETE:9/32 training,2/8 validation,2 excluded training infrastructure
failures. Four mixed groups provide16 selected episodes; export retains all40.
Unchanged-weight validation replay COMPLETE4/8, versus initial2/8. Avoid claiming
similarly sized post-update deltas as demonstrated learning. Long recursive tails
cost970.5seconds for40 and746.4seconds for replay8; allrecorded, no outer censoring.

Batch1/64 and exact-cardinality schema followups are allcomplete. Schema restores
all array contracts; trainedsingleton strict16/24, trained64 still0/24. At64,first16
labels97.4%correct butlast16 only21.1%, with366/384 predictionsentity. Input64 fully
present, only1321–1361tokens, nottruncated. Varied-batch fullSFT A(max32)/B(max64)
preparing byleaf_sft_prepare, same5065groups/twoepochs/fixedfinalepoch2. Matched
vLLMgreedy6alreadyfinished0validarrays; HFcounterpart readyforreleasedGPU.

storage_audit implements an approved independent8-round fresh-rollout root-only
campaign in newroot-rlvr-campaign-v1 (noGPUduringprep),4-hour cap,persistentAdam,
fixedc32dechild, separatefrompilot. current_literature sealsbatchpositionaudit.
No source repository changes/push. Live RESEARCH_QUEUE.md has allnewqueueitems.

Everything below is historical, including the23:02-preceding live-client statements.

**22:39 authoritative override:** service PID/PGID1472413 is still alive on18601.
Three clients currently use it: root-only native40 session58643 (started22:34),
fixed64-item arrays session2094 (22:37), fixedsingleton3072 session26298 (22:38).
See live RESEARCH_QUEUE.md for exact paths/spec hashes. Do not stop until all finish.

Root-only capture has real native root-child-root CPU qualification and frozen40
coordinates (32training,8validation). Source-training questions were intentionally
seen by the selected child SFT but are disjoint from leaf-validation/test and the
new-composition384 source groups. Export via root-only-credit-v1/root_export.py only
after collection ends. Child tokens are evidence/context, never targets. Trainer
being prepared by leaf_sft_prepare with frozen TRAINING_RECIPE.json: one full-batch
TIS step, LR5e-5, cap2, seed981260500,600seconds. Use actual mixed groups only.
After all clients finish: export, verify narrow trainer critical path, stop owned
service, run GPU update, reload root checkpoint plus same child and replay validation.

Role12 and composition48 are COMPLETE:2/6 ->2/6 and4/24 ->6/24. Identical first-root
requests nevertheless yield different first actions in3/6 and15/24 pairs before
any child; this is not child-mediated and weakens causal interpretation of tiny
full-RLM deltas. Fixed five-item batching624 gives1/24 ->15/24; fixed16-item192
gives4/24 ->15/24 with much lower logical input use. Learned leaf skills help a
supplied reliable routine substantially more clearly than the current free root.

Native direct MRCR6 completed after an additive /models typed-dict SDK fix; all six
outputs are byte-identical to prior Chatdirect6, exact2/6. Preserve failed attempt.
SFT semantic audit separates strict355->473 from itemcanonical374->473 on489;
strict gains are not purely semantic. Full SFT is128 actual updates, not a smoke run.

Agents: current_literature joint audit; storage_audit nativeMRCR audit;
leaf_sft_prepare root trainer. All source changes and artifacts remain external;
rootGit has not been edited this turn. GPU idle gaps between short jobs and readiness
are real opportunity cost; loaded serving memory must not be called useful work.

Everything below this override is historical, including stale live-client labels.

**22:10 latest override:** SFT session14102 EXIT0, all128 steps complete. Test
355/489 ->473/489 (strict whole-array validity), selectionepoch2 uses validation
250/300 vs245/300. Selected checkpoint-0128 SHA
c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3.
Actual training705.625sec; full workflow included baseline/validation/test GPU calls.

GPU now owned by dual-LoRA service PID/PGID1472413, port18601. Run-dir
`sidecars/leaf-role-routing-v1/service-attempt-001`. The actual serving config uses
lora_dtype=auto (BF16cast),max_loras2,max_cpu_loras2; a draft READY mentionedfloat32
but actual config/startup are authoritative. Source/serve.py launch hash84c2375362...
Full endpoint-original.json and endpoint-selected.json identify actual loaded aliases.
Original is the exact key-converted adapter SHA857a7ce6..., not broadcast-fileSHAe5be32...
SFT training required that exact conversion;504FP32 tensors independently matched.

Active clients: development role12 session56260; new-composition48 session9977.
Both started after SERVER_READY22:06:59. Do not stop service while either runs.
Next ready nativeMRCRdirect6 needs additive converted-adapter identity amendment
by storage_audit. Fixed624 leaf-composition control preparing by current_literature.
leaf_sft_prepare is now doing completed SFT reproducibility/paired semantic analysis,
not changing any live/frozen role code. All source/weights/specs remain external toGit.

Newcomposition prepared data identitybc1e2ba2d0121c0243b68b1286e44a94f02cf7a81b73b4a091fb294d1b36302f;
fullrun SPECsha5faba7d386f71166f3ab7c1b4dec5cff8d989fac63ac71112b0f3fec656aa548.
6disjoint64-record contexts from384 component-test questions; HUM/NUMcountqueries,
2seeds×2childweights×12tasks. Root prompt is supplied example, not learned planning.

Priority after these: root-only native RLVR capture with fixed trained child and
new training contexts. This needs explicit role-aware exact-token export and root
gradient credit, not merely filtering old mixed aliases through the old exporter.

Everything after this paragraph is historical; this22:10 override is authoritative.

**CURRENT OVERRIDE:** full supervised leaf SFT is RUNNING, tool session14102,
launched21:45:19UTC. Attempt `sidecars/trec-leaf-sft-v1/outputs/attempt-001`.
The coordinator owns baseline evaluation, two epochs/128 optimizer steps, per-epoch
validation, validation-only checkpoint selection, and paired test evaluation. One
A100, BF16 original4B base + exact FP32 LoRA. Recipe and prepared data are frozen;
READY.json and IMPLEMENTATION_REPORT.md give explicit resume and provenance.
Checkpoints every16 steps include optimizer/RNG/cursor. 60minutes is accumulated
training time; evaluation/checkpoint overhead is additional. Do not start inference
while this process owns the device.

All inference jobs are complete. The last original4B service group1430616 was stopped
after definitions12 completed. Prior8B group1417571 and4B group1313187 are also stopped.
Their endpoint files are historical evidence, not live services.

Next jobs: original-root/selected-SFT-child role-isolated comparison, then explicit
result-submission versus retranscription in MRCR. Both need CPU preparation while
SFT runs. The selected child adapter must come from frozen SELECTION.json, not a
test-outcome-driven choice. Inspect actual forwarded model/contract metadata.

Newest completed evidence:

- 8B36 total episodes:12calibration +24training, no reward variation within any of
  nine4-seed groups; no optimizer. Root has identical two actions; sole repeated
  error is worker owner/actor classification. Audit in single-gpu-rlvr-8b-v3/analyses.
- Leaf72 then clean-validation720: clearer definitions and canonical schema improve
  classification but leave major headroom. Validation canonical baseline183/900,
  definitions388/900, schema343/900, both410/900;300 unique groups,60 shared batches,
  3seeds. Validation HUM group/organization subtype dominates and is often mislabeled
  entity, so do not call this generic reasoning ability.
- MRCR rootless12 exact0/6 both arms; direct6 exact2/6. Six short cached documents,
  different client paths; whole-harness exploratory comparison only. Native raw
  input/output0 fields were wrong; additive audited logical totals41278/8368.
- Full-RLM definitions12 completed in254.57sec with all12 recorded; analysis pending.

Active agents: current_literature audits definitions/validation; storage_audit audits
paired directMRCR; leaf_sft_review does bounded read-only training correctness review.
leaf_sft_prepare completed CPU data/trainer with16focused tests and all2184 rendered
arrays checked, max891tokens. Initial independent reviewer found no launch blocker.

The rest of this document is historical state only; this override and the live queue
take precedence over every older running/ready label below.

Historical next jobs were frozen4B `trec-leaf-contract-probe-v1`72 calls and rootless MRCR
`mrcr-rootless-document-baseline-v2`12 episodes. Both require actual reloaded original
step0 alias, NOT the old stopped endpoint alone. See their README/RUNBOOK commands.

Latest4B findings: original/SFT/RLVR primary scores are all2/14, every paired outcome
unchanged. All three hint56 and example12 are done; literature agent is sealing the
last original-example comparison. NativeTrain recursion attempt002 is complete12/12:
9 recursive episodes,132 child calls+returns,159 sampled turns/12423 action tokens.
Mixed group's only positive contradicts its Python aggregate. Full process audit:
`sidecars/recursive-train-capture-v1/analyses/attempt-002/REPORT.md`.

The following ownership and immediate-queue details describe20:30 historical state,
not current work. Preserve them for provenance; current override above takes precedence.

The RLVR4B inference service is owned by PID1313187, process group1313187.
Port18601, backend18621, RPC18611. Alias strict-rlm-qwen3-4b-rlvr-final.
Service files: operations/2026-09-08-resume/inference-rlvr-tis-attempt-001.
Use its endpoint.json with every new evaluator; it records the actual adapter hash.
Its launch tool session59405 has completed readiness; the service remains detached.

Active CPU clients using that GPU:

- Heldout-after-RLVR16: tool session13615, strict-rlm-client-qualification-v2/
  outputs/heldout-after-rlvr-attempt-001.
- Agent current_literature is preparing hint56/example12 RLVR specs now. Check
  live process/agent handoffs before launching duplicates.
- All three self-SFT evaluation jobs are complete; its service was stopped.

Stop only this owned service after clients finish, using launch_4b_service.py stop
with its run-dir. Verify process/GPU release before training. Never stop all containers.

## Completed current evidence

- Baseline/native client qualification48+48: training-client Python0/24 ->16/24
  after native prompt correction, without weight changes. Eval totals18/24 both.
- Fresh4B training40:6 terminal successes, all40 aligned/trainable captures.
  Four mixed groups give16 episodes/32 model turns/6454 action tokens.
- Heldout-before16: primary2/14 correct excluding known revealing task12000052;
  all16secondary3/16. Previously inspected contexts, exploratory not confirmation.
- Hint baseline56: development minimal6/14 versus procedure1/14, procedure4.61x
  output tokens, no actual recursion. Source-heldout separately report-only.
- First4B RLVR attempt stopped BEFORE optimizer.step: sparse serving/training
  logprob discrepancy. See rlvr4b-attempt001.log and two precision/tail probes.
  Mean|delta|0.00747, max1.0103,71/6454 ratios outside[.8,1.2], samplek3 .000975.
  Switching lm_head precision did not remove the discrepancy.
- Original Prime adapter keys do not match PEFT and original LoRA tensors areFP32.
  Exact additive conversion with all504 CPU tensors verified lives in
  single-gpu-self-sft-control-v1/inputs/step0-peft-key-conversion-v2.
  Conversion SHA857a7ce6...; use autocast_adapter_dtype=True to preserve tensors.
- Self-SFT completed6 actual steps on6 positives/2863 action tokens,17.65seconds,
  peak9.99GB allocated. All six checkpoints plus optimizer/RNG/cursor preserved in
  single-gpu-self-sft-control-v1/outputs/attempt-001/training.
  Final checkpoint-0006 SHA0c08ef740d20c0c4928ee84996a4543494afb79536eb67d8c7224d4ee0712175.
- SFT primary heldout2/14->2/14, all14 exact-outcome ties. Secondary3/16->4/16 only
  gains on the revealing task. Hint56 development minimal6/14->3/14, procedure
  1/14->4/14; mixed changes, not uniform capability improvement.
- SFT executable-example12: abstract4/6 correct,0/6 actual recursion; example5/6
  correct,3/6 actual recursion,64 committed child calls+returns. Error-responsive
  batching is observed, but child labels can be wrong; correct aggregate is insufficient.
- TIS RLVR COMPLETED one actual update. Gradient norm0.0978214, parameter delta
  L2 .0147117,16 episodes/32turns/6454actions, all distribution guards pass,
  zero cap2 clipping. Checkpoint: single-gpu-rlvr-v2/outputs/
  4b-native-tis-v3-attempt-001/checkpoint-1, adapter SHA
  41dae0891793c4218a304230aec4aae1e78bcc9bee31ac10c477099f17374a58.

## Immediate queue

1. Finish RLVR heldout16 and launch/replay identical hint56 plus example12.
2. Execute frozen step0 example12 for weight control. PLANNED descriptor:
   operations/2026-09-08-resume/frozen-replay-planned/endpoint.json; alias
   strict-rlm-qwen3-4b-frozen-replay must actually be loaded/verified first.
   Spec recursive-call-example-v1/FROZEN_REPLAY_SPEC.json. Evidence agent owns
   handoff. Do not change adapters while current clients still request another.
3. Run READY8B sidecar single-gpu-rlvr-8b-v3/source/run_8b.py run --attempt
   single-gpu-rlvr-8b-v3/outputs/attempt-001 --gpu ACTUAL_MIG --port19472.
   It owns sequential inference/training/post phases with a90min cap; original
   v2 attempt remains unused. See its README for absolute launch command.
4. Expand to fresh contexts and MRCR using existing cache/rootless boundary,
   counterfactual shortcut tests, and further learning driven by actual results.

The current six successful4B programs use weak keyword/default classifiers;
correct outcomes do not prove correct intermediate interpretation. Do not change
the declared SFT admission retrospectively. Analyze and test this mechanism.

Detailed notes: RESEARCH_QUEUE.md, DECISIONS.md, ideas/2026-09-08-*-reassessment.md,
and ideas/2026-09-08-findings-and-followups.md. Agents current_literature,
evidence_reassessment, and storage_audit are active and have independent CPU tasks.
