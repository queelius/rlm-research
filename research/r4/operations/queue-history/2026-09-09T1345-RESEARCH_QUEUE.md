# Live GPU research queue

Updated September 9, 2026, 13:45 UTC. MAIN owns GPU launches and cleanup.
[Previous state](2026-09-09T1311-RESEARCH_QUEUE.md).
Accepted sources, raw outputs and sealed analyses are immutable; this is a living index.

## Allocation and active work

One exclusive A10040GB full MIG on an21, Slurm5771, ends19:07:17UTC
(epoch1788980837). Do not end this session at a routine report. GPU idleness is
a real opportunity cost. Eight logical CPUs (32–35,96–99),64GiB host memory.
Model memory alone is not useful-work proof.

| State | Question and exact authority |
|---|---|
| ACTIVE: complete-success SFT and shared readout72 | after-ledger16-success-sft72, PTY1584, parent3988732/start1076512135. Actual COMMANDstart1788961314.0896254 (13:41:54.090). PLAN3c386768…/ACCEPTANCEfc6c0f40…,2916paths; READYced16bec…/identity50515d52….27 training-only successful trajectories/114 native root turns/15,256targets, eight full-corpus updates from efab/freshAdam.216episode/912turn/122,048target exposures. Fixed SFT8, last-savedRL7 and baseline on24identical fresh readouts each; frozen phase orderRL7→SFT8→baseline.4530outer/4500owned/4380work/1200training/900eachreadout. Two real checkpoints at13:44; allocator retry warning did not prevent steps1–2. No outcome claim. |
| CPU NEXT1: move sparse reminders over the same records | Independent released-model auditor finishes Qwen report, then proposes phase0/1/2/3 cadence4 versus constant controls. Each fixed record can be compared at all reminder distances, removing the present different-record distance confound. Candidate192calls; design not yet approved or GPU-ready. |
| CPU NEXT2: outcome-directed root/harness follow-up | Ledger16 finished16/16, independent source/native audit underway. Use its evidence and the richer SFT result to rank harness replication versus adaptive terminal-RL continuation. No speculative GPU filler or unapproved change to active weights/rewards. MAIN prepares smallest informative follow-on while GPU trains. |

There is currently one active accepted GPU parent and no second accepted waiter.
This is a queue-readiness risk: preparing two decision-relevant successors takes
priority over broad tests or documentation. Root jobs use qualified private local
image8cfe/store /tmp/rlmc.0m4242; historical/shared stores remain unchanged.

## Newly completed work and analysis status

- Released-model Qwen144: exit0,144/144 recorded,1269.344s scientific/1270.107s
  outer. Independent early reconstruction: matching IDs beat constants in all48
  model×task×context×seed pairs;143valid, one3072-token truncated constant output
  retainedstrict0, noNULL. Both released exact-revision models ran without research
  adapters. Final report is being sealed; do not treat component gain as wholeRLM.
- Equal-row SFT48: complete718.578s scientific/719.120s outer. Independent
  [report](../../analyses/root-interface-sft-row-mean-live-2026-09-09/REPORT.md),
  cbc2bfd5…: both same2/24correct, noNULL; syntax9→7, coverage16→12.
  Terminal microexamples already have almost zero teacher-forced CE despite larger
  coefficient mass. Do not promote weighting alone or failed-trajectory cost savings.
- Reminder-order96: exit0,96/96 recorded, all96 actual typed-prompt matches;
 128.307s collection/177.793s outer. Independent primary raw audit pending.
 Missing ownedTERMINAL marker remains null, not fabricated; parent exit/release
 and STATUS are observed. No outcome inference from completion.
- Running-tally ledger16: exit0,16/16 rows/67native attempts,233.247s science/
 233.766s outer. Exact plan5150d889…/acceptance3a27e455…1198paths,
 READY4ccf83e1…; active during13:37–13:41, now released.
 Independent pre-outcome method followed by terminal audit in progress.
- Complete-success screening sealed:27confirmed of29strict successes among80
 training attempts from rounds1–5;114real root turns/15,256targets. Two weaker
 aggregation-lineage cases excluded prospectively. No evaluation trajectories.
 [Report](../../analyses/adaptive-success-trajectory-feasibility-2026-09-09/REPORT.md).

## Completed evidence and decisions

| Finding | Evidence and implication |
|---|---|
| Adaptive RLVR stops after seven real updates | All128 training attempts completed; round8 has one all-correct group and one all-wrong admitted group, so no within-prompt reward variation. Predeclared no-reroll stop: no step8 or planned final8 readouts. Seven checkpoints preserved. Only original paired post-update validation4 remains2/8→2/8. A NEW prospective shared readout will evaluate last-saved7 without rewriting this stop. [Terminal audit namespace](../../analyses/root-adaptive-rlvr-live-2026-09-09/README.md). |
| Sparse reminders expose a local correspondence weakness | All144 outputs valid. Matching-label accuracy falls between cadence4 reminders, especially on news:102/128 correct at tagged positions, then51/128,44/128,38/128. Matching versus constant gives+61 correct at anchors but−18 across nonanchors. All24 context-seed pairs lose accuracy when reminders become sparse. [Independent raw recheck and plain-language plot](../../analyses/leaf-sparse-anchor-main-review-2026-09-09/REPORT.md). Output tokens fall substantially; correctness also falls, so no free-efficiency claim. |
| Interface SFT changes behavior, not established accuracy | Four real Adam updates,32authoredrows/twoepochs; only83/1603 targettokens teach finalanswers. Helperuptake0/24→24/24;22firstactions exactlycopy4-recordexample. Strictcorrect1/24→2/24;syntax19/24→9/24. All48graphs clean,50/50typed mapsvalid,744/800labels;11complete relevantcoverage,4correct map-derivedcounts,2ofthose mishandled atfinal. [Independent audit](../../analyses/root-interface-sft-live-2026-09-09/REPORT.md),959ac7ce…. Warmstart forRL, notbettercountingclaim. |
| A useful hand-written filtering baseline exists | Typed operators: userfilter8/8correct, userall6/6observablecorrect+2setupNULL, global3/8. Six jointlycorrect userpairs reduce childcalls48→6 (87.5%), uncachedinput3642→632 (82.6%), output6931→428 (93.8%). Zero sampledrootpolicy.22observableendpoints but only6 episode.ok;16finalizeerrors/2setupNULL. [MAIN independent primary review](../../analyses/typed-adaptive-operator-live-2026-09-09/PRIMARY_REVIEW.md). Original report cacheunknown sentence superseded by additive correction;120physicalcalls allcacheknown. |
| Typed child structure alone is insufficient | Capped36plan/31raw/27observable;U6correct/9observable,R1/8,T3/10, nineNULLorunrun. T−R8observedpairs2wins1loss5ties,4unresolved; full12net[-2,+4]. Eligibletyped15/15validmaps versus raw16/70responses, but only1of3 eligibletypedrootscorrect. Three late cancellation files explain STATUS28versus31raw. [Independent audit](../../analyses/typed-helper-child-live-2026-09-09/REPORT.md),2b1a10b5…. Do not turn syntax guarantee into accuracy gain. |
| ID benefit does not require emitting current ID before label | Cue48 allvalid. TREC tag-first/label-first matching251/240 versus ordinal129/122 of256; SST241/241 versus162/157. Matching advantage remains about31–48points either order. Order interactions small/mixed across the two context clusters/task; not equivalence or an internal-mechanism claim. [Report](../../analyses/output-cue-order-live-2026-09-09/REPORT.md),5759b983…. Sparse144 is now audited; reminder-order96 is accepted and waiting. |
| New-task ID effect transfers to original weights | AG96: all96 valid/authenticated; meaningful/ordinal correct of512: original q420/180,p423/181; old-SFT q404/184,p405/187. Gains42.6–47.3pp, positive in each of four contexts; prefix effects≤0.59pp. Historical helper SFT is not necessary. [Report](../../analyses/agnews-identity-live-2026-09-09/REPORT.md), seal00954079…. Component package effect, not whole-RLM benefit or isolated copying mechanism. |
| Planning pilot exposes prerequisites | Adaptive40/48: filtered user3/8 success coverage, all-file0/8, free0/16. All40 completed; empty endpoints stay null under this study's contract. Fixed operators23/44 attempted sessions yield complete maps;21 parsed-empty outputs despite112total HTTP200 calls. Free roots never call children;12 bare numerals all wrong even if prefix repaired. [Report](../../analyses/adaptive-filter-live-2026-09-09/REPORT.md),1d96e966…. No clean matched-success efficiency/planning result; test child structure and root competence separately. |
| API/procedure restoration is insufficient | Uptake96: U/D/R/V correct original4/2/0/0 and step8 9/1/1/0, each of12. All96 observed.127 trusted contract-matched child invocations:61 complete maps,65 parsed-empty,1HTTP tail. Only1/27 uptake-positive episodes correct; correct complete child evidence can still be mishandled by root. [Report](../../analyses/receipt-uptake-live-2026-09-09/REPORT.md),84a853ca…. Neither child-only nor root-only remedy established. |
| Role wording did not improve answers | Role16:2/8→2/8,1gain1loss; all observed. No child tool loops in either arm, so targeted mechanism absent. Calls79→57 but uncached/output tokens rise; three identical-prefix seed pairs already differ before child treatment. [Report](../../analyses/child-role-suffix-live-2026-09-09/REPORT.md),a5c2c911…. Do not promote suffix or infer deterministic paired trajectories. |
| Broader root RL has modest uneven transfer | Fixed final16:13/48→16/48,8gains5losses. Composition64 flat5/24, reserved3/12→2/12,128records2/8→3/8,256records0/4 both. All16 actual root-only updates verified. [Report](../../analyses/root-broad-equality-continuation-live-2026-09-09/REPORT.md),8c288369…. Not general decomposition learning. |
| Broader counts often get closer | Posthoc24 both-numeric pairs: MAE4.625→0.875,9closer2farther; numeric coverage31/48→38/48. Response-selected cohort, not new primary or population causal effect. [Diagnostic](../../analyses/root-broad-posthoc-examples-2026-09-09/REPORT.md). |
| Earlier root-training gain repeats directionally | First5/24→16/24; independent seed9/24→15/24,11gains5losses,4of6contexts improve. Selectedstep6 in second, not savedstep8. Same six exposed contexts. [Audit](../../analyses/root-independent-seed-continuation-live-2026-09-09/REPORT.md). |
| Identity controls preserve a large advantage | Prospective384allvalid: disjoint matching IDs beat counters47–53points on question types and~35points on sentiment, all four context sums/task/prefix positive. Numeric overlap explained part, not all, of the earlier gap. Counts can conceal wrong correspondence. [Audit](../../analyses/identity-factorial-live-2026-09-09/REPORT.md). |
| Extra helper-ID SFT adds no useful gain | Earlier mixed-size373/384 versus ID-trained374/384, both fail long plain-list output;624 matched readouts audited. [Report](../../analyses/anchor-indexed-followups-live-2026-09-09/REPORT.md). |
| Corrected root-tool interpretation | All48 historical first prompts end only with assistant header; both policies SAMPLE their tool opener. Syntax13/24→22/24 remains, but no prefilled opener or increased observed tool-attempt rate. [Additive correction](../../analyses/root-first-action-screen-2026-09-09/PREFILL_CORRECTION.md),bcc92d48…. Old seals preserved. |

## Ranked conditional work

The final adaptive RLVR report is now sealed: [REPORT](../../analyses/root-adaptive-rlvr-live-2026-09-09/REPORT.md),04fd5d61…. Seven actualupdates/95selectedepisodes/572rootturns/68,008creditedtokens; STOP after round8 has no within-prompt variation. No original step8/final8 evaluation. Three availability NULLs arise from the native IPython broker timeout, not HTTP/provider outages; diagnose separately without hot-editing active jobs.

1. Preserve the seven-update RL stop and evaluate its last saved policy in the NEW
   shared readout. Separate loss weighting from richer successful trajectories through
   the accepted equal-row control and new complete-success SFT package.
   Typed maps and helper uptake now work, but coverage and final answers do not.
   Do not call example copying autonomous planning or optimize helper counts as reward.
2. Finish accepted released-model and sparse-reminder-order comparisons. AG supports
   new-task/original-weight robustness. Preserve four context clusters, actual native
   templates, output instruction/grammar package and exposure caveats.
3. Metadata-sensitive questions distinguish correspondence from global-count
   cancellation. Filtering is a legitimate alternative plan, not a confound to
   forbid. Fixed operators are not model policy likelihood or RL training data.
4. Use structured outcomes to choose binary terminal RL versus a separately
   designed correctness/cost reward. Do not hot-change rewards or salvage
   malformed outputs to manufacture a gain.
5. Continue bounded primary-literature/source acquisition linked to concrete
   experiments. Generic semantic query planning, typed wrappers, IDs and
   model–harness co-adaptation are established directions, not novelty claims.

## Hardware time, artifacts and preservation

Actual scheduling gaps, excluding successor service/runtime startup:
broad→uptake4.153s; uptake→role1.394s; role→AG3.734s;
AG→adaptive5.795s; adaptive→cue4.260s.
Cue exited1788950238.1919425; typed launched1788950856.9068444:
**618.715seconds (10min18.7s) of queue exhaustion** while typed preparation/
qualification and parent launch review finished. Record this as avoidable
opportunity cost, not useful GPU work. Preparing two successors is now explicit.

Typed36→operators24 automatic handoff:6.1024s; operators24→SFT5.1516s.
RL accepted_job_exited1788958877.8214161→Qwen actualCOMMANDstart1788958885.619105:
7.7977s between those recorded clocks (launch event is slightly earlier than COMMAND).
Sparse exited1788955003.3921397; RLVR launched1788955711.9499612:
**708.558seconds (11min48.6s) of queue exhaustion** while scientific preparation,
MAIN start binding/launch review and session-context recovery completed. This is
avoidable opportunity cost, not useful GPU work. Qwen144 now has its actual waiter.

Typed36 reached its collection
cap;1841.67s outer is not1841.67s continuous GPU arithmetic. Persistent VFS runtime
waiting remains measurable; future SFT/common-local runtime targets that overhead.

Completed outer wall: uptake1910.826s; role346.097s; AG461.172s;
adaptive489.902s; cue199.653s; typed36 1841.670s; operators1210.547s;
interfaceSFT+48readouts755.335s versus31.650s training/checkpoint; sparse144 322.189s. These are not optimizer time or all-active GPU time.
BROAD combined scientific8083.08s versus430.46s optimizer/checkpoint; earlier
stops/nulls and their costs remain in the sealed audit and historical queues.

All new outputs remain in the external research store. No cleanup, cache deletion,
shared environment mutation, live-file relocation, Git commit or push was performed.
Private image8cfe… is CPU-qualified; no end-to-end speedup established. Its original
fixture failures and installed-version provenance remain preserved.

[Current summary](../../analyses/CURRENT_SUMMARY.md) ·
[Promising findings](../../analyses/PROMISING_RESULTS.md) ·
[Analysis index](../../analyses/README.md) ·
[Session checkpoint](../../../../ARTIFACTS.md#unpublished-files "Not published: operations/2026-09-09-continuous-allocation/SESSION.md").
