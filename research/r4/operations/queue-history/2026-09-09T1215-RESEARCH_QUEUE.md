# Live GPU research queue

Updated September 9, 2026, 12:15 UTC. Main owns GPU launches and cleanup.
Previous complete state: [11:35 snapshot](2026-09-09T1135-RESEARCH_QUEUE.md).
Accepted sources, raw outputs and sealed analyses are immutable; this is a living index.

## Allocation and active work

One exclusive A10040GB full MIG on an21, Slurm5771, ends19:07:17UTC
(epoch1788980837). Do not end this session at a routine report. GPU idleness is
a real opportunity cost; keep useful follow-ons prepared while the current run
executes. Allocation is eight logical CPUs (32–35,96–99) and64GiB host memory,
not the whole node. Model memory alone is not proof of useful GPU work.

| State | Question and exact authority |
|---|---|
| ACTIVE: adaptive root RLVR8 | Can terminal rewards turn newly learned helper use into correct final answers? Launched12:08:31.950, operation after-sparse144-adaptive-rlvr, PTY93472, parent3804776/start1075952176. PLAN1c75b18e…/ACCEPTANCE0b427068… binds865paths; CAMPAIGN51afee1b…/START_BINDING52f2ac7b… selects fixedSFTfinal4 efab2913, freshAdam/RNG.128train+24val+32transfer=184, fixedfinal8, every-update checkpoints, no rerolls/no-mixed-round stop.7080work/7200owned/7230outer. Validation0 eight records complete; GPU33828MiB/215.69W at12:15 and next stage progressing. No reward result read by MAIN yet. |
| ACCEPTED WAITING NEXT1: released-model identity144 | Operation after-adaptive-rlvr-qwen144, PTY40783, parent3814686/start1075976013. PLAN4862b4b0…/915acceptedpaths; READYc62c85a4…. Exact actual RLparentclock1788963061.9795966 worstcase. Does matching-ID benefit extend to Qwen3.5-4B versus Qwen3-4B-Instruct2507, neither with research adapters?12 exposed contexts/four eachTREC,SST,AG×two freshseeds×plain/matching/constant×two models.144calls,2400work/2640owned/2670outer. Model-specific nonthinking templates, no-prefixcache/eager/BF16; actual Qwen3.5 A100 kernels unqualified until launch. |
| DESIGN PREPARATION NEXT2: equal-row SFT | Keep original32authoredrows/start473210/fourupdates/order/seed/LR/masking; change only global-target-token normalization to equal-row loss. Compare fixedfinal4 against frozen token-weighted efab2913 on48 fresh paired readouts of same exposed24task coordinates. Tests whether downweighted terminal examples explain poorer final syntax; no new complete trajectories. Exact proposal awaiting MAIN reading, no implementation/launch yet. |
| CPU AUDIT: sparse output IDs144 | Completed11:56:43.392,322.189s outer,exit0. READY25b80395…/STATUSa7f1d4bc…/FINISH6eb67334….144calls/9216labels on12exposedcontexts, cadences1/4/16×matching/constant. Independent nonauthor METHOD5b4fa6fc… written postterminal before reading outcomes; outcomes not yet promoted. |

Only the RLVR job currently owns the GPU. The next job already has an accepted,
running exact-parent waiter. Equal-row SFT is being prepared in parallel as the
second successor. Both RLVR and SFT readouts use the qualified private local runtime
image8cfe/store /tmp/rlmc.0m4242. Original persistent stores remain untouched.

## Completed evidence and decisions

| Finding | Evidence and implication |
|---|---|
| Interface SFT changes behavior, not established accuracy | Four real Adam updates,32authoredrows/twoepochs; only83/1603 targettokens teach finalanswers. Helperuptake0/24→24/24;22firstactions exactlycopy4-recordexample. Strictcorrect1/24→2/24;syntax19/24→9/24. All48graphs clean,50/50typed mapsvalid,744/800labels;11complete relevantcoverage,4correct map-derivedcounts,2ofthose mishandled atfinal. [Independent audit](../../analyses/root-interface-sft-live-2026-09-09/REPORT.md),959ac7ce…. Warmstart forRL, notbettercountingclaim. |
| A useful hand-written filtering baseline exists | Typed operators: userfilter8/8correct, userall6/6observablecorrect+2setupNULL, global3/8. Six jointlycorrect userpairs reduce childcalls48→6 (87.5%), uncachedinput3642→632 (82.6%), output6931→428 (93.8%). Zero sampledrootpolicy.22observableendpoints but only6 episode.ok;16finalizeerrors/2setupNULL. [MAIN independent primary review](../../analyses/typed-adaptive-operator-live-2026-09-09/PRIMARY_REVIEW.md). Original report cacheunknown sentence superseded by additive correction;120physicalcalls allcacheknown. |
| Typed child structure alone is insufficient | Capped36plan/31raw/27observable;U6correct/9observable,R1/8,T3/10, nineNULLorunrun. T−R8observedpairs2wins1loss5ties,4unresolved; full12net[-2,+4]. Eligibletyped15/15validmaps versus raw16/70responses, but only1of3 eligibletypedrootscorrect. Three late cancellation files explain STATUS28versus31raw. [Independent audit](../../analyses/typed-helper-child-live-2026-09-09/REPORT.md),2b1a10b5…. Do not turn syntax guarantee into accuracy gain. |
| ID benefit does not require emitting current ID before label | Cue48 allvalid. TREC tag-first/label-first matching251/240 versus ordinal129/122 of256; SST241/241 versus162/157. Matching advantage remains about31–48points either order. Order interactions small/mixed across the two context clusters/task; not equivalence or an internal-mechanism claim. [Report](../../analyses/output-cue-order-live-2026-09-09/REPORT.md),5759b983…. Sparse reminders now queued. |
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

1. Run terminal-reward RL from the exact interface-SFT checkpoint; concurrently
   separate loss weighting from missing full-task demonstrations with equal-row SFT.
   Typed maps and helper uptake now work, but coverage and final answers do not.
   Do not call example copying autonomous planning or optimize helper counts as reward.
2. Follow cue-order evidence with the smallest informative correspondence
   comparison; AG supports new-task/original-weight robustness. Preserve four
   context clusters, output instruction/grammar package and exposure caveats.
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
Sparse exited1788955003.3921397; RLVR launched1788955711.9499612:
**708.558seconds (11min48.6s) of queue exhaustion** while scientific preparation,
MAIN start binding/launch review and session-context recovery completed. This is
avoidable opportunity cost, not useful GPU work. Qwen144 now has its actual waiter.

Typed36→operators24 automatic handoff:6.1024s. Typed36 reached its collection
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

