# Live GPU research queue

Updated September 11, 2026, at 00:10 UTC. MAIN owns GPU launch and cleanup.

## Current state: 00:10 UTC

This section supersedes all historical live overrides below.

- RUNNING: lower-update-size reward training, attempt002. Exact coordinator
  117240/start927292184, operation `2026-09-10-after-qwen8b144-lr1e5-attempt002`.
  Actual launch00:02:36.673; cap15000 seconds includes final72 evaluation.
- QUEUED: matching-key whole-task bridge. Coordinator135275/start927370748,
  operation `2026-09-11-after-lr1e5-downstream-bridge120`. Only READY_V3
  (18505cc5), owner_v2.py, attempt002. 24 released-base helper acquisitions
  plus96 main-model episodes, cap2400. Three encodings, two queries, supplied/free
  plan, eight fixed inputs. Primary arbitrary-tags minus untagged; ordinary row
  numbers are the second control. Prospective method and explicit amendments sealed.
- PREPARING: balanced tag-set matching control, audit_field_order. This is the
  second successor, not a filler run; it asks whether the tags must literally match.
- COMPLETE: Qwen3-8B144, all available and valid. Later-label accuracy untagged31.5%,
  numbered85.5%, arbitrary81.1%; both gains positive16/16 inputs. Same16 inputs as4B
  and same model family, not a pure size comparison or a new-input replication.
- PARTIAL READOUT, TRAINING COMPLETE: new-corpus SFT6. All six updates/checkpoints,
  70/72 authenticated endpoints, two attempted timeouts. Faithful-and-correct55/72
  (bounds55–57) versus original-corpus50 and already-trained start12 (17unknown).
  Two separately captured training corpora, one shared exposed evaluation panel.
  Sealed report's incorrect released-start language has an additive erratum.
- MEETING: updating the13-slide package and teaching guide with these two
  replication checks; newPDF not yet built. Target evidence cutoff00:15.
- GPU transitions: SFT→8B2.227seconds;8B→RL2.740seconds. The old waiting LR
  coordinator was canceled before launch, never the active GPU job.

Resume: `operations/2026-09-09-allocation-5780/SESSION_20260911_0010.md`.

## Live override: 23:49 UTC

SFT V2 has saved all six checkpoints and entered metadata72 evaluation at23:43.
At23:48,30 episode receipts and138 native response receipts existed; no outcome
scores have been adopted. The LR attempt002 coordinator remains queued exactly
as described below. Neither GPU owner has been interrupted.

Two short, meeting-relevant jobs are being prepared. If ready in time, MAIN may
reschedule the still-waiting LR coordinator behind them without changing its
scientific inputs or interrupting active GPU work:

- Cross-model matching-key check: released Qwen3-8B, exact same16 stable-panel
  inputs, three references and three arms (untagged, sequential, arbitrary),144
  new calls, cap2400. Same model family, not a pure capacity or fresh-input test.
  question_cards is correcting inherited collector bindings before READY;
  audit_host_join has frozen the prospective method.
- Whole-task bridge V2: MAIN found V1's sequential-versus-arbitrary comparison
  omitted the untagged baseline and selected the TREC-trained c32 helper instead
  of the released base helper from the original matching-key result. Preserve
  V1 unlaunched. V2 adds the untagged arm and uses the released base alias for
  leaf calls with the unchanged QS6 main model;24 leaf acquisitions +96 root
  episodes, cap2400. Keep the exact8 inputs, questions, metadata and generation
  seeds. Confirm actual base-alias support and a nonempty root collector path.
  This is an explicit pre-output design revision for decision relevance, not a
  post-result rescue. audit_field_order is preparing it.

Queued idea, not READY: `ideas/2026-09-10-do-the-tags-have-to-match.md` proposes
a balanced tag-set comparison to distinguish literal matching from extra input
and output structure. Do not let this idea delay the two short comparisons.

## Live override: 23:34 UTC

This section supersedes historical active-job labels below.

- RUNNING: new-corpus SFT completion V2. Operation
  `2026-09-10-new-corpus-completion-v2`, PTY98600; coordinator74992,
  start_ticks927148078, PGID74991, UID1523821556. Actual launch23:28:55.575;
  cap3000 seconds includes six full-corpus updates and fixed metadata72 readout.
  READY704d6f84 / identity074728a0. Training GPU PID75113 at10.7GB and
  checkpoint0001 present at23:33. Reuses all72 captured demonstrations.
- QUEUED: smaller-update reward training, attempt002. Operation
  `2026-09-10-after-sft-completion-v2-lr1e5-attempt002`, PTY25585;
  coordinator76617/start927167898/PGID76616. Waits for whole74992 coordinator,
  including readout. READY6b4921c9 / identity03cd8b1d; exactQS6/freshAdam0,
  fixed192 attempts plus sole-last72; cap15000 starts at actual launch.
- PREPARING SECOND SUCCESSOR: stable-tag whole-task bridge, audit_field_order.
  Fixed8 inputs, two questions, two encodings, supplied/free plan; minimum80
  model episodes. Original varied-gold gate failed because count3 occurs4/8.
  MAIN approved explicit pre-model-output amendment3→4 without changing inputs;
  five distinct nonzero count answers remain. Constant-answer baseline4/8 is
  disclosed; weighted sums have eight distinct nonzero values. No model outputs
  were consulted. This is exploratory, not preregistered confirmation.
- COMPLETE: stable-anchor192, all192 native-valid, no missing responses.
  Later-label accuracy no matching keys34.18%, sequential85.42%, shuffled86.13%,
  arbitrary84.90%; both arbitrary/shuffled planned checks pass and improve16/16
  batches. MAIN adopted; fixed key/order contract limits the claim.
- FAILED WITHOUT UPDATES: SFT completionV1 loaded the model but omitted the
  inherited GATE_PLAN; LR attempt001 omitted START.json. Both retained unchanged
  outputs. V2 explicitly supplies six fixed existing corpus rows as the diagnostic
  training gate. LR attempt002 supplies the byte-identical qualified START binding.
- OPPORTUNITY COST: last failed LR released23:16:27.717; SFT-V2 launched
  23:28:55.575. The747.858-second gap is avoidable failure detection/recovery and
  orchestration overhead, not useful GPU training. A resumed tool session had lost
  the old PTY handles, but on-disk terminal receipts exposed the actual failure.
- MEETING: reviewed13-slide PDF plus teaching guide/evidence/publication options,
  `repos/rlm/slides/2026-09-11-advisor-meeting/`, evidence cutoff23:25. Added stable
  tags as H3, rebuilt and visually checked; earlier historical deck untouched.

Resume checkpoint: `operations/2026-09-09-allocation-5780/SESSION_2334.md`.

## Live override: 23:14 UTC

This section supersedes historical active-job labels below.

- RUNNING: stable-anchor192, PTY96739, coordinator64420/start927002164/PGID64416;
  operation2026-09-10-after-new-corpus-sft6-stable-anchor192. Final READYc1ee76c7,
  identity654f7434; launch23:04:36.442. Native audit prospective beforeoutputs.
- QUEUED: new-corpus SFT completion, PTY62844, coordinator65691/start927017339/
  PGID65690, operation2026-09-10-after-stable-anchor-new-corpus-completion.
  READY35c205b3/identity80c6477d; cap3000. Reuses immutable72capturedteachers,
  sixfull72freshAdamupdates, thenmetadata72. No recapture or comparatorrerun.
- QUEUED SECOND: LR1e5 rewardtraining, PTY36690, coordinator67784/start927045455/
  PGID67783, operation2026-09-10-after-new-corpus-completion-lr1e5.
  READYae69614d/identity166fbbfa; cap15000 startsafteractualGPUlaunch.
  ExactQS6freshAdam,8×24fixedtrainingattempts, solelast72readout.
- COMPLETE INFRASTRUCTURE FAILURE: originalnewcorpusattempt captured72/72 then
  inheritedCPU-only suite.command hid CUDA fromtraining; no model load/update.
  OWNER19abba15,EXIT96264800,released22:52:58.927. Recoveredcorpusisunchanged.
- OPPORTUNITY COST: release→anchorlaunch697.516s. Prelaunchscoringamendments
  overlappedterminal; MAIN sentfollowup via send_message to a completedagent
  instead of followup_task, delayingwake. This is avoidable orchestration cost.
- MEETING: first12slidePDF+teachingguide+evidence+publicationoptions complete,
  compiled/visuallychecked underrepos/rlm/slides/2026-09-11-advisor-meeting.
  Newrunoutcomesnotinserteduntilaudited. Historicaldeckpreserved; nopushrequested.

CPU followup: inspect previousroot-mapbridge evidence beforedesigning a new
downstream key-interface comparison; avoidbalanced-labelconstantanswer artifacts.

## Live override: 22:48 UTC

This section supersedes historical active-job labels below. Advisor meeting
preparation is now the main CPU deliverable; independent GPU research continues.

- RUNNING: new-corpus question-sensitive SFT6 plus metadata72, PTY38585,
  operation2026-09-10-after-two-harness-bridges-new-corpus-sft6; launch22:32:08,
  cap4500s. All72genuine teacher acquisitions required beforetraining.
- NEXT: stable-anchor192. Independent review found NULL-as-zero scoring;
  host_join correcting/resealing beforelaunch, inputsunchanged. No scientific
  outcome observed yet. Tests separate missing outcomes from known failures.
- SECOND: LR1e5 terminalRL192+final72, bounded15000s. CPUqualificationdone,
  MAINrevisionreview/acceptance remains. No overlap with currentGPUowner.
- COMPLETE: RLfinal6strict47/72vsstart55/72, boundsremainnegative; mixedchild40
  labelsbetter butdownstreamgatefails; directstats40validbutdramaticallyworse
  aggregateerrors. Use these to revise research, not repeat failingrecipes.

Resume checkpoint:operations/2026-09-09-allocation-5780/SESSION_2248.md.
Meetingpackage:repos/rlm/slides/2026-09-11-advisor-meeting/.

## Live override: 22:14 UTC

This section supersedes all historical active-job labels below.

- **RUNNING:** RL continuation windows4..8 from exact saved Adam2, operation
  `2026-09-10-after-checkpoint2-readout-sparse-continuation`, PTY99052.
  Coordinator4094127/start926537162; training child4094132/start926537239.
  V2 sidecar `root-composed-rl-sparse-continuation-v1`, outputattempt002,
  READY SHAeddba0ad…, identity94f51eac…. Started21:47:07 UTC. At22:13,
  windows4,5,7 committed updates3,4,5; window6 was noop; window8 underway.
  Training12000s maximum; conditional fixed-last72 readout2700s follows within
  the same coordinator. Do not start another GPU job after only training exits.
- **SERIALIZED NEXT:** two bridges, PTY70547, operation
  `2026-09-10-after-sparse-continuation-two-harness-bridges`, waiting on the
  whole coordinator above and empty GPU. Mixed-child supplied-plan40 first,
  sufficient-statistics40 second; each1200s inclusive. Accepted mixed READY
  SHA98a9ac6c… identityab010b04…; statistics **V2** READY SHA3bbc6941…
  identitya664df94…. Both reuse the same old40 control calls. The actual
  schedule is2×32 records for each64-record episode and8×32 for256 records.
  Withdrawn mixed first seal and statisticsV1 remain unlaunched; never use them.
- **CPU IMPLEMENTING:** new-corpus SFT replication, agentquestion_cards.
  New SHA-selected128 root-process training groups,8contexts×9tasks=72
  teachers and72 genuine child acquisitions; fixed24 start, fresh Adam,
  six full-corpus updates, existing metadata72 readout,4500s total cap.
  The superseded order-only proposal is not an independent training replication.
- **CPU IMPLEMENTING:** LR1e-5 composed RL from exact original QS6/fresh Adam0,
  agentaudit_host_join. Same fixed192 training attempts; sole new final72,
  reused start control,15000s total maximum. All other objective choices fixed;
  sparse-vs-initial-dense implementation qualification explicitly disclosed.
- **MAIN ADOPTED:** mixed24/192, task-aware×agreement48, checkpoint2/72.
  Mixed local gates pass but downstream transfer pending. Agreement comparison
  fails downstream gates. Checkpoint2 strict47/72 versus start55/72, tight
  missing-outcome difference bounds−9..−3; no general anti-RL claim.

The checkpoint2 parent released21:44:00.616; continuation launched21:47:07.078.
The186.46-second gap was runtime/source correction and launch overhead, recorded
as avoidable GPU opportunity cost, not training. Subsequent preparation overlaps
GPU work. Latest resume checkpoint:operations/2026-09-09-allocation-5780/SESSION_2214.md.

## Live override: 21:40 UTC

This section supersedes all earlier active-job labels below.

- **RUNNING:** fixed72 root checkpoint2 readout, V5 original unaliased source
  collector, `2026-09-10-after-mixed-sft24-checkpoint2-readout72`, PTY31301.
  Actual start21:31:21.995 UTC; 2700s inclusive. GPU engine4052598 active at
  21:37:42, 33.8GB/227W. This is inference, not another training update.
- **PREPARED, awaiting score-blind terminal/cost gate and MAIN review:** exact
  RL windows4..8 continuation from saved Adam2, at most five more updates.
  `sidecars/root-composed-rl-sparse-continuation-v1`, CAMPAIGN373366ab…,
  identity3b24ad7c…. 120 fixed training coordinates, no refill/reroll;
  1800s/update, 12000s training owner. Final fixed72 readout is separate2700s.
- **CPU PREPARING SECOND SUCCESSOR:** replace c32 child with mixed-SFT24 in
  the exact supplied-plan40 requests. Test transfer from local label accuracy
  to true six-class labels and downstream counting; reuse old40 controls.
- **COMPLETE; agent audit passed, MAIN review underway:** mixed-SFT24 and192
  readout calls, parent256.465s, training57.17s, all four checkpoints retained.
  Primary mixed full-format734/768 versus c32725; compact665 versus590.
  Both frozen local promotion gates pass. Full-format metric here projects
  six labels to A/B/other, not true six-class accuracy. Both panels are research-
  exposed. Audit FINALf9814287…; no generalization or whole-RLM claim yet.
- **COMPLETE; audit now explicitly reactivated:** task-aware selection ×
  two-sample verification48. All planned calls collected in120.192s; no
  scientific result adopted before native audit and shared-cost accounting.
- **MAIN ADOPTED:** prior pure-interface SFT and confidence-vs-uniform recheck.
  Their MAIN_ADOPTION.json receipts retain failed retention/downstream gates.

Mixed completion≈21:30:33 to V5 launch21:31:22 was about49 seconds. Earlier
readout attempts failed before inference due wrong environment and source binding;
they remain separate zero-request engineering failures, not model outcomes.

## Live override: 21:27 UTC

This section supersedes all earlier active-job labels below.

- **RUNNING:** mixed child-interface SFT24 plus192 fixed readout calls,
  operation `2026-09-10-after-readout-binding-failure-mixed-sft24`, PTY9629.
  Actualstart1789075576.5109015 (21:26:16.511UTC). Nativeowner,3600s inclusive.
  READYidentityab27c58c…, SHA439d0021…. MAIN13tests11.91s/40pins, allsource
  diffs reviewed,96exact training-row choices and192request bodies independently
  matched to predecessor except the intended model/coordinate identity changes.
- **PREPARING NEXT:** fixed72 checkpoint2 root evaluation, attempt003. Use
  original unaliased qualified collector and authentic source starting lineage.
  Attempt001 failed0.538s because MAIN selected CONTROL Python withoutverifiers.
  Attempt002 failed3.253s before inference because the reused runner lacked its
  original START binding; further compatibility assumptions are being removed.
  Both had zero model requests and are preserved, not called model failures.
- **COMPLETE; AUDIT PENDING:** task-aware targeting×two-sample verification,
  all48 planned calls collected in120.192s; exact ownerae151be8…,
  EXIT08d6262a…. Four derived policies reuse samples and are not independent;
  agreement costs two samples, not one. No model-effect claim before nativeaudit.
- **COMPLETE:** exact sparse RL recovery committed Adam2/model/optimizer/RNG.
  Parent319.492s, actual optimization241.797s,154turns/647114causal tokens/
  18517credited actions. Peakallocated12.294GB/reserved17.421GB,deltaL2.14389.
  Adapter6c038070…,stateffce53a9…. Originalfailednumericalgate remainsfailed;
  successful newengineering policy is not bitwise equivalence or behaviorgain.
- **COMPLETE:** prior child-interfaceSFT48/480calls plus96reused. MAIN literal
  native decode, class projection and confusion recount all576 validstop,
  576unique providerIDs and1440receiptpins. Confirmed primaryc32full725/ABO590,
  fullSFT745/580,ABOSFT707/680 of768. Compactgain+90; fullretentionloss18
  misses2ppgate. Report wording/prospective-reader amendment receipt pending;
  no pristine holdout claim. Mixedrun follows this signal.
- **NEXT TRAINING DESIGN:** continue still-unrun RLwindows4..8 fromAdam2,
  using successful sparsehead and adequate bounded per-window budget, after
  fixedcheckpoint2 readout. Do not retire RL after onlytwo updates. No extra
  homogeneous-group refill or outcome-selected checkpoint; collect actual cost.
- **IDEA ADDED:** `ideas/2026-09-10-credit-assignment-and-imperfect-repair.md`
  relates current findings to APEX-Searcher, CARL and GuardedRepair, with exact
  URLs/versions/read depth and bounded experiments. No novelty or reproduction
  claim; no asset downloads. Reference-child training and evidence-consistent
  rewards remain conditional, not implementation-ready.

Avoidable gaps remain costs: sparse2 end≈21:13:24 to next informative task48
start21:18:42 included source review and a wrong-environment launch; task48 to
evaluationattempt002 was38seconds; its zero-request failure to mixedstart was
about4min53s. Do not count these as GPU training. Mixed preparation was also
delayed because MAIN sent a message to an idle agent without triggering a turn;
use `followup_task` after checking status for a completed agent.

## Live override: 21:09 UTC

This section supersedes the historical status descriptions below.

- **RUNNING:** exact sparse-head RL recovery-v2, operation
  `2026-09-10-after-numerical-diagnostic-sparse-recovery2`, parent4038185 /
  start926302962 / PGID4038184, PTY81175. Actual start21:08:04.416 UTC
  (1789074484.4160743); work1800s, inclusive2100s. Restore exact checkpoint1
  Adam/RNG and failed11-episode/154-turn group; commit at most checkpoint2.
  READY identity31a7ac3d…, SHA390d5a19…. MAIN95 new Python lines read,
  two focused tests passed in0.19s; inherited exact trainer already reviewed.
- **PREPARING NEXT:** mixed-contract child SFT24 plus fixed192 readout.
  Same c32 initialization, fresh optimizer, same96 training contexts/order/seed;
  half full-six and half A/B/other contracts, no doubled examples. Question:
  can compact-format gains coexist with original-format retention?
- **CONDITIONAL NEXT:** fixed72 root readout only after genuine checkpoint2
  commits; compare retained start/checkpoint1 observations without rerunning them.
- **COMPLETED:** child-interface SFT48 and480 readout calls, all checkpoints
  saved. Producer primary counts: c32 full725/compact590 of768; full-six SFT
  full745/compact580; compact SFT full707/compact680. Compact gain+90 but
  full-six loss18/768 exceeds2pp retention gate. Independent native audit pending.
- **COMPLETED:** selective recheck24, agent native audit all24 valid/all16
  arm-episodes valid. Confidence71 repairs/31 regressions (net+40 labels),
  uniform19/28 (net-9). Exact downstream1/8 versus0/8 misses frozen+2 gate.
  MAIN adoption review in progress; no claim of reliable downstream benefit.
- **COMPLETED:** supplied-plan ceiling40 and fresh ordinal192, MAIN adopted.
  Ceiling1129/1280 child labels but0/8 exact downstream; private oracle8/8.
  Fresh ordinal late interaction+42.7734pp, positive16/16 new contexts.
- **FAILED, PRESERVED:** original sparse-v1 numerical qualification; no update.
  Diagnostic then showed dense-repeat also fails old1%/.99995 gradient gates.
  Recovery-v2 uses a separately documented, post-diagnostic exploratory policy
  (3%/.9995 and sparse difference <=2x repeat). Old failure is not relabeled.
- **OPERATIONS COST:** GPU release about20:56:34 to next launch21:08:04 was
  approximately11.5 minutes idle for preparation and context resumption. This
  is lost opportunity, not productive GPU execution. Native export verification
  and model loading occur inside the new job before actual GPU training.

## Allocation and current owner

One exclusive A100 40GB full MIG `MIG-d3fcfaa9-e5d5-59f3-854c-01f98007d465`
on an27, allocation 5780; CPUs 0..15 and 64GiB. Lease ends September 11 at
17:32:38 UTC (epoch 1789147958). GPU is assigned to sparse RL recovery; loaded
memory alone is not counted as productive utilization.

1. **COMPLETE; ANALYSIS IN PROGRESS: composed RLVR attempt003.** Parent3862232/
   start925748075/PGID3862204, PTY29892; operation
   `2026-09-10-after-query192-composed-rlvr3`.
   READY identityf1736aea…, SHA484331ed…. Exact QS6 root and fixed c32 child,
   192 fixed training coordinates, up to eight actual updates, fixed-last144
   readout, 7200-second inclusive cap. Phase timer corrected; earlier failed
   attempts retained. MAIN22 source+345 input/proof pins verified and four
   focused tests passed; agent15 tests passed. Actual24-slot CPU transport
   fixture passed. Checkpoint every actual update with optimizer/RNG state.
   Actual start1789069515.585182. Window01 all24 successes: no update.
   Window02 selected8 episodes/24 root turns: update1 checkpoint saved and all
   five payload hashes verified by MAIN. Adapter358d2cef…, state93300fe9….
   Window03 selected11 episodes/154 turns, max8192 causal tokens versus1964
   previously; CUDA allocation failure warning then240-second training timeout.
   No second checkpoint. Fixed readout complete; parent exit0/released in2609.59s.
   Native audit start55/71 versus last53/71; one actual update, no improvement.
   Manual execution review pending. Producer zero cost ledger has a layout bug:
   independent actual physical union1178, not zero; audit preserves this correction.
2. **COMPLETE; MAIN ADOPTED: fresh-context ordinal192.** Parent3872187/
   start925769952/PGID3872184, PTY41062; operation
   `2026-09-10-after-rlvr3-fresh-ordinal192`. Sidecar
   `leaf-mnli-positional-anchor-new-context-v1`, READY identity5e9e8999…,
   SHA5ae8a97c…. Sixteen new contexts ×12 factorial cells. Primary late
   input-number×output-number interaction; no changes to the old output-only gate.
   MAIN eight tests6.07s and27source/12input pins verified; independently checked
   premise/hypothesis exclusion against37 named inventories, including field96.
   All192 native/valid; late interaction+42.7734pp, positive16/16, gate passed.
   MAIN192 exactrequest rerenders/literal output recounts and576capture pins,
   byte-identical replay; report early/late denominator typo qualified additively.
3. **COMPLETE; TERMINAL AUDIT IN PROGRESS: supplied-plan ceiling40.** Parent3927914/
   start925925797/PGID3927913, PTY88575; operation
   `2026-09-10-after-fresh-ordinal192-supplied-plan40`.
   Accepted wait1789070712.7294667; READY33feec97…, identity71a7f6ce….
   All four scale clusters at64/256 records, forty genuine c32 child calls,
   supplied host acquisition and J1 reducer; no root calls or gold in prompts.
   MAIN six tests6.77s,27pins and original/recovery context equality verified.
   Parent exit0/released in124.528s; all40responses retained. Diagnostic ceiling,
   not learned planning or compute-matched ablation. Actualstart1789072567.968351.
4. **RUNNING: child-interface continuation SFT.** Two
   matched24-update continuations from c32, full-six versus A/B/other contracts,
   followed by288new-pair and192development readout calls. READYb1699136…,
   identity80bea707…; MAIN12tests12.90s,40pins0errors,192exactpromptprefixes.
   Parent4016868/start926102156/PGID4016867, PTY1772. Operation
   `2026-09-10-after-ceiling40-child-interface-sft48`; actualstart1789072696.5400882.
   Fixed24updates perarm, checkpoint6/12/18/24 withAdam/RNG;10800inclusive.
   Design and feasibility receipt:
   `analyses/leaf-trec-child-interface-sft-followup-idea-2026-09-10/`.
5. **ACCEPTED AFTER CHILD SFT: exact sparse-head RL recovery.** Parent4019813/
   start926122132/PGID4019812, PTY75518. Operation
   `2026-09-10-after-child-sft48-sparse-rl-recovery`; accepted1789072676.0871365.
   READYd3a76973…, identity40883af4…. MAIN8tests7.71s/23pins0errors and
   actualtrainenv nativepreflight. First no-step numerical/longest-turn gate<=900s;
   iff passing, exact failed154turn group fromcheckpoint1/Adam/RNG, atmostupdate2
   <=1800s,3000inclusive. No recollection, truncation, newgroups or evaluation.
6. **CONDITIONAL DESIGN: confidence-directed child recheck.** Matched24-call
   selective-versus-uniform25% recheck only if adoptedceiling reveals child-error
   bottleneck. No producer/GPUapproval yet; designin
   `analyses/root-supplied-plan-selective-recheck-design-2026-09-10/`.

## Latest decisions and evidence

- Scale64 ended in1850.70 seconds; all GPU ownership released. Native replay:
  38 observed (9 correct,29 wrong including16 empty) and26 timeout-NULLs.
  Manual12 actual-path faithful,7 also correct;6/7 are zero-gold cases.
  Only1/52 nonzero-gold cases was verified correct. No scale-transfer claim.
  Additive qualifications preserve the original frozen row judgments.
- Query192 ended in204.64 seconds; MAIN614pins,192 reconstructed native requests
  and literal-contract/confusion recounts passed. Full-six host-projected accuracy
  base672/c32 726 of768; direct A/B/other605 for both. Compact interface lost the
  adapter's aggregate gain. Contract-specific continuation training is the next test.
- Ordinal96 is adopted: all96 native responses valid, MAIN341 pins and96 exact
  request rerenders/literal contract recounts passed. Matched numbering improved
  total590→933/1152 and late292→620/768. Output-only late gain16/768 failed its
  frozen gate. Fresh-context replication tests the package interaction.
- Field96 fresh-context selective effect+9.765625 points, positive14/16, all96
  valid; narrowly missed frozen10-point gate. Directional support only.
- Metadata144: correct-and-performed12→50/72, composed0→32/48. Same records
  under changed public metadata, not new records or independent training.
- Composed RLVR attempt002 made physical requests but no updates: stale180-second
  startup alarm interrupted collection after146.67 seconds, before360-second cap.
  MAIN stopped the exact owner to avoid duplicate unchanged readouts.
- Scale→query handoff3.0519 seconds; query→RLVR2.7844 seconds.
  Ordinal96→scale handoff was4.6105 seconds. Earlier failures and idle time remain
  in the historical record; do not describe the entire allocation as productive.

## Next decisions

Audit the RL fixed-last readout; diagnose its long-trace training memory/time failure
without changing the running campaign. Audit fresh ordinal and supplied-plan results
before any end-to-end promotion. Prepare child contract training in parallel.
The queue is adaptive:
only accepted exact-parent jobs above own future GPU transitions.

## Durable entry points

[Plain-language findings](analyses/CURRENT_SUMMARY.md) · [Research priorities](analyses/PROMISING_RESULTS.md) · [Question cards](questions/README.md) · [Analysis index](analyses/README.md).

[Complete earlier queue and scheduling history](operations/2026-09-10-status-history-at-1917/RESEARCH_QUEUE.md) is preserved byte-for-byte. Historical RUNNING labels are not active reservations. [Migration receipt](../../ARTIFACTS.md#unpublished-files "Not published: operations/2026-09-10-status-history-at-1917/PATH_MAP.json").
