# Complete-success imitation and stopped RL7 both improve this paired readout

Final independent outcome audit, September9,2026. **Baseline solves5/24; complete-success SFT8 and last-saved RL7 each solve9/24.** SFT wins six baseline pairs and loses two; RL wins five and loses one. The two trained policies solve different cases: their direct comparison has four wins and four losses. This is a positive but small, exposed-context training-package result—not proof of equivalence, an objective-only effect, or broad planning generalization.

Both trained roots improve final-format validity and source-authenticated helper coverage. SFT uses approximately half as many physical calls as RL over all24 cases, but that large saving shrinks to27 versus29 calls on their five jointly correct cases. Neither training package is cheaper than baseline on its own jointly correct subset.

## What was compared

Frozen order: RL7→success-SFT8→baseline, with separate sequential services and common four-worker collection. All three policies use the same24 fresh-seed task coordinates, exact first native/physical prompts, sampling, typed child and local runtime. The24 coordinates are nested within eight already-exposed contexts, not24 independent source clusters or newly unseen test data.

| Policy | Actual checkpoint meaning | Adapter SHA256 |
|---|---|---|
| Baseline | Unchanged interface-SFT fixed final4 | `efab2913e7fe9f5f9b381ae6eb67bb56071070f86b237e6145f98654816aad64` |
| Success SFT | This study's fixed complete final8 | `66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5` |
| RL7 | Last saved after original no-mixed round8 STOP | `809fc46ed50d36c5e61b2e8ae785ae84083b509fcb8bdd3b1914eaca3c0c842a` |

RL7 is **not** the original RL study's prescribed final8 and was not selected by validation performance. Its old STOP remains intact. This new three-arm readout was fixed prospectively with seeds981308101–108/201–208/301–308. Both baseline contrasts are primary; SFT−RL is an exploratory, non-equal-compute package comparison. SFT's teacher data came from the same adaptive RL run, so these are not independent training histories.

All three retain fixed child `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`, with the unchanged source-matching typed batch contract. Root requests are unconstrained; child map grammar does not train or constrain the root's answer. Main sources: [READY](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-trajectory-sft-v1/READY.json"), [training RESULT](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-trajectory-sft-v1/outputs/attempt-001/training/RESULT.json"), [SELECTION](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-trajectory-sft-v1/outputs/attempt-001/training/SELECTION.json"), [TERMINAL](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-trajectory-sft-v1/outputs/attempt-001/TERMINAL.json").

## Primary endpoints and paired changes

| Metric /24 | Baseline | Success SFT8 | RL7 |
|---|---:|---:|---:|
| Strict correct | 5 | 9 | 9 |
| Strict final syntax | 10 | 18 | 23 |
| Completed protocol failures | 14 | 6 | 1 |
| Valid syntax but wrong number | 5 | 9 | 14 |
| Null / empty / unrun | 0/0/0 | 0/0/0 | 0/0/0 |
| Exact first HELPER copy /24 AST-valid first actions | 22 | 22 | 22 |
| Actual first helper requests exactly first4 IDs | 22 | 22 | 22 |
| Helper used | 24 | 24 | 24 |
| Requests beyond first4 | 15 | 22 | 23 |
| Complete relevant valid-map coverage | 15 | 21 | 23 |

SFT−baseline:6 wins,2 losses,16 ties; RL7−baseline:5 wins,1 loss,18 ties; SFT−RL7:4 wins,4 losses,16 ties. Every contrast has zero unknown pairs, so planned-denominator net bounds equal the observed net. Equal totals do not mean interchangeable behavior. Exact pair outcomes and artifact links are retained in [AUDIT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: AUDIT.json").

| Stratum, eight coordinates each | Baseline correct | SFT correct | RL7 correct |
|---|---:|---:|---:|
| Validation | 1 | 4 | 4 |
| Query transfer | 1 | 1 | 3 |
| Length transfer | 3 | 4 | 2 |

SFT's gains are not uniform transfer: query-transfer accuracy stays1/8 despite improved coverage. RL improves that stratum but loses one net length-transfer case. The full four-coordinate query-transfer-00 cluster is wrong for all three policies. Per-context tables and strict syntax/coverage counts are in [DETAILS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: DETAILS.json"). These small clustered subsets do not establish a reliable method ranking.

All72 raw endpoint reconstructions agree with the frozen scorer. Completed wrong/malformed replies remain zero; none was converted to an availability null or repaired. There are no episode/trace errors and no incomplete native graphs. Model-generated error observations inside a completed episode are retained separately: a descriptive error-string screen finds6 baseline,8 SFT and8 RL episodes with an error observation and later assistant continuation; respectively1,2 and4 end correct. This is not an exhaustive recovery detector or proof that the model corrected every observed error.

## Training was the specified eight-pass imitation package

Exactly27 confirmed successful **training-only** trajectories from adaptive rounds1–5 were included. They contain114 physical root actions,15,256 target tokens and87 child calls in their source graphs. All root actions—including initial helper calls and recovery steps—were preserved. No evaluation/later-round candidate, provisional success, scripted operator trace or duplicate-elimination change was introduced. Five teacher root weight identities are recorded in EXPECTED_INPUTS; teacher behavior is not all from the final RL checkpoint.

The independent audit reconstructed all27 native graphs and found the exact exported114 root input/label/mask/logprob sequences. Current depth0 action suffixes alone receive loss; child/tool/history/context tokens are masked. All114 native action ends already contain151645, with no appended terminator or retokenization. Old sampled probabilities remain provenance only, not the SFT loss. Training source groups320 and readout source groups512 have zero overlap under the frozen grouped partition; both remain exposed/public/helper-training-supported research data. [TEACHER_GRAPH_PROOF.json](../../../../ARTIFACTS.md#unpublished-files "Not published: TEACHER_GRAPH_PROOF.json").

SFT started exactly from baselineefab with fresh AdamW. Every update consumes all27 episodes/114 root turns/15,256 targets; all eight recorded shuffled orders match seed981308002+update_index. Total exposures are216 episodes,912 root turns and122,048 targets. Per-turn FP32 coefficient is `1/(27 × episode_root_turns × action_tokens)`: equal episode, then equal turn, then mean target-token CE. Executed coefficients, actual masses, weighted CE sums and all target counts reconcile.

All eight contiguous checkpoint states/member hashes authenticate with previous-state links, epoch=step, full-pass cursor0, and actual Adam cursors1…8. Adam recipe remains LR2e−5, weight_decay0, beta(.9,.999), eps1e−8, clip1. One invocation, no resume, no partial-pass substitution. Load audit reports exact504 adapter tensors/dtypes with no missing/unexpected keys; base is BF16 and trainable rank8 adapters FP32. Child is not loaded or updated by training. The audit checked saved artifacts and authenticated source/qualification, not a new GPU forward pass.

Weighted loss falls0.061086→0.052086 and token NLL0.086680→0.078168. Gradients remain finite/nonzero(0.84144 at1,0.07829 at8); delta from the single common load reaches0.392350. Final root actions have138 targets per pass: their CE sum falls1.267698→0.000023, whereas intermediate-root CE falls1305.90→1182.33. Initial taught helper actions remain in all27 trajectories. **These CE/coefficient contributions are not measured gradient shares**, and loss reduction does not identify why held-out answers changed.

Training records590.240seconds cumulative load/verification/training/checkpoint work, not an isolated pure optimizer clock. Peak allocated memory14,452,734,464bytes. The logged allocator warning at13:43:13 precedes checkpoint1; subsequent eight checkpoints, a single invocation and exit0 establish that it was not a fatal aborted-training event. The audit does not infer the allocator's exact internal recovery mechanism. [training log](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-trajectory-sft-v1/outputs/attempt-001/training.log").

## Native inputs and the remaining bottlenecks

All24 three-way first physical prefixes and sampling settings match. All881 physical model calls (462root/419child) return HTTP200, with native/wire prompt IDs, sampled IDs/logprobs, role aliases and checkpoint identities reconciled. No request-only tails or unknown usage/cache fields remain. Each of the419 typed helper calls returns a duplicate-free complete canonical map for its own requested IDs. Protocol validity is therefore not the remaining child bottleneck in this run.

Semantic label occurrences are717/764 baseline,1018/1076 SFT and1269/1332 RL. These are repeated, adaptively chosen occurrences, not paired independent classification accuracy samples. Different root subsets and repeated calls can change these numbers; the fixed child weights did not change.

Three concrete patterns constrain interpretation:

1. **Real strict-format gain:** at seed981308302 baseline has a correct visible-map count1 but returns surrounding prose; SFT returns exactly `Answer: 1`. RL instead returns `Answer: 18`. This SFT win need not imply better semantic classification. [Baseline episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-trajectory-sft-v1/outputs/attempt-001/baseline/rollout/episodes/b52cf8511d5a563f51a273d9bedc4e4630a15f9664ef1e325595b2a09f88d0a1.json").
2. **Correct map, wrong root count remains:** at seed981308207 SFT has a complete supported map implying6, matching gold, but says `Answer: 7`. RL has several similarly clear failures: seed981308103 map/gold0→answer7, and seeds301/302 map/gold1→answer18. [SFT episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-trajectory-sft-v1/outputs/attempt-001/success_sft/rollout/episodes/6807899dfacbfa1a58d81369a24d8fa43becb38fd4463b54e603e5a5d323b6d5.json"), [RL episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-trajectory-sft-v1/outputs/attempt-001/rl7/rollout/episodes/718acef8d2ac49606ef6dfb5f49a3eb9868730242c95cc72832799d9ae1eb90f.json").
3. **A stronger policy still regresses:** seed981308101 is correct for baseline and RL, while SFT stops with prose after the first4 records and has zero relevant-ID coverage. The gain is not monotonic per task. [SFT episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-trajectory-sft-v1/outputs/attempt-001/success_sft/rollout/episodes/8f942805805259ae0e5f79e9cffb91a1f49436992bb30b448cb98f4dc362f829.json").

The conservative final-branch map diagnostic recognizes complete unambiguous maps in5 baseline,4 SFT and7 RL episodes, with correct implied counts in3/4/5. It detects one SFT and six RL formatted answers disagreeing with those maps. Most episodes are diagnostically partial because they expose numeric outputs or other structures instead of a standalone full map; this is **not** lack-of-coverage proof or endpoint null. No decoder repair, regenerated map or sampled code execution was used. The unchanged22/24 first-helper-copy rate combined with higher subsequent coverage points to changes after initial uptake, but does not prove a particular planning mechanism.

## Cost: gains require more work than baseline

| Actual readout quantity | Baseline | SFT8 | RL7 |
|---|---:|---:|---:|
| Root / child calls | 99 /65 | 117 /124 | 246 /230 |
| Root input / output tokens | 161794 /12619 | 249425 /14743 | 691219 /26166 |
| Child input / output tokens | 68057 /7064 | 121340 /10013 | 210105 /12573 |
| Total cached / uncached input | 207664 /22187 | 343184 /27581 | 865344 /35980 |
| Collection seconds | 273.502 | 345.760 | 406.804 |

Against baseline, SFT uses1.47× calls/1.26× output and RL2.90× calls/1.97× output across the24 matched coordinates. Both also cost more on their jointly correct baseline subsets: SFT15 versus13 calls across three pairs; RL27 versus21 across four pairs. These subsets differ and must not be pooled.

SFT versus RL is241 versus476 calls and24756 versus38739 output tokens overall. On the five jointly correct pairs it is27 versus29 calls,3554 versus3665 output, and3450 versus3333 **uncached** input tokens. Thus the overall twofold call advantage is not a demonstrated twofold successful-task efficiency gain. It is a useful package-level cost signal to replicate, with substantial failure-path contribution.

Provider token/cache usage is not measured GPU FLOPs or unique inference work. The scientific launcher reports1769.137seconds overall(29.49minutes), complete/no error, all three collectors exit0, and all three ownership-release records confirm captured processes exited. Training plus collection clocks exclude/include different startup/verification components; summed parallel episode durations are not wall time. These facts were read from completed markers, not inferred by touching live GPU ownership. [FINAL_SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: FINAL_SOURCES.json") includes lifecycle evidence.

## What this changes

Complete-success imitation is more informative than simply reweighting the original32 microtasks: this package now has observed strict gains and increased relevant coverage. That is a cross-study research inference, **not** a controlled comparison between datasets/objectives: examples, updates, LR, target exposures and fresh readout seeds differ. The old row-mean negative result is not merged into this sample.

The next discriminating work should separate (a) completing output formatting/aggregation after correct native evidence from (b) obtaining semantically correct evidence and selecting the relevant subset. Preserve this fixed8 package; do not choose a new checkpoint from these outcomes. A replicated, source-disjoint readout would test stability of the9/24 gain; an explicitly new training-only transition ablation could test whether full successful trajectories or just faithful post-observation aggregation/answer transitions supply the gain. This report does not authorize those studies or admit these evaluation episodes into training.

Limits: one training seed, eight updates,27 success-selected training trajectories, exposed eight-context clusters, sequential phase order, shared child/teacher history, non-equal learning compute and no independent unfamiliar-domain root test. Both primary contrasts gain four correct, but discordant-pair counts remain small. No generic RLM generalization, algorithmic superiority, novelty or causal-objective claim is established.

## Reproducibility and independence

[METHOD.md](METHOD.md) and METHOD_READY were sealed before this auditor opened new training/readout outcomes. The auditor did not author the new SFT study or candidate selector, but did author shared original SFT/native components and knew prior results. All three new focused fixtures passed before outcomes. The sealed audit, full teacher-graph check and supplementary native-map/cost reconstruction exit0; no new parser correction was required. The inherited row-mean internal-request-ID correction was explicitly included before this study's method seal.

[AUDIT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: AUDIT.json") contains training states, per-coordinate strict outcomes/native checks and raw paths; [DETAILS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: DETAILS.json") contains paired costs, context tables, conservative diagnostics and loss-position accounting; [METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json") is the compact readout. FINAL_MANIFEST authenticates all analysis artifacts. The source inventory states exact consumed files without repeating large model hashes per call. No accepted outputs, masks, admission rules, endpoints or source files were changed.
