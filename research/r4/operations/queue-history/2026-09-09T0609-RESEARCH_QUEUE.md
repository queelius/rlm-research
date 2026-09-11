# Live GPU research queue

Updated: 2026-09-09 04:55 UTC. This document records current execution authority,
not every historical status. The complete previous queue is preserved byte-for-byte
in [the 00:36 snapshot](2026-09-09T0036-RESEARCH_QUEUE.md).

## Hardware and immediate priority

Latest state04:55 supersedes the04:43 milestones below: grammar160 and B80 are
COMPLETE, exit0; padding128 is ACTIVE (62 calls at04:55), automatically launched
at04:49:38.1659. The independently seeded root RLVR run is ACCEPTED and its
automatic waiter is LIVE: session49154, PID2265571/start1073347164/PGID2265570,
started04:54:19.0639. It waits for the exact controls coordinator2260395 to exit
and empty GPU/shared lock, then launches one original-step0→8 campaign.

Operation `operations/2026-09-09-after-controls-root-replication/`:
PLAN3bf201019dd5366f914ce2b7b71e5223f2ddd11dd01f58cf1d7bde9fd9cf9e4b;
ACCEPTANCE6cf01b26e1b1756d807ae29bf75cc8c67e5f68df31e83e24a5b25724342d7b28,
171 authenticated paths. Main read all360 new source lines and targeted inherited
seams; fresh3 replication/5 handoff tests and native verify pass. Independent
bounded source review found no material blocker. Fixed seed981265001, original
857a7 root, fixed c32de child, empty initial Adam/no inherited RNG or rollouts,
eight fresh32-episode generations and checkpoints every update.6000s main-entry
exception budget,6030s outer process cap plus ordinary owned cleanup grace;
do not claim every descendant must exit at exactly6000s. Predecessor conservative
deadline1788940402.2401078 includes the complete earlier chain, not waiter start.
No extra run or automatic retry is authorized. Exposed development data and
original-then-selected transfer order remain limitations.

The user asked about storage, not to pause research. Ceph at04:52 reports home
117187404219bytes and project460399312089bytes, about538GiB combined. Each directory
reports its own1099511627776byte (1TiB) quota. Current RLM store is about108GiB;
caches dominate remaining usage. No files, caches or environments were removed.

### Retained04:43 handoff milestones

One exclusively reserved A10040GB full MIG on an21; Slurm5771 ends approximately
2026-09-09 19:07 UTC. Grammar160 now owns the GPU through automatic coordinator
session25734, PID2129741/start_ticks1072915615, actual launch04:35:15.0812. At the
04:41 check,74/160 raw calls were saved, GPU memory33884MiB/power249.85W; MIG
utilization percentage is unavailable. Generation records, not allocation alone,
establish useful work. Root96 completed all96 GPU episodes and service releases,
then main interrupted only its redundant CPU analysis tail to release the shared
scheduling lock. The parent records exit-2, not exit0; raw data remain complete.
The indexed coordinator session93781 is COMPLETE, exit0, no timeout; all624
matched HF readouts have an independent final audit. Root continuation is also
COMPLETE and session32800 exited0.
No old service or waiter below is authorized to relaunch. Root owns launches;
agents prepare CPU-side inputs and analyses.

| Priority | Question / job | State and next action |
|---|---|---|
| Active | Does explicit correspondence work without a grammar, and does training transfer it beyond the training task? | RUNNING: session25734, PID2129741/start_ticks1072915615, actual launch04:35:15. Frozen160 calls, old/indexed-final × anonymous/indexed × free/exact × ten contexts × two seeds. Six exposed TREC contexts; four fresh SST contexts at input freeze, excluded from both earlier studies. Actual fixed-final step204 weights authenticated.30-minute collection/45-minute overall cap. |
| Next 1 | Does the earlier mixed-size-trained helper already capture the new model's transfer performance? | ACCEPTED, AUTOMATIC WAITER LIVE: shared successor session39984, PID2260395/start1073262797, began04:40:15. B80 uses identical parent contexts/seeds/prompt IDs/sampling/schema bytes, different frozen adapter.15-minute collector,1800-second execution stage,1830-second outer cap. Main read sources, fresh6 tests/owned verify passed, independent review found no material blocker. |
| Next 2 | Do meaningful output IDs help beyond equally verbose placeholder structure? | ACCEPTED in the same automatic session39984 after B80.128 calls, old child, four representations × free/exact × eight developmental contexts × two fresh seeds. Main read all sources; fresh8 tests/owned verify passed; independent review found no material blocker.15-minute collector/1800-second owned/1830-second outer cap. Placeholder instruction+26 tokens; no equal-actual-compute or before-label mechanism claim. |
| Next 3, CPU ready | Does the root reward-training gain repeat from the original weights with a genuinely new training seed? | CPU READY, NOT ACCEPTED OR LAUNCHED. Independent step0→8, seed981265001, empty Adam/no inherited RNG or rollouts; fixed c32de child and same exposed task compositions.256 new training episodes,40 validation captures,48 paired transfer captures; checkpoint every update.6000-second inclusive cap. Main read360 new source lines; fresh3 tests PASS. Independent bounded review and automatic operation preparation in progress. |

The automatic root→anchor→indexed-SFT handoff is COMPLETE, started02:21:10 UTC:
session93781, PID1988752, start_ticks1072428288. It observed the exact root parent
exit at02:44:35, launched the anchor at02:44:36, and launched indexed SFT at02:48:22
after successful service cleanup and an empty GPU process listing. The indexed
job finished at approximately04:10:43, exit0/no timeout,4941.115 seconds including
load/train/checkpoints/validation/readouts. GPU processes were empty at exit. Operation:
`operations/2026-09-09-queued-successors/attempt-001`.
Parent acceptance SHA8e1c683129dd427b11101e8c2b5cc728b748e2f43222a5258a3bca60f0ffbbd7
binds the reviewed plan, exact commands and23 source/input identities. It waits
for GPU release, uses the qualified owned lifecycle, and preserves failures without
retries. The anchor has a30-minute collection cap (40-minute outer envelope);
SFT has60-minute optimization and90-minute overall caps. Do not launch either
successor manually or create duplicate attempts. A queued job is not yet a result.

The root→grammar operations were independently accepted and automatically chained:

- `operations/2026-09-09-after-indexed-followups/attempt-001` waits for
  PID1988752/start_ticks1072428288. Acceptance SHA
  `0fa26a734041c350562a8fdccc39d2759671c505204d0892fc784ffeeb9668ae`
  binds204 source/input paths and only root96. It observed predecessor exit at
  04:10:47.28 and launched04:10:48.2017. Main read all new source;
  eight sidecar tests and three loader tests passed. The current SFT predecessor
  deadline is1788927532.2401078, plus120 seconds exit grace.
- `operations/2026-09-09-after-root-contract-grammar/attempt-001` waits for
  PID2120762/start_ticks1072822471. Acceptance SHA
  `842182b9b31f2009ae49dd99eb6ceb75869c58069fa72709e8e5c8c5a2a00169`
  binds95 source/input paths and only grammar160. Main read the remaining
  operation sources, freshly passed three loader tests, and authenticated the
  exact final weight/source closure. Eight sidecar/wrapper tests previously
  passed. Indexed adapter SHA starts7a18736d; no outcome-based selection occurred.
  Its predecessor deadline1788932092.2401078 includes upstream waits and the
  complete root96 envelope, rather than timing from waiter startup.

Both use the existing shared lock and owned service lifecycle. They never signal
their predecessor or retry failed runs. Root96 is not gated on indexed evaluation
success; grammar160 has its own authenticated fixed-final weights. Do not duplicate
either job. The original source attempts and all failed outcomes remain intact.

New accepted control operation: `operations/2026-09-09-after-grammar-followups/`,
session39984, PID2260395/start1073262797/PGID2260394. PLAN SHA
568cc0c0b47b025bf3347cc1ad173f7accd0b5b093f386ed89766f0837544319;
ACCEPTANCE SHA94946c7678f167abdeac647f61eac70b1c100762ed0d32a8c88a8497c1a62ace
binds168 source/input paths and only B80 then padding128. Three new loader tests
passed; unchanged coordinator/shared lock. Conservative exact-grammar predecessor
deadline1788935662.2401078 includes all upstream waits/job/cleanup bounds. B uses
operation/B80-owned; padding uses its sidecar/owned/attempt-001. Do not duplicate.

Root96 scheduling recovery: at04:35:09 main sent SIGINT only to exact owned
CPU-only driver2144297/start1073086090 after96 complete raw episodes, both service
releases and empty GPU/no children were checked. Repeated per-episode source
rehashing held the parent lock after GPU release. Collection TERMINAL remains
complete; operation child exit is-2 and built-in ANALYSIS absent. Independent raw
analysis continues outside the GPU schedule under a pre-outcome amendment. The
next grammar job launched about six seconds after the signal. Preserve this as
avoidable CPU-tail idle, not an exit0 job or inference censoring. Exact decision
and action are in operations/2026-09-09-proceed/ROOT96_CPU_TAIL_{DECISION.md,ACTION.json}.

The completed indexed SFT comparison changes the interpretation: mixed-size B
already performs nearly identically on indexed64 (373/384 versus374/384). The
grammar160 contrast cannot by itself establish an indexed-specific training
benefit, so add the B80 control before making that claim. No frozen recipe changes.

The root continuation completed at approximately02:44:30 with FINAL.json and exit0.
On matched transfer coordinates, original root5/24 versus selected step8 root16/24:
13 gains, two losses, nine ties. All48 outcomes were observed/admitted with no
integrity failure, censoring or exclusions. All24 actual initial root prompts and
sampling settings match; the child staysc32de. Four of six context groups improve,
two tie. This is one exploratory training run on root-new but leaf-train-supported
contexts, without a contemporaneous unchanged-policy replay. Dispatch order and
stage timing differ between arms; do not claim a fully counterbalanced replication.

## Newly completed work

- Indexed SFT and all624 matched HF readouts are COMPLETE and independently
  audited.204 actual Adam updates,14 committed checkpoints,118198 target tokens,
 1282.463 optimization seconds; fixed final epoch2. At size64, B indexed373/384
  versus new indexed374/384, both6/6 valid (two gains/one loss). Both anonymous
  formats fail6/6: B returns short arrays, new exhausts3072 tokens. Old free indexed
  outputs select tool mode; those strict zeros are not pure labeling deficits.
  This does not establish a useful extra ID-training benefit. These are six
  exposed TREC contexts, one training seed, not task-transfer or whole-RLM gains.
  See the [completed report and audit](../../analyses/anchor-indexed-followups-live-2026-09-09/REPORT.md).
- A [posthoc first-action screen](../../analyses/root-first-action-screen-2026-09-09/REPORT.md)
  locates part of the root change: valid first tool-call JSON rises13/24→22/24.
  Closed malformed JSON falls10→1; one unfinished length-capped block remains
  in each arm. All48 syntax classifications match runtime structured-call presence.
  Eight of13 final-answer gains occur in pairs changing unusable→usable first
  requests; five gains and both losses occur where both first requests are usable.
  These post-treatment groups do not identify causal mediation. The native setup
  already supplies a first-tool prefix. Raw wire usage also recovers provider cache
  counts for all553 successful calls:190,384→341,856 cached prompt tokens. Input
  minus reported cache is23,719→24,989; this is not measured GPU work or FLOPs.
- The output-ID anchor completed600/600 calls in175.643 collection seconds
  (225.599 including service startup/cleanup). At batch64, TREC correct586/1536
  anonymous versus1437/1536 indexed; new SST correct615/1024 versus986/1024.
  All outputs were valid and every paired context/seed/permutation improved.
  Batch5 remained strong:738/768 versus736/768 TREC;485/512 versus491/512 SST.
  These are repeated observations from six/four context groups, not1536/1024
  independent examples. Output instruction and grammar change together with IDs,
  and actual indexed output tokens are about3.2–3.3 times larger. No RLM or indexed
  training benefit follows from this alone. The independent raw audit reconciles
  all600 scores, wire bodies and qualified physical prompt identities. See the
  [completed anchor report](../../analyses/anchor-indexed-followups-live-2026-09-09/ANCHOR_REPORT.md).
- All8 optimizer updates are authenticated:158 mixed-group training episodes,
  362 root turns,108,461 credited root tokens,297.324 optimizerseconds. Validation8
  reaches4/8 (three gains/one loss versus initial), and the frozen rule selects
  step8, whose adapter SHA is473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd.
  All8 validation terminal outputs are valid. Val8 uses108,184 input/9,676 completion
  tokens,117 calls and131.762 rollout seconds. Completed transfer improves5/24→16/24
  as qualified above. Its rollout times are389.392→210.424 seconds, but successful
  child calls increase97→352; wall time alone is not logical-call efficiency.
  See the [root training report](../../analyses/root-continuation-live-2026-09-09/REPORT.md).
- Updates5/6 add10,168/11,660 credited root tokens; the six-update total is85,791.
  Actual Adam4→5→6 and unchanged child/observation masks were checked. Validation6
  is2/8, one regression and seven ties versus validation4. All8 outcomes are
  observed/admitted;7/8 terminal outputs valid. Costs rose descriptively to109,564
  input and10,444 completion tokens,103 model calls and112.904 rollout seconds.
  The repeated eight-coordinate set is not new held-out evidence. See the
  [completed milestone report](../../analyses/root-continuation-live-2026-09-09/REPORT.md).
- Continuation update4 is committed:19 mixed-group episodes,44 root turns,
  15,343 root-action tokens,35.610 optimizerseconds; no child/observation credit.
  Validation4 is3/8, equal to validation2 with one gain and one loss. The same
  eight coordinates come from only two source contexts; this is not established
  learning beyond the observed unchanged-policy replay variability.
- Original-weight scope72 completed and was audited:111/512 all64,
  105/512 full16,192/512 planned local16 (192/480 aligned,30/32 valid).
  The two invalid responses exhausted1024 tokens after15 labels and whitespace.
  All72 physical prompts match the trained-child comparison. Selection failure
  predates child SFT; SFT improves all three conditions in this exposed sample.

- Root campaign V2 STOPPED after3 committed updates, not8. Total48620 credited
  root tokens and126.114 optimizerseconds. Validation00=2/8, validation02=3/8;
  no step3 validation. Round04 stop was an authenticated child context-overflow
  incorrectly classified as fatal identity corruption, not an established
  weight/alias/mask mismatch. Original STOP and all checkpoints stay unchanged.
  See [terminal report](../../analyses/root-campaign-complete-2026-09-09/REPORT.md) and
  [actual RLVR harness audit](../../analyses/actual-rlvr-harness-review-2026-09-09/REPORT.md).
- Mixed-size SFT A/B COMPLETE:206/204 updates,1151.455/1142.028 trainingseconds,
  short-batch test477/489 and476/489. Neither produced usable64-label arrays on
  the six fixed final probes. A truncated5/6; B truncated0/6 but returned short
  arrays. Training changed the failure shape without solving the large output.
- Leaf post-SFT suite COMPLETE600 calls. Fresh supervised sentiment transfer
  retains strong five-item performance but schema64 still deteriorates by
  position. Original/old/A/B schema64 correct318/308/326/324 of512 assignments,
  all8 arrays valid per condition. Repeated seeds on256 source questions are
  not512 independent test questions.
- Correspondence representation control: old child anonymous181/512,
  indexed405/512, echo419/512; each8/8 valid. Echo copies511/512 records exactly.
  This changes the output representation and does not prove an attention mechanism.
  Rotation retains early-position strength under changed question ordering.
- B template replay COMPLETE12 calls: both exact probe-template and
  training-template arms0/6 usable arrays, no truncation. Matching the training
  serialization did not rescue cardinality on these six contexts.
- Scope72 COMPLETE: all64/full16/local16 correct145/153/348 of512.
  Unchanged72-call replay COMPLETE:143/153/349. All arrays valid. Four reused
  validation contexts and256 distinct questions; no independent new-data
  confirmation. Later full16 outputs match first-visible gold more often than
  requested-target gold (posthoc176/384 versus71/384), suggesting ignored IDs.
  The raw CPU token-hash mismatch is confined to vLLM tool-key serialization;
  full system/user text and live physical inputs were retained.
- MRCR computed commitment V1 failed before inference on all6 cases due to a
  missing endpoint URL field. EndpointV2 COMPLETE operationally:12 native calls,
  six model non-submissions, no commit/restatement pairs. Do not score this as
  evidence for or against exact commitment. All six cells parse as valid Python
  and have successful cell status, but none calls submit_text. Three blank
  observations correspond to bare expressions inside if/else blocks; the other
  three return intact print/display output. No transport defect is established.

## Readable evidence and decisions

September 9, approximately04:10 update: [the most promising findings](../../analyses/PROMISING_RESULTS.md)
keeps the output-ID and root-training results as the leading research signals.
The [nearest-prior-work review](../../analyses/publication-positioning-2026-09-09/REVIEW.md)
finds that numbered outputs, RLM reward training and generic harness–weight
co-adaptation are already established. The narrower candidate contribution is
measuring when local task competence survives the helper/program/final boundary,
and whether targeted interface/training changes generalize.

The [official-runtime comparison](../../ideas/2026-09-09-official-runtime-comparison.md)
reuses current author RLM and Lambda-RLM clones and adds a pinned current nano-RLM
source snapshot. No active runtime upgrade, package installation or GPU call was
made for acquisition. Record-bound returns, visible coverage diagnostics and
first-action syntax controls are proposed experiments, not claimed new inventions.
The padding control is the one new CPU-preparation task. Root96's independent
analysis method was frozen before its new outcomes, and leaf_sft_prepare continues
the existing matched-SFT audit. Do not change any currently accepted comparison.

Start with the [research dossier](../../analyses/cross-experiment-synthesis-2026-09-09/README.md).
It separates a plain-language overview, findings, experiment catalog, limitations,
ranked research questions, bounded next experiments, and sources. Its machine-readable
claims and candidate queue are analysis inputs, not automatic launch authority.

Latest controls are audited in
[post-SFT controls](../../analyses/post-sft-controls-2026-09-09/REPORT.md):816 HTTP calls
plus12 HF calls, with all raw scores and captured input paths reconciled.
Core Responses-harness fixes are committed in an isolated worktree:
`/project/alex_phd/repos/rlm/.worktrees/core-evidence-fidelity-20260909`.
They preserve executor truncation evidence and account for valid late-response
usage without accepting late answers. These are separate from the frozen Prime/nano
experimental runtime; no silent patching of completed runs.
Commit:bb2d6da11b5a97f8e27e449d095b6fa7c1bcdbd4. Branch and worktree retained;
no merge or push. Parent fresh read-only dossier verification at02:14:46 passed:
55 local source hashes,62 total sources,24 claims and205 local links, plus bounded
numerical checks. Repository entry point: `docs/RESEARCH_RESULTS.md`.

The completed [process-consistency screen](../../analyses/process-consistency-screen-2026-09-09/REPORT.md)
does not justify a reward change. Complete maps are observable in27/64 development
and16/48 exposed readout episodes. All25/6 complete-map strict successes have correct
target membership, so auditable target-cancellation sensitivity has no denominator.
Extra queries reject14/24 and3/4 successes with errors about OTHER classes: that
tests stronger map reuse, not invalidity of the task originally answered. Efficient
target-specific strategies need not emit a full six-way map. Parent independently
recomputed these aggregate counts. Missing maps remain unresolved, not wrong.

The [single-case follow-up](../../analyses/root-consumption-example-2026-09-09/REPORT.md)
is complete. Thirteen child returns correctly identify14 humans (61/64 overall
labels correct). The root's program extends a list with each raw answer string,
adding characters rather than decoded labels, and counts0. The root model sees
only that computed0 and faithfully submits it. This is supported consumer/type
misuse, not demonstrated transport loss or direct disregard of visible labels.
The case suggests the return-type instruction ablation above, not automatic
full-state replay. One posthoc example does not estimate an effect or prevalence.

Current primary literature and the acquired, unexecuted official WHALE clone are
documented in [the literature update](../../ideas/2026-09-09-harness-weight-literature-update.md).
Generic model–harness alternation is already prior work; the ranked proposals
focus on correspondence, interface robustness and faithful evidence use.

## Operational accounting

Completed coordinators:39335(rootV2),56459(postSFTsuite),44507(template+MRCRV1),
87657(scope first attempt),36215(scope replay+MRCRV2),27490(original scope),
32800(root continuation). Their sessions and historical
PIDs are NOT live launch authority.

The gap after V1 release01:11:40 until scope launch01:19:10 was approximately
7m30 of avoidable scheduling/setup loss, before further service startup.
After scope-replay/MRCRV2 completion01:28:13.633, the original-scope operation
started01:38:04.029:9m50.396 of scheduling/preparation gap. After original-scope
completion01:39:25.719, continuation started01:47:40.031:8m14.312 more before
model loading. These gaps exclude subsequent startup work and are not exact
low-level GPU idle samples, but they are real avoidable operational opportunity cost.
Do not call loaded-but-unused or empty-GPU intervals useful inference.
The original approximately17-minute gap23:16:36–23:33:36 is retained in the archive.

Preserve all raw outputs, setup failures and incomplete outcomes. New variants
need additive namespaces, frozen input/source identities, question, metric, seed,
compute cap and checkpoints. No meaningless utilization filler.
