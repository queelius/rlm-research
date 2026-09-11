# Live GPU Research Queue

Updated: 2026-09-09 00:36 UTC

## Immediate live status (supersedes older running/preparing labels below)

**00:36 authoritative status:** one A100 on an21. Both mixed-size SFT runs are
COMPLETE. Root campaign V2 owns the GPU and serial service/training transitions.
No other GPU launch is authorized while its operational waiter remains live.

- **COMPLETE:** mixed-size SFT A, session93960 EXIT0,206 actual updates,
  1151.455 trainingseconds. Fixed5 test477/489,98/98 valid. Final64 gives0/6
  valid arrays,5 truncated: no demonstrated reliable32-to64 extrapolation.
  Zero strict aligned labels means unavailable alignment, not all labels wrong.
  Checkpoint0206 SHAe822c841b78ac448c7860f5e3e7a7053cfce68c57f4a1d8f5584e1c728b35531.
- **COMPLETE:** mixed-size SFT B,204 updates,1142.028 trainingseconds,
  fixed5 test476/489,98/98 valid. Final64 gives six canonical JSON arrays with
  lengths62/58/62/57/62/58:0/6 usable,0 truncated. Training changes failure shape
  but does not establish reliable64-item output. Final adapter SHA59ad854293142161f6b5e613dd5d1e3630fed600637106d5eae2cbcd764e9200.
  Session28844 completed its B launch; never resume/relaunch the completed attempt.
  Full report`analyses/mixed-size-prefix-diagnostic/REPORT.md` keeps strict and
  post-hoc prefix diagnostics separate; A/B compute is not exactly matched.
- **RUNNING:** independent root-only RLVR campaign V2, automatically launched
  00:25:36, RUN started00:25:39, deadline04:25:39 UTC (epoch1788927939.309858),
  eight fresh32-rollout rounds maximum, persistent Adam, fixed c32de child,
  eight pair workers,4-hour envelope. Parent verified V2, CPU session53956 EXIT0.
  USE `campaign_lifecycle_v2.py`, not unused V1. Amendmenta9202fe166fcdd667c0ca70d12b051d1e5ac110fa33679cf1aa671feace2d1a0.
  Operational waiter session39335/PID1643395 is live; campaign output
  `root-rlvr-campaign-v1/outputs/attempt-v2-001`. It owns all service transitions;
  don't act on an older service PID after it rotates. Initial service worker1650238
  is historical as soon as first training begins. Validation00 complete2/8;
  round01 export complete12/32 strict, no nulls,7mixed groups/28selected episodes,
  63root turns/23130credited tokens; first optimizer result pending at00:36.
  Source/log: `operations/2026-09-09-succession/B_to_root_campaign.py` and
  `.events.jsonl`. B success is not a dependency: campaign starts original root
  with old trained child, so B failure is retained but does not block independent RL.
- **READY / AUTOMATICALLY QUEUED:** leaf post-SFT suite, session56459,
  `operations/2026-09-09-succession/after_root_campaign.py` waits for owned
  campaign waiter1643395/start1071664442 and empty GPU, then launches
  `leaf-post-sft-suite-v1/suite.py run --output .../outputs/attempt-001`.
  Suite identity6aed87ef5c92e47b1074f1cea68bad7dc2226f09530012d0e5fda4cd1b94ee9e.
  Parent read full source and fresh verify31491 EXIT0. Primary536calls comprise
  correspondence representation24/rotation32 plus SST-2 transfer480; optional
  mixed-SFT free/schema64 control64 is now READY and is bound once at suite startup.
  Four fixed original/old/A/B weights, two owned services, no test-based selection,
 2hcap. Do not manually launch another suite while this waiter is live.
- **PREPARING NEXT:** B-only fresh HF template replay12, six exact64 contexts×
  saved probe vs saved training-template IDs, same fixed B checkpoint,15mincap.
  This isolates a known tool-key serialization difference, not an assumed cause.
- **PREPARING:** six shared-prefix MRCR terminal pairs, explicit computed-string
  commitment versus one generative restatement.20-minute cap. Core already has
  FINAL_TEXT; this is an additive research nano transport experiment, not a new
  core final API. No core/sealed source changes; rootless execution only.

Root-only pilot optimizer COMPLETE: one real full-batch AdamW/TIS step,16 episodes,
30 root turns,10500 credited tokens,23.866 trainingseconds, gradnorm.169678,
parameter deltaL2.147690. All distribution guards passed, child not trained.
Checkpoint SHA00ad756b609950f3873ae8c3e49ea917be1b207a369d1be7f95933eda78110c9.
Post validation8 COMPLETE:2/8 strict,314.920seconds, no outer budget censoring.
Three-way pilot audit is COMPLETE; initial2/8, unchanged replay4/8, updated2/8
is not evidence of a validated improvement. All8 first-root physical prompts match;
unchanged replay reproduces only2/8 first-root actions. Five depth1 overlength
errors are recovered within completed wrong episodes, not null outer failures.

Both greedy64 backend probes COMPLETE,0/6 valid arrays in each. Semantic messages
and tools match, but actual prompt token sequences differ in tool JSON key order;
this is NOT an exact backend-only comparison. A/B final64 evaluation uses the
same frozen HF prompt IDs as the HF baseline; training keeps prior-SFT serialization.

Operational gap: post validation ended around23:16:36; coordinator resumed23:33:36
and launched SFT23:34. The approximately17-minute loaded-but-unused GPU interval
is a real scheduling loss, not useful inference. B now has a launched automatic
waiter rather than only a written queue entry; the campaign also has a continuous
coordinator. These changes reduce dependence on a timely assistant resumption.

Completed root40:9/32 training successes,2/8 validation,2 training infrastructure
exceptions,970.519seconds collection;521 recorded calls/133907 completion tokens.
Export38 trainable episodes retains all40, null failures, only16 mixed-group episodes
selected. Manifestfe7e3a572a6e3166ec4142dc87a55e5217ac656693bbb4e8ac335f0c5639c12f.
Unchanged validation8 replay is COMPLETE:4/8 versus initial2/8,746.406seconds.
This is an actual no-weight-update fluctuation, not a training improvement.

New completed evidence (all exploratory, repeated source questions):

- Leaf SFT:128 steps,705.625 trainingseconds; strict355/489 ->473/489.
  Itemwise canonical374/489 ->473/489; only part of the strict gain is whole-array
  format repair. Selected by validation, one seed, public TREC, no general-reasoning claim.
- Role12:2/6 ->2/6. New composition48:4/24 ->6/24. Same root weights and forwarded
  first-request hashes, but first root actions differ before any child in3/6 and15/24
  pairs respectively. These pre-child differences cannot be caused by child weights;
  do not overinterpret small paired outcome differences as an isolated causal gain.
- Fixed batching/aggregation624: strict1/24 ->15/24; canonical1192/1536 ->1485/1536.
  Batch16/192 calls: strict4/24 ->15/24; canonical1068/1536 ->1466/1536.
  Trained batch16 uses86372 logical input tokens versus248804 at batch5, but has one
  whole-coordinate contract failure (batch5 none). No universal free accuracy gain.
- Native MRCR direct6: same six output strings, scores and per-case token counts as
  Chat direct6;2/6 exact, mean.3522015294. This small control reduces client-path
  concerns, not every harness difference. Initial converted attempt failed at a
  typed /models SDK probe before inference; additive typed-probe fix preserved it.
- All batch endpoints and their schema followups COMPLETE. Trained singleton gives
  strict5/24 without grammar and16/24 with exact-cardinality enum grammar (all24valid).
  Trained64 gives0/24 in both conditions; grammar fixes validity24/24 but only698/1536
  labels correct. Its first16 positions are374/384 correct, last16 only81/384;
 366/384 last-block predictions are entity versus80/384 gold entity. Actual input
  tokens contain all64 distinct questions in order and are only1321–1361 tokens,
  not an input-truncation failure. Full independent batch audit is complete/sealed.

Agents: current_literature finished controls and prepares B-only template replay;
leaf_sft_prepare analyzes campaign through first2updates/validation2 or STOP using
read-only watcher80837; storage_audit prepares computed-string commitment and
audits whether inherited nano retries explain wall costs (no live-source changes).
New literature/context-lens questions:
`ideas/2026-09-09-output-correspondence-and-context-lenses.md`.
Batch seal578c5f18... covers7056 actual requests; three-way root pilot audit completed.
Current research outputs remain external toGit; root main is clean/ahead5.
Earlier entries below are historical only, including every old running service.

**22:10 current override:** the full leaf SFT below is COMPLETE:128 steps,
705.625seconds accumulated training, selectedepoch2 by validation250/300 vs245/300.
Matched HF test355/489 ->473/489; valid arrays91/98 ->98/98. Whole-array validity is
part of this strict endpoint; separate semantic/format/alias analysis is underway.
This is supervised TREC child classification, not yet a full-RLM gain.

One GPU now belongs to dual-LoRA inference group1472413 on18601, run-dir
`sidecars/leaf-role-routing-v1/service-attempt-001`. Both aliases are actually loaded:
`strict-rlm-qwen3-4b-role-original-v1` and `strict-rlm-qwen3-4b-role-sft-selected-v1`.
Exact starting/selected FP32 disk adapters are served with normal auto/BF16 inference
casting. Actual inference.json and SERVER_READY.json resolve an early draft READY
description of float32 serving; the actual launched config is auto, not float32.

- **RUNNING:** role-isolated development12, tool session56260, launched22:07:51;
  `leaf-role-routing-v1/outputs/attempt-001`. Root is original in both arms; trusted
  invocation-depth routing changes children only. Actual aliases reconcile with ACP.
- **RUNNING:** new-composition48, tool session9977, launched22:08:14;
  `leaf-composition-transfer-v1/outputs/attempt-001`. Six64-record documents,384 TREC
  test questions, two counts per document and two pairedseeds. These are new context
  compositions of the component-test source, not a new untouched question source.
- **READY / binding amendment:** native no-tools MRCR direct6 to separate client
  effects from decomposition. Its original spec expects unconverted broadcast bytes;
  an additive variant authenticates the exactly equal504-tensor PEFT conversion now
  served by the original alias. No weight substitution or silent identity relaxation.
- **PREPARING:** fixed-leaf-composition-v1,624 leafcalls: same48 coordinates, fixed
  five-question batches and Python aggregation, no root model. This tests whether the
  learned child enables reliable aggregation when root parsing/combining is removed.
- **NEXT RESEARCH:** root-only RLVR with the selected child held fixed, on new source-
  training contexts. Need actual native mixed-role token/role capture, root-only
  credit and fresh mixed-reward groups. No constraints/grammar and no fabricated
  old probabilities. Do not apply the old all-action exporter to mixed policy data.

The entries immediately below preserve21:46 historical status, not live jobs.

- **RUNNING:** `trec-leaf-sft-v1/outputs/attempt-001`, tool session14102, launched
  21:45:19 UTC. One owned A100, BF16 Qwen3-4B plus exact original FP32 rank8 LoRA.
  Two supervised epochs, 5065 normalized training groups, 128 optimizer steps,
  assistant-only loss, 60-minute accumulated training-time cap (evaluation and
  checkpoint-write time additional). Baseline/epoch validation and selected test
  evaluation are part of this coordinator. Checkpoint every16 steps and each epoch,
  including optimizer/RNG/cursor. Frozen prepared identity35ad159cd2eb4c2540227a6383037167103fa55f63020e01f57598921dcb59d0.
  Read READY.json for explicit resume; never relaunch a completed attempt.
- **PREPARING NEXT:** role-specific serving comparison: frozen original root with
  original versus selected-SFT child, using the same explicit classification contract.
  Measure record accuracy, coverage, aggregation, final answer, and cost separately.
  Freeze new task composition/paired seeds before outcomes. Establish actual model
  routing; changing an alias before Prime's global interceptor is insufficient.
- **PREPARING NEXT:** explicit result-submission versus textual copying in MRCR.
  Six-document pilot shows retrieval/copying failures; direct full-context control is
  now complete. Any submission intervention must be declared as an actual tool, not
  a post-hoc answer-file fallback. Keep short-context results separate from scaling.
- **COMPLETED:** 8B calibration12 and fresh training24; no optimizer update because
  all task groups have invariant rewards across four seeds. Root's two actions are
  identical in all36 episodes; near-saturated sampled probabilities, not measured
  full entropy. One recurring worker-label error accounts for the four failures.
- **COMPLETED:** leaf72 factorial and clean-group validation720. On 300 validation
  questions, three repeated seeds, canonical correct predictions are183/900 baseline,
  388/900 definitions,343/900 schema,410/900 both. These are300 independent groups,
  not900; shared five-question batches and imbalanced TREC subtypes matter. Alias-
  normalization sensitivity is separately reported; no generic reasoning claim.
- **COMPLETED:** full-RLM definitions12, all12 recorded, no budget censoring;
  `recursive-label-definitions-v1/outputs/attempt-001`, 254.57seconds. Agent audit
  pending; prompt changes are visible to root and children, not leaf-isolated.
- **COMPLETED:** MRCR rootless12: exact0/6 both vanilla/sketch; direct full-context6:
  exact2/6. Distinct client/harness paths and six short cached documents make this
  an exploratory whole-system comparison. Native client token accounting corrected
  additively in analyses; frozen raw outputs remain unchanged.
- **COMPLETED:** original/SFT/RLVR example12 each; all hint56 replays; nativeTrain
  recursive12. Primary heldout is2/14 for all three weights, all paired outcomes tied.
  Recursive training capture has159 sampled turns/12423 action tokens and132 child
  calls+returns. Its only mixed-reward group's positive contradicts its Python aggregate;
  do not immediately reinforce that group as if terminal success proved a sound process.
  Child canonical-label accuracy is274/712 repeated assignments (38.5%); an explicitly
  separate alias-normalization sensitivity is465/712 (65.3%). These are not712 unique
  independent records. See `recursive-train-capture-v1/analyses/attempt-002/REPORT.md`.

All inference clients ended before owned original4B service group1430616 was stopped
at21:44–45 UTC. The GPU belongs exclusively to SFT session14102 now. Earlier 8B service
group1417571 and RLVR4B group1313187 are also stopped. Do not use their stale endpoints.
Keep analysis and the two follow-on preparations concurrent with training.

Everything below this paragraph preserves older queue decisions as historical context;
its ready/running labels do not override this current status.

## Current allocation and reassessment (supersedes the historical status below)

One A100 40 GB is allocated on an21, Slurm job 5771, visible as
`MIG-43a3375a-1942-592d-accf-d0884164dcb8`. The user is away and authorizes autonomous
research for this approximately 24-hour allocation. Save questions rather than blocking.
Home-cache migration is explicitly deferred: home now has a 1 TiB quota. New outputs and
cache growth should remain under `/project/alex_phd`.

1. **Completed: paired evaluation/training-client qualification on Qwen3-4B.** The old
   two-GPU sweep was never runnable as sealed: its plan digest drifted and the new qualification
   stage was not wired. Use a new one-endpoint 48-call design (four tasks, three temperatures,
   two seeds, both clients). Preserve raw token/structured-action differences, strict answer
   correctness, costs, and execution errors. New service logs are in
   `operations/2026-09-08-resume/`. Server startup attempt 001 found that the prepared config's
   API-key string is incompatible with vLLM 0.28, which expects a list; attempt 002 fixes only
   that field and the output location. The rootless image was rebuilt on this allocation and
   its new identity must be recorded rather than equated with the old ephemeral image.
   The baseline48 and native-prefill48 episodes are now complete. Baseline Train executed
   Python0/24 and was strict-correct0/24; corrected Train executed Python16/24 and was
   strict-correct3/24. Eval executed Python18/24 and was strict-correct2/24 in each run.
   The generic renderer's empty thinking prefill was absent from the actual nonthinking model
   template. Removing it restored tool use and produced mixed reward groups, with no weight
   changes. Initial and multiturn prompt-token parity checks passed. These are interface
   correction results, not evidence of reinforcement-learning improvement.
2. **Completed: fresh Qwen3-4B RLM rollouts and pre-update evaluation.** Training40 uses
   ten task IDs disjoint from qualification, four fresh samples each, temperature0.5, and
   excludes two answer-revealing training tasks. Heldout16 is frozen on a separate context
   group; the primary analysis excludes known answer-revealing ID12000052 (14 episodes),
   with the full16 as a historical-comparability secondary result. These are historically
   inspected contexts and exploratory evaluation, not pristine confirmation. The next GPU
   optimization will use these working 4B traces before switching models. All40 traces are
   captured, with6 strict successes. Four mixed groups provide16 episodes/32 turns/6454 action
   tokens for RLVR; all40 records remain sealed. Primary heldout-before is2/14 correct.
3. **Ready: single-GPU RLM RLVR.** Sequential old-policy rollouts, a real
   action-masked LoRA update, and paired heldout evaluation using the existing adaptive 8B
   checkpoint. Keep any nonempty correctly aligned controller trace eligible regardless of
   decomposition shape. Observable wrong/malformed policy outputs receive strict reward zero;
   missing traces and infrastructure errors remain excluded. Calibration, update data, and
   heldout tasks must be distinct. Checkpoint every episode and optimizer step. The generic
   trainer now supports the frozen4B model/step0 adapter and group temperature0.5 as well.
   The 8B attempt is CPU-prepared with15 tests and a rootless import probe passed; no8B GPU
   work has started in this allocation.
4. **Completed: supplied-procedure versus minimal-task-prompt comparison.** A56-episode
   frozen4B evaluation uses14 tasks across development/source-heldout contexts, two prompt
   conditions and two paired seeds. Both retain generic tool/recursion system guidance.
   This tests the benefit of task-level procedural support, not universally free planning.
   Replay identical coordinates after learning for an exploratory weight-by-hint comparison.
   Source image-ID prefix mismatch was corrected in an additive spec before any episodes.
   Development: minimal6/14 correct versus procedure1/14; procedure output tokens4.61x higher.
   No actual recursion was observed. A12-episode development followup adds a compact, executable
   recursive-call example to the same procedure to test whether API demonstrations provide
   action headroom that verbal instructions do not. No heldout tuning is involved.
5. **Preparing: self-SFT control on the same fresh4B dataset.** Train only verified successful
   actions, masking all environment/context tokens, from the same initial adapter as RLVR.
   One epoch, at most8 gradient-accumulation steps covering every successful episode, LR2e-5,
   checkpoint each step. Record actual training
   tokens/steps; do not claim this initial control is compute-matched with a one-step RL update.

### Immediate adaptation after the first GPU optimizer attempt

The first4B RLVR trainer ran its forward/backward pass but stopped BEFORE optimizer.step on
the inherited maximum logprob-drift gate. No weight update is claimed. Across6454 actions,
mean absolute drift is0.00747; only8 exceed0.5, maximum1.0103. A real GPU precision comparison
showed that matching the inference FP32 output projection does not remove this sparse tail.
BF16 policy ratios span0.3641 to1.8591, mean1.00050;71/6454 lie outside the PPO clip interval;
the sampled k3 divergence estimate is0.000975. Do not spend hours demanding bitwise backend
agreement or silently increase the old gate.

Two independent adapter compatibility errors are being corrected additively: Prime broadcast
keys lack PEFT's expected prefix, and its FP32 LoRA tensors need FP32 adapter loading to
preserve their values. All original B matrices are zero, so the original rollout function was
the base model; missing-key fallback nevertheless fails the intended starting-A identity.

Both updates are now completed: self-SFT6 steps/2863 action tokens; token-TIS RLVR1 step/6454
action tokens. The latter has finite gradient0.09782, parameter deltaL2 .01471, exact loaded
adapter tensors and all distribution guards passing. Cap2 clips no observed token weights.
Primary14 evaluation is2/14 for all three weight snapshots, with all paired outcomes unchanged.
Do not describe secondary fluctuations on the answer-revealing task as a semantic learning gain.

Current GPU jobs: RLVR hint56 and executable-example12 comparisons. SFT hint56 is complete:
development minimal3/14 versus procedure4/14, compared with baseline6/14 versus1/14. This mixed
interaction includes deterioration, not a clean overall gain. SFT example12 is complete:
abstract4/6 correct and0/6 recursive; example5/6 and3/6 recursive,64 actual child calls. Root
programs adapt batch sizes after errors but sometimes misclassify records or default unknown labels.

Immediate followons: fresh12 native-Train recursive trajectories on the current RLVR weights
(CPU preparation), frozen-step0 replay of the same example12 (ready), then the amended READY
single-gpu-rlvr-8b-v3 sequential90-minute experiment. The new MRCR rootless sketch comparison is
being prepared on six independent documents, not treating its82 related questions as82 documents.
Official TREC source labels now uniquely match all89 training-context records, enabling a direct
audit of intermediate classification without reading heldout outcomes for training selection.

The six positive4B programs inspect the full context but use crude keyword/default-category
heuristics. Two successes even count label-list headers rather than correctly classify records.
Do not change the predeclared SFT selection after seeing this; interpret it as outcome-supervised
self-imitation. Queue counterfactual task variants that break these shortcuts and separate
record-level semantic accuracy, aggregation accuracy, and actual recursive-call behavior.

### Corrections to earlier interpretation

- The hard-curriculum terminal audit is complete: 18 retained completions all have structurally
  trainable token traces, despite the old shape gate rejecting every one. Sixteen malformed or
  wrong-schema outputs are legitimate observable zero-reward policy examples. None of the 18
  answers is correct. The 102 discarded exception rows cannot supply missing token/terminal
  evidence, so they are not retroactively converted into training examples.
- The direct-policy strict audit is complete: heldout exact correctness is 1/8 before and after
  four actual optimizer updates. The official 2/8 values each include a gold-mention truncation.
  Reward contamination did not occur in the four reconstructed admitted update batches. We
  have no demonstrated heldout improvement from this direct RL run and no completed RLM RL
  optimizer update yet.
- Prefix-cache attempt 007 is interrupted, with 123/320 rows and no final terminal record. It
  is not a completed crossover. All five available cache-off concurrent sentinel cells vary,
  so prefix caching is not necessary for the observed drift. The full cache effect remains
  unestimated, and this is lower priority than learning/decomposition experiments.
- Strong routine-following SFT results do not establish adaptive plan discovery. Generic
  model/harness co-adaptation is already studied in recent literature; our next claim must name
  a concrete intervention and heldout transfer comparison.

Detailed reassessments: `ideas/2026-09-08-evidence-reassessment.md` and
`ideas/2026-09-08-literature-reassessment.md`. The following sections preserve the prior
September 2 queue as historical context; their running/ready labels are no longer live.

## Running / launching

1. **Prefix-cache crossover attempt 007 is live on both GPUs.** GPU0 is the cache-on arm at port
   8441 and GPU1 is the cache-off arm at port 8442; every scientific response is checkpointed.
   The preceding 29-row thinking-enabled attempt 006 is retained only as a zero-admission diagnostic.
   A distinct strict/rootless TrainClient temperature-adherence calibration and the controlled RLVR
   boundary factorial are sealing in parallel. MRCR v1 remains blocked because its current executor
   would run untrusted generated Python on the host.

## Latest completed results

**Strict containerized Prime RLM pilot, 2026-09-02.** The full current-Prime systems path worked:
Qwen3-4B inference, LoRA broadcast, strict task-aware scoring, and per-episode rootless containers.
The frozen step-0 evaluation at temperature zero was strict-correct on 0/8, but 7/8 outputs used
Python and 7/8 had the required terminal schema. All 32 temperature-one training outputs instead
ended after one turn, used neither Python nor recursive calls, and were terminal-invalid. The seven
complete four-member strict-reward groups were all `[0,0,0,0]`; two partial groups were also all
zero. The predeclared constant-group gate stopped the run with no admitted batch or optimizer step.
All 40 records and exact hashes are sealed, and GPU, port, process, and container cleanup passed.

- **Scorer warning.** Four strict-invalid training outputs received positive official reward. This
  independently confirms that the old scorer can reward text that never supplies the required final
  answer; the official-reward smoke should not be used for training or as a utilization filler.
- **Decision changed.** Do not interpret the failed update only as a task-difficulty floor. The sharp
  phase change in Python use and terminal validity initially made sampling policy plausible, but a
  client-path audit exposed a stronger confound. Eval recorded structured tool calls in 7/8 outputs;
  train recorded none, while 23/32 train outputs contained intended-looking `ipython` calls serialized
  as ordinary assistant text. Hold the exact TrainClient/Qwen3-renderer/custom-inference path fixed
  before mapping temperature or selecting an RLVR coordinate.
- **New questions.** Is the transition gradual or cliff-like? Does moderate temperature produce
  mixed strict reward without destroying environment use? Why did TrainClient/Qwen3 rendering leave
  tool-like JSON in assistant content? Does the same path preserve structured calls at temperature
  zero, or is this a renderer/derenderer contract failure independent of sampling?
- **Ranked follow-up.** Use the exact training client, Qwen3 renderer, custom inference endpoint, and
  request contract on two frozen replicas; counterbalance repeated groups at temperatures 0, 0.2,
  0.5, 0.8, and 1.0. Record both intended-looking text calls and actually structured/executed calls,
  then validity, correctness, disagreement, errors, turns, and tokens. Require tool-call preservation
  and at least two genuinely mixed strict groups before spending an optimizer step.

**Current-Prime direct OOLONG RLVR baseline, 2026-09-02.** After isolating three hidden runtime
assumptions (CUDA/cache paths, Verifiers' home cache, and unconditional home-local `uv` installation),
the Qwen3-4B direct-text control completed four genuine LoRA optimizer steps. All 72 train traces and
16 heldout traces were valid, every update had finite loss and nonzero gradient norm, checkpoints and
weight broadcasts completed, and the run exited cleanly. Official heldout reward was unchanged at
2/8 before and after four steps. This is a direct-policy reference and systems proof, not an RLM arm.

- **Reward-validity warning.** The pinned official OOLONG-synth scorer gives full credit for a
  non-comparison gold string appearing anywhere in the response. At least one nominal heldout success
  was a 2,048-token truncated enumeration that mentioned the gold label but never produced the
  required final answer. A strict task-aware final-answer audit of all 88 traces is active. Report the
  2/8 values only as official reward until that audit finishes.
- **Decision changed.** Do not extend the 25-step direct arm: the four-step run answered the systems
  question, showed no official heldout gain, and exposed a potentially exploitable reward. Prioritize
  the harder exact-terminal curriculum and redesign OOLONG RLVR scoring so formatting and terminal
  answer extraction are tested independently of explanatory text.
- **New questions.** How often does the official scorer disagree with strict final-answer validity?
  Which admitted groups received advantages from substring or truncation artifacts? Does training
  against strict terminal parsing reduce verbose 2,048-token failures and improve real exact answers,
  or merely make output shorter? How much of prior OOLONG RLVR signal is robust to rescoring?
- **Ranked follow-up.** Finish the frozen trace audit, then rerun a small matched official-versus-strict
  reward comparison only if disagreement materially changes admitted batches. Keep the exact same
  traces/tasks/seed and treat invalid or missing final answers explicitly rather than as implicit
  negatives during calibration.

**First action-masked RLVR calibration, 2026-09-02.** Attempt 001 exposed a launch-contract mismatch:
vLLM decoded logprob tokens to strings while the trainer correctly required exact token IDs. It was
bounded after 12 invalid episodes and before training. A TDD-tested server flag fixed the source
contract; a live probe then proved raw action IDs and logprob IDs aligned exactly. Attempt 002
completed all 72 planned calibration episodes: 66 were valid and all 66 received exact reward one;
four exceeded the turn limit and two hit the absolute timeout. Because no valid coordinate had mixed
rewards, the sealed stop rule correctly performed zero optimizer steps.

- **Decision changed.** The masked-loss and exact-token data path is now operational, but these four
  tasks are too easy for group-relative RLVR. Invalid executions remain invalid; they must not be
  relabeled as reward-zero examples merely to manufacture gradient.
- **New questions.** Which task/context/turn-budget coordinates put the same policy in the 20--80%
  valid exact-success range? Is difficulty best increased by answer reasoning, context size,
  composition depth, or a smaller action budget while keeping the verifier unchanged?
- **Ranked follow-up.** Use a broader, cheaper rollout-only difficulty screen across held-out task
  seeds and context lengths, then freeze several genuinely mixed coordinates before rerunning the
  one-step masked update. In the meantime the independent Prime smoke is using both GPUs.

**Controlled base-model replay, 2026-09-02.** All 416 sealed calls completed successfully across 13
exact historical prompts, two GPUs, sequential and width-eight serving, and eight repeats per cell.
The selected prompts were deliberately stratified around stable and variable cases, so the study is
a mechanism probe rather than a prevalence estimate.

- **Result.** Ten of 52 prompt/GPU/mode conditions varied within the run, including sequential
  conditions, and four other conditions were internally stable but differed from the selected
  historical response. All 13 prompts had the same cross-GPU modal map in each serving mode, while
  sequential and concurrent modes disagreed modally on one prompt per GPU. Every observed map was an
  already-seen historical variant. Differences were localized to one or two borderline records and
  clustered by semantic label (`definition`, `reason`, `time`, `agent`, or `quantity`), rather than
  representing wholesale alternate solutions. All 416 calls still produced the exact originating
  aggregate-task answer. Seven concurrent conditions varied at an identical reported warm-cache
  token count, so cache count alone cannot explain the drift.
- **Decision changed.** Do not attribute a temperature-zero leaf difference to an adapter or training
  checkpoint without replicated, counterbalanced serving controls. At the same time, do not treat
  every leaf-map difference as reward-impacting instability: report semantic trace variation and
  terminal task variation separately. Terminal-answer RLVR remains the immediate priority because it
  does not arbitrarily penalize verified, functionally equivalent traces.
- **New questions.** Which part of the serving state causes the two historical variants: prefix-cache
  contents, dynamic batching width/order, fresh-versus-warm model state, or a lower-level numerical
  path? Does this localized leaf variation ever cross a task's decision boundary on a representative,
  unselected workload? Would training on a portfolio of verified equivalent traces improve transfer
  compared with imitating one arbitrary trace?
- **Ranked follow-up.** After the running RLVR pilot, run a compact factorial on the variable sentinel
  prompts: prefix caching on/off, fresh/warm server, and sequential versus batch widths two, four, and
  eight. Repeat enough times to estimate variant frequencies and include downstream tasks whose
  answers depend on the changed label. This isolates mechanism without delaying the higher-value real
  policy update now in flight.

Full machine-readable results and per-record Hamming/transition audits live under
`exploratory/controlled-replay-20260902/artifacts/`.

## Ready next

1. **Strict RLM TrainClient temperature/adherence calibration.** Freeze the existing SFT controller
   and step-0 adapter, then sweep temperatures 0, 0.2, 0.5, 0.8, and 1.0 through the exact training
   client/renderer/custom-inference path and safe rootless harness. This first tests whether that path
   preserves structured tool calls and then locates a mixed strict-reward coordinate without risking
   a meaningless update.
2. **Controlled RLVR boundary factorial.** Separate record count, ontology size, and execution budget
   near the validity cliff: 64/80/96 records, matched-coarse versus fine labels, and 4-turn/1-subcall
   versus 6-turn/2-subcall. Preserve `trace_trainable`, `terminal_valid`, and `terminal_correct` as
   separate fields.
3. **ReTool-style RLM RLVR and first real update.** Begin from the existing SFT controller, interleave
   generated Python with live workspace observations, mask environment tokens from the policy loss,
   and reward the exact final answer. Select tasks on which grouped rollouts have roughly 20--80%
   success, then perform a checkpointed LoRA update and compare held-out behavior before/after. This
   directly adapts the outcome-driven tool-use recipe in [ReTool](https://arxiv.org/abs/2504.11536),
   [Search-R1](https://arxiv.org/abs/2503.09516), and
   [VerlTool](https://arxiv.org/abs/2509.01055) to the RLM workspace.
4. **Fast three-route qualification and RLVR difficulty map.** Use the newly generated inline and
   bucketed 8K/16K/32K contexts to compare Python-only, filter-then-classify, and whole-context
   behavior. Start with a balanced mini-qualification instead of waiting for the full production
   workflow. Repeat stochastic rollouts on boundary tasks to locate 20--80% success coordinates and
   feed them directly into the RLVR pilot.
5. **Uncertainty-guided RLM program search.** Generate several candidate ways to inspect and decompose
   one context, then select using self-consistency, trace length, and confidence under a fixed call
   budget. Compare direct, ordinary recursive RLM, and reflective program selection across context
   length and task type. This follows the new challenge posed by
   [SRLM](https://arxiv.org/abs/2603.15653): recursion may be less important than selecting the right
   context-interaction program.
6. **RLM harness ablation tournament.** Compare the current workspace with small additions: a context
   profiler/map, typed delegation, parallel batch calls, and explicit budget feedback. Hold weights
   fixed first; evaluate paired correctness, trace validity, calls, tokens, and latency.
7. **Matched bootstrap SFT.** From one base checkpoint, train one adapter on verified direct solutions
   and another on verified RLM trajectories with matched tasks and token budget; evaluate both models
   directly and inside the same frozen RLM.
8. **Adaptive diagnose-then-edit harness on typed ODE search.** Reuse the exact evaluator and paired
   A5 search seeds in `evolved-integrators`, but route duplicate streaks and infeasible proposals
   through a typed diagnostic subcall before emitting the next candidate. Run one Qwen3-14B arm per
   A100 under matched calls/tokens/wall time. The primary test is whether the adaptive harness lowers
   the observed 60% duplicate share while preserving or improving feasible unique candidates and
   held-out search quality. Five paired replicates are estimated at 2.5--4 hours and provide a fast,
   substantive harness-modification study independent of model training.
9. **GEPA versus frozen and random/local harness search.** Optimize the existing exact-verifier
   three-route harness with GEPA and compare against the frozen seed plus an equal metric-call-budget
   deterministic mutation arm. Keep train/development/confirmatory groups disjoint and report exact
   score, invalidity, token/call/time cost, and train--development gap. The adapter-only sidecar is
   being prepared now; it must refuse research launch until the authenticated 108-task corpus and
   production verifier/runner contract from the three-route workflow exist.

## Near-term studies requiring a small implementation step

1. **Verified local certificates for structured decomposition.** Extend each decomposition worker in
   `structured-decomposition-benchmark` to return a locally checkable state trace, screen certificate
   precision and coverage first, and only then test verify-and-bind synthesis against answer-only,
   advisory, unconditional-binding, compute-matched direct, and exact-report-oracle controls. This is
   the highest-priority scientific bottleneck exposed by that repository: earlier workers sometimes
   produced wrong reports, while synthesis could use correct reports when forced to bind them. The
   first report-only screen needs a new frozen checker/protocol and likely Qwen3-32B tensor-parallel
   across both A100s.
2. **Context lens by decomposition headroom.** With a smaller Qwen3-14B model, cross local-shard versus
   full-root worker context with fixed three-way decomposition versus compute-matched repeated direct
   calls. This asks whether scope restriction itself helps or whether apparent decomposition value is
   merely extra inference compute. Calibrate away from floor/ceiling before the paired study.
3. **Harness--weight co-adaptation crossover on verified ODE traces.** If diagnose-then-edit produces
   enough diverse successful traces, train matched LoRAs on whole-candidate versus diagnostic traces,
   then cross all checkpoints with one-shot versus adaptive harnesses. The interaction, rather than
   the best cell, tests whether model and harness adaptation complement or substitute for each other.
4. **Reproduce, then extend, RLM length-generalizing RLVR.** The original
   [RLM v3](https://arxiv.org/abs/2512.24601v3) reports RLVR of Qwen3-4B on MRCRv2 32K--64K contexts
   with two needles and evaluation at 512K--1M with eight needles. First reproduce the direction of
   that result at a reduced but nontrivial scale on our two A100s. Then run matched arms using the
   free-form Python harness versus an explicit context-profile/belief-state harness. This turns a
   reproduction into a test of whether a small RLM affordance improves sample efficiency and
   compositional length/needle transfer. Keep the external context beyond the neural window in both
   arms; otherwise this is only long-context fine-tuning, not RLM learning.
5. **TimeRLM anomaly harness transfer.** Use the official deterministic AnomalyXL generators and
   continuous verifiers as an independent domain for RLM adaptation. First cross the same Qwen3.5-4B
   weights with its file-backed/plot-aware harness versus a matched plain Python harness; only then
   run short RLVR. This tests whether structured observations and visible turn budgets transfer
   beyond synthetic text aggregation without depending on the three-route corpus.
6. **Audit tree credit before SkyRL reuse.** Released SkyRL code flattens parent and child trajectories,
   but the inspected child environment assigns zero reward and no explicit parent-advantage rewrite
   was found. Add a regression test that proves the intended credit tensor reaches every descendant
   before treating the reported parent-to-child credit rule as implemented or using it as a baseline.

## High-value questions from the 2026-09-02 literature scan

1. **Does an RLM exhibit harness annealing?** Adapt the Belief/Progress/Experience state and cost-aware
   GRPO design from [EvoHarness-RL](https://arxiv.org/abs/2608.05446) to long-context decomposition.
   Measure whether training first increases effective workspace use and then internalizes repeated
   routines, reducing calls while preserving or improving correctness. The published work already uses
   Qwen3-8B, making this unusually actionable on our hardware.
2. **Harness evolution, weight RL, or both?** Run a matched 2-by-2 pilot: static versus reflectively
   evolved RLM harness, crossed with frozen versus RLVR-updated LoRA weights. Use the same rollout
   budget and held-out tasks. The interaction directly tests whether harness and weights complement,
   substitute for, or interfere with each other. Use
   [GEPA](https://arxiv.org/abs/2507.19457) for reflective prompt evolution and cost-aware GRPO for
   weights.
3. **Can the model create useful harness updates and can it use them?** Measure these separately, as
   recommended by [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621). A
   capable external evolver may write a strong decomposition playbook that Qwen3-8B nevertheless fails
   to invoke or follow; SFT/RLVR can then target invocation and adherence specifically.
4. **Is recursion the mechanism, or is program selection the mechanism?** Compare ordinary RLM,
   non-recursive candidate program search, uncertainty-guided selection, and typed combinators under
   equal call/time budgets. This connects [SRLM](https://arxiv.org/abs/2603.15653) and
   [Lambda-RLM](https://arxiv.org/abs/2603.20105) to our decomposition study.
5. **Is the best harness less useful than a diverse harness portfolio?** Generate many small,
   source-traceable harness variants and retain both the winner and complementary siblings that solve
   different examples. Compare SFT/RLVR data from the single winner with data from the matched
   portfolio. [HELIX](https://arxiv.org/abs/2608.13951) reports that complementary harnesses expose
   substantially more verified coverage than the best fixed harness; RLM decomposition gives us a
   clean setting in which to test whether that diversity transfers into the weights.
6. **Can pairwise harness revision improve context flow before weight training?** Represent only the
   RLM agent loop and observation format as an editable prompt-level specification, revise it using
   pairwise trace feedback for a few rounds, and then freeze it. Compare the resulting traces and SFT
   data with those from the original harness. This adapts
   [Recursive Harness Self-Improvement](https://arxiv.org/abs/2607.15524), whose reported gains came
   mainly from better context management rather than longer reasoning.
7. **What should recurse: a model call or an entire small agent?** Under matched tokens and wall time,
   compare ordinary leaf calls with leaves that can inspect files, execute code, and return a typed
   result. [Recursive Agent Harnesses](https://arxiv.org/abs/2606.13643) reports a fixed-backbone gain
   from full-harness recursion; our smaller open-weight setting can test whether that extra agency is
   worth its cost and whether it yields better training traces.
8. **Can one policy learn when to solve and when to repair its own RLM harness?** Add a constrained
   `edit_harness` action beside ordinary task actions, permit edits only to prompt/observation/tool
   components with immutable external verification, and compare joint action-space RL against
   alternating external harness search plus weight updates. This directly adapts
   [HASE](https://arxiv.org/abs/2607.03935), which reports that a single Qwen3-8B policy can improve
   both task solutions and selected harness components. Our key ablations are whether edits transfer
   across tasks and whether gains survive resetting the weights or the harness.
9. **Does an explicit, checkable context belief improve RLM credit assignment?** After each Python or
   recursive observation, have the controller emit a compact typed state: established facts, relevant
   context regions, unresolved questions, predicted next observation, and remaining budget. Compare
   terminal-only RLVR with belief-consistency rewards and belief-state grouping, inspired by
   [ReBel](https://arxiv.org/abs/2605.20061). Unlike a free-form summary, later workspace observations
   can verify many stated predicates. Measure task success, sample efficiency, belief drift, calls,
   and whether the belief field merely adds tokens. This is a direct experimental version of the
   proposed context-sensitive interrogation competency.
10. **Can decomposition hints bootstrap strategy discovery and then disappear?** Small RLMs often
    need an explicit task strategy, but permanently supplying it answers the planning question for
    the model. After a small cold-start SFT, compare RLVR with a fixed detailed strategy, no strategy,
    and a curriculum that progressively masks or shortens the hints. Evaluate all checkpoints under a
    common minimal prompt on unseen task structures. This tests whether the model merely follows an
    example decomposition or internalizes a context-sensitive interrogation skill. The fixed-versus-
    short-prompt instability reported in
    [Reinforcing Recursive Language Models](https://www.alphaxiv.org/blog/reinforcement-learning-for-rlms)
    supplies both the baseline and the open mechanism question.

## Follow-on directions

- **Learn when *not* to recurse.** Give the controller a visible remaining-call/token budget and train
  an explicit `answer`, `inspect`, or `delegate` decision. Compare it with fixed recursion limits under
  matched total compute. The key outcome is a Pareto curve of answer quality versus model calls, not
  accuracy alone.
- **Information-gain context probes.** Add a cheap context-profile primitive (length, schema, sampled
  regions, keyword/entity counts) and let the controller propose the next query. Reward probes that
  reduce disagreement among candidate answers or plans. Ablate raw Python access versus the profiler
  to learn whether a small affordance makes adaptive decomposition easier to acquire.
- **Counterfactual value of each recursive call.** Replay successful traces after removing, replacing,
  or shuffling one subcall result at a time. Use the measured answer degradation as a subcall-value
  label, then test whether auxiliary value prediction improves credit assignment over terminal reward
  alone. This also distinguishes useful decomposition from decorative tool use. Treat restored-state
  replay fidelity and the precise causal contrast as part of the claim, following the cautions in the
  [2026 agentic credit-assignment review](https://arxiv.org/abs/2604.09459).
- **Who receives the terminal reward: root, leaves, or both?** Compare root-only RLVR with a shared
  parent/child policy in which each child inherits its root rollout's group-relative advantage and
  child losses are normalized by the number of children. This follows the operational recipe in
  [Reinforcing Recursive Language Models](https://www.alphaxiv.org/blog/reinforcement-learning-for-rlms),
  then tests a finer alternative using our counterfactual subcall-value labels. Hold rollout trees and
  total action tokens matched so extra child gradients are not mistaken for better credit assignment.
- **Role-specialized leaves.** Compare one shared leaf model with lightweight role adapters for
  `extract`, `solve`, `critic`, and `aggregate`, keeping total calls and trainable parameters matched.
  If specialization helps, test learned routing; if it does not, retire the added complexity.
- **Failure-driven curriculum.** Cluster failures by observable trace symptom (no inspection, invalid
  code, weak partition, missing evidence, bad aggregation, budget exhaustion), synthesize nearby
  verified tasks, and train on the highest-regret cluster. Re-evaluate old and new clusters after each
  short update to detect both improvement and regression.
- **Train on answers or on one arbitrary trace?** The controlled replay is provisionally finding
  multiple temperature-zero leaf assignment maps that differ on only one or two boundary records yet
  induce the same exact aggregate answer. Compare single-target trace SFT, SFT that samples among
  verified functionally equivalent traces, and terminal-answer RLVR. Measure final accuracy, leaf-map
  stability, calibration on ambiguous records, and transfer. If equivalent traces are common, exact
  trace imitation may punish valid decompositions and manufacture an unnecessary stability target.
- Co-adapt harness choices and LoRA weights in alternating rounds.
- Build a small typed combinator RLM (`inspect`, `filter`, `partition`, `map_model`, `reduce`,
  `verify`) and compare it with free-form Python. Then train the controller to choose combinators.
  [Lambda-RLM](https://arxiv.org/abs/2603.20105) reports that typed symbolic control can improve both
  accuracy and latency; our open question is whether typed control also makes SFT/RLVR substantially
  easier for an 8B controller.
- Search/evolve prompts, observation formats, tool affordances, and call-budget policies, with a held-out
  task split to measure harness overfitting. Use an archive-based search inspired by
  [Automated Design of Agentic Systems](https://arxiv.org/abs/2408.08435).
- Let successful and failed RLM traces build an incremental decomposition playbook, then compare it
  with a static system prompt and weight updates. This tests the generate-reflect-curate mechanism in
  [Agentic Context Engineering](https://arxiv.org/abs/2510.04618) inside an RLM.
- Test whether learned policies transfer to new task compositions in the structured-decomposition
  benchmark.
- Evaluate larger or newer open-weight models only when they answer a concrete capability or scaling
  question.

## Hard-curriculum validity cliff: terminal result (2026-09-02)

The earlier easy calibration arm (about 64 records, 6 labels, simple facet query) produced 66/66
valid and correct trajectories under the same four-turn/one-subcall execution budget. The complete
hard curriculum then produced 0/120 valid trajectories across 96/8, 128/10, 160/12, 192/12, and
224/14 record/label settings. There were 87 four-turn exhaustions, 14 absolute timeouts, one subcall
limit, and 18 wrong-shape completions; all rewards stayed null and the protocol correctly performed
zero optimizer steps. This is an execution-validity floor, not evidence that the model supplied 120
wrong answers. The two replicas processed 60 episodes each and had nearly identical turn-limit counts,
so a single broken endpoint is not the main explanation.

A posthoc answer-only rescore found two schema-valid but wrong answers among the 18 retained
wrong-shape completions (0 instead of 5, and 0 instead of 12); nine were malformed JSON and seven had
the wrong schema. The other 102 exception episodes retain no output. The predeclared `valid` field
therefore measured a stricter training contract, not just final-answer validity.

**Decision changed.** Retire monotone-harder calibration until the execution boundary is located. Do
not train on invalid trajectories and do not interpret the lack of an update as evidence against
RLVR. The current sweep changes records and ontology size together while holding the action budget
fixed, so it cannot distinguish semantic difficulty from insufficient room to finish the learned
routine.

**Ranked follow-up.** Execute the controlled design in
`sidecars/rlvr-boundary-factorial-v1/DESIGN.md` (SHA-256 prefix `076b3a37`). It crosses 64/80/96
records, matched-coarse versus fine ontology, and four-turn/one-subcall versus six-turn/two-subcall
budgets. Measure valid-final rate first and reward only conditional on validity. If the transition is
still too abrupt, add 72 and 88 records locally around the detected boundary. The result should reveal
whether context size, ontology resolution, or execution allowance creates the cliff and identify a
genuinely mixed coordinate for the next masked update. In the executable attempt schema, report
`trace_trainable`, `terminal_valid`, and `terminal_correct` separately; use only trainable traces for
the masked update, while preserving terminal-answer outcomes for capability analysis.

## Update rule

Every completed or failed run adds: its result, what decision changed, new questions, and a ranked next
experiment. Remove or reformulate directions that repeatedly yield no information. Keep at least two
decision-relevant jobs ready while accelerator access remains available.
