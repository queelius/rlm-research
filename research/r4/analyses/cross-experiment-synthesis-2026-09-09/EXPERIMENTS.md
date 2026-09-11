# Experiment catalog

This is a question-oriented catalog, not a complete listing of every smoke test. It inventories completed evidence from the run stores and neighboring projects through the source snapshot in [Sources](SOURCES.md). The old `rlm-research`, `rlm-research-r2`, `rlm-research-r3` and `rlm-v2-spikes` trees are historical archives; migrated adaptive-context reports and the reassessment link their provenance. Those archives were inventoried but not every raw attempt was independently reanalyzed. Qualification tests are not benchmark wins. Current queue labels can lag actual terminal markers.[^35][^36]

## Current 4B leaf and root studies

All percentages below preserve their stated denominator. “Strict items” may count every item in an invalid array wrong; “canonical items” checks recognized labels individually when alignment is available; “exact coordinate” requires the declared final task answer. Seed repeats of the same records are not additional independent data.

| ID / question | Data and experimental unit | Intervention / result | Actual compute and status | Evidence |
|---|---|---|---|---|
| E01 — Can the child learn TREC? | 5,065 train / 300 validation / 489 test normalized groups; 98 test arrays | Original→validation-selected all-five SFT: strict355→473/489; canonical374→473; alias376→473 | Complete, 128 steps, 705.625 training seconds; ~1,122s full observed run; one training seed, HF greedy batch2 | [1](SOURCES.md#s1) |
| E02 — Does the learned child help the full system? | One reused dev context:6 pairs; six new64-record contexts:24 pairs,384 unique test groups | Dev2→2/6; new composition4→6/24. Fixed5/Python aggregation1→15/24; fixed16 4→15/24 | All complete:12+48 RLM episodes;624 fixed5+192 fixed16 calls. Composition elapsed673s; fixed5 54s, fixed16 44s under different operational conditions | [2](SOURCES.md#s2) |
| E03 — Is long-output failure just formatting? | Same384 questions, repeated across two targets and two seeds;24 coords per arm | Schema64 repairs24/24 arrays but exact0/24; old SFT canonical698/1536. Schema1 repairs surplus labels; exact5→16/24 | Complete,7,056 audited calls including references; no new independent source records | [3](SOURCES.md#s3) |
| E04 — Do mixed record-exposure curricula generalize in length? | Same train/val/test groups as E01; six frozen64 contexts | A max32:small477/489,long0/6usable. B max64:476/489,long0/6usable; six closed short arrays | Complete. A206steps/1,151.455train seconds; B204/1,142.028. Both10,130record exposures, fixed epoch2, not compute matched to E01 | [4](SOURCES.md#s4) |
| E05 — Does one root-only increment help? | Four training contexts,32 training trajectories; two val contexts,four tasks×two seeds | One actual step; validation initial2/8,unchanged4/8,updated2/8 | Complete;10,500credited root tokens,23.866training seconds. No child training. Collection970.519s; validation walls differ strongly | [5](SOURCES.md#s5) |
| E06 — Do fresh persistent root updates improve orchestration? | Same four root-train contexts;32 fresh trajectories/round;fixed8 validation | Three updates;train12/32,13/32,12/32;val00 2/8,val02 3/8. Round04 terminal STOP | Terminal after~34.57min,126.114optimization seconds,48,620credited tokens. No update4, val4/6/8, selection/final or transfer | [6](SOURCES.md#s6),[7](SOURCES.md#s7) |
| E07 — Do definitions and grammar repair the child contract? | Reused89-record dev pilot72calls; independent300-group validation,three repeated seeds | Validation canonical183/900baseline,388defs,343schema,410both; valid arrays2/180,112,180,180 | Complete:72+720calls,~7s+59s warm elapsed. No weight updates | [12](SOURCES.md#s12),[13](SOURCES.md#s13) |
| E08 — Can prompts elicit executable recursion? | Three dev tasks×two seeds×two prompts×three weights; separate two-context plan-hint crossover | Concrete example elicits original recursion5/6; abstract hints yield0/168 across weights; final correctness does not certify labels | Complete; six-step self-SFT and a separate one-step TIS checkpoint are NOT the later child SFT or root pilot | [14](SOURCES.md#s14)–[16](SOURCES.md#s16) |
| E09 — Was the nonexecuting native path a capability limit? | Native Eval/Train client×temperatures0/.5/1×eight coords, baseline/prefill variants | Baseline Train0/24Python; native prefill16/24Python and some mixed rewards. Prompt/client correction materially changes behavior | Complete qualification, not a held-out model-learning gain | [10](SOURCES.md#s10) |
| E10 — Did direct RLVR improve strict OOLONG answers? | 88 traces across collection/readouts; eight heldout trajectories per endpoint | Four updates; official2/8→2/8,strict1/8→1/8. Fourteen official-exact truncated false positives in entire trace pool; none reconstructed in admitted batches | Complete retrospective reward audit; batch lineage reconstruction has stated limits | [8](SOURCES.md#s8) |
| E11 — Did previous rollout campaigns provide trainable variation? | Hard120episode run; separate8B calibration12+training24 | Hard exporter missed18completed policy failures;102incomplete remainnull. 8B all task groups homogeneous;zero actual update | Completed/failed collections are evidence about admission/headroom, not trained-policy outcomes | [9](SOURCES.md#s9),[11](SOURCES.md#s11) |

### Weight and policy identities

Recent E01–E07 use the cached Qwen3-4B-Instruct-2507 base revision `cdbee75f17c01a7cc42f958dc650907174af0554`, with exact starting converted LoRA and ordinary inference BF16 casting. Disk hashes are not a claim of bit-identical sampled probabilities across HF/vLLM or schedules.

| Name used in this dossier | Adapter SHA-256 | Selection status |
|---|---|---|
| Original converted4B | `857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6` | Fixed starting policy |
| Old five-item child SFT | `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3` | Epoch2 selected using validation before test |
| Mixed A child | `e822c841b78ac448c7860f5e3e7a7053cfce68c57f4a1d8f5584e1c728b35531` | Fixed final epoch2; no test selection |
| Mixed B child | `59ad854293142161f6b5e613dd5d1e3630fed600637106d5eae2cbcd764e9200` | Fixed final epoch2; no test selection |
| One-step root pilot | `00ad756b609950f3873ae8c3e49ea917be1b207a369d1be7f95933eda78110c9` | Exactly one increment from original; child stays old SFT |
| Last committed campaign root | `6cd68cb764ea1dc46f2e0adf1a5d692d53ebc12cd5e5ef9d9c6dbd7d949fffcb` | Step3, NOT validation-selected or final-evaluated |

## Earlier synthetic controllers and component studies

| ID / question | Data and unit | Result | Compute / status | Evidence |
|---|---|---|---|---|
| E12 — Can SFT teach adaptive input routing? |18unseen synthetic context groups;two question types;two optimization seeds;four rank16adapters |Plan following288/288each;visible144/144each;conditional134→144/144;leaf input−67.8%. Formal decisionmodify because visible gain gate unmet |Complete;19.85aggregateGPU-hours across qualification/training/screen/readout,11.11wallhours; not comparable to one recent4B run |[19](SOURCES.md#s19) |
| E13 — Can larger synthetic leaf batches work? |48fresh64-record contexts;paired batch sizes1/8/16/32/64;Qwen3-8B |Size64 item99.3%,wholepartition36/48;valid calls throughout |Complete component screen; no universal large-batch ceiling |[20](SOURCES.md#s20) |
| E14 — Does scope reduction preserve semantics? |48synthetic contexts;fullmap vs relevant-facet filter;unchanged6-waycontract |Conditional exact43→47/48;input−67.8%;opposite-GPU parsed agreement48/48 |Complete;leaf-only costs, no broad natural-document transfer |[21](SOURCES.md#s21) |
| E15 — Does target/other output simplify the task? |48synthetic contexts;binary vs genericmapping |Unfiltered6/48 vs40/48;filtered27/48 vs43/48 |Complete negative contract-change test |[22](SOURCES.md#s22) |
| E16 — Can agreement target useful verification? |48contexts,precollected batch32/64 and singletoncalls |Wholepartition35→43/48;50/57disagreements corrected;11mutually agreed wrong labels fail safeguard |Complete prospective offline policy replay;201consultedcalls,not online controller |[23](SOURCES.md#s23) |
| E17 — Does varied-layout SFT generalize? |Grouped dev readout,two optimization seeds,known renderer families |Positive interaction+15.3pp but canonical−30.6pp and more failures;nonmonotonic checkpoints |Complete exploratory readout; no untouched structural-OOD claim |[24](SOURCES.md#s24),[25](SOURCES.md#s25) |
| E18 — Can supervised bootstrap solve the small controller benchmark? |Qwen3-8B;development12,sealed12,fullsealed96 |Fullsealed direct3/96 vsSFT-controlledRLM96/96;exactly2reported modelcalls perRLM |Complete benchmark-specific SFT; supervised examples plus harness differ from direct baseline; not cleanselfSFT |[26](SOURCES.md#s26) |

## Other tasks and cross-project checks

| ID / question | Data and unit | Result | Compute / status | Evidence |
|---|---|---|---|---|
| E19 — Does short-document MRCR benefit from the current RLM? |Six reused public short MRCR docs,greedy |Direct2/6;vanillaRLM0/6;sketch0/6. Native direct reproduces all6Chatdirect outputs |Complete;direct6calls36,063input/1,904output;RLM14/13calls. Not a matched long-context scaling test |[17](SOURCES.md#s17),[18](SOURCES.md#s18) |
| E20 — Does binding wording make roots use reports? |SDB two open roots,ten saved report tuples,pairedadvisory/binding;Qwen3-32B |Adherence2→10/10,trueaccuracy3→7/10;binding follows threewrong-implied tuples incorrectly |Complete20calls,oneH20043.75min,no failures/retries;not population estimate |[28](SOURCES.md#s28) |
| E21 — Do natural reports and targeted revision help? |SDB five exposed roots,15naturalreports;then15revisionbranches |Natural direct2/5,advisory1/5,binding3/5. Revision repairs1/8wrong,damages4/7correct;zero wrong→correct impliedtuples |Complete40newcalls then45calls;H200~93.3min+86.1min;reused roots,not20or15independent problems |[29](SOURCES.md#s29),[30](SOURCES.md#s30) |
| E22 — Can program search find useful constrained changes? |EI ten A5replicates:five7B,five14B;deterministic train/heldout instances |65/474unique A5candidatesfeasible;712/1,186validproposalsduplicates. Small coefficient changes tradework/error;aggressivefamilymisses18vs12seed |Complete heldout diagnostics;OOD unopened. A4/A5 rawfeasibilityrates not randomized budget-matchedcausalcontrast |[31](SOURCES.md#s31) |
| E23 — Do identical serving requests give identical semantics? |Controlled416calls across52prompt/GPU/modeconditions |10/52conditionsshowsemanticvariation includinggreedysequential;aggregateanswersunchanged416/416 |Complete controlled replay; prefix-cache crossover incomplete,not identified cache effect |[32](SOURCES.md#s32) |
| E24 — Are failures artifacts of the research instrument? |Core fake-backend reproductions;separate actualnative304fileaudit |Core omission/lateusage bugs and nanoexport400classification are distinct;noactual3-stepoptimizerissueestablished |CPU audits,not model benchmarks; executed runtime boundaries maintained |[7](SOURCES.md#s7),[33](SOURCES.md#s33) |

## Latest completed controls, incorporated at the publication cutoff

The [leaf suite](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-post-sft-suite-v1/outputs/attempt-001") completed on 2026-09-09 at01:08:28, with488.199seconds suite wall time. This dossier reads its immutable aggregate files directly. A separate reviewer reports recomputation from all600raw calls and exact physical-prompt reconstruction; that audit was not yet published at this edition's cutoff, so no report hash is invented.

| ID / question | Unit and actual result | Status / source |
|---|---|---|
| E25 — Does explicit correspondence help? |Four reused TREC validation contexts,256groups,two seeds. Anonymous181/512,indexed405/512,echo419/512;all8/8valid;echo511/512exactcopies. Rotation preserves early-position advantage at allfour offsets |Complete24+32calls; [46](SOURCES.md#s46),[47](SOURCES.md#s47),[59](SOURCES.md#s59) |
| E26 — Does mixed-size training improve aligned64labels under schema? |Samefour validation contexts/two seeds;original135,old179,A219,B241/512. Allschema8/8valid;B lastquarter27/128 |Complete64calls acrossfourweights; [48](SOURCES.md#s48)–[51](SOURCES.md#s51) |
| E27 — Does the effect transfer to sentiment? |256SST-2publicvalidationgroups,fourcontexts,two seeds. Natural5correct462/459/470/470;schema64correct318/308/326/324 of512,original/old/A/B. Allschema8/8valid;full64correct0/8all |Complete480calls; [52](SOURCES.md#s52)–[57](SOURCES.md#s57) |
| E28 — Is B's short array explained by tool serialization? |Same six64contexts,fixedB;fresh training/probe template calls both0/6usable,no truncation. Lengths training60/58/61/57/62/58,probe60/58/62/57/62/58 |Complete12calls at01:10:45; [56](SOURCES.md#s56) |
| E29 — Input scope or output length? |OldSFT,four validationcontexts,two seeds:all64/full16/local16correct145/153/348 of512;unchangedreplay143/153/349. Allvalid |Complete72+72calls; [60](SOURCES.md#s60),[61](SOURCES.md#s61) |
| E30 — Does computed commitment beat restatement? |Sixshared-prefix coordinates processed,12nativecalls;all6modelnon-submission;commit/restatement outcomesnull |Completedprotocol-feasibility failure,not an effect estimate; [62](SOURCES.md#s62) |

E30's terminal result explicitly says processed coordinates are not successful model submissions. No branch-comparison effect is estimable. The subsequent bounded review reports all six first cells AST-valid/status-ok, but none calls `submit_text`. Blank observations occur only in cases0–2, whose bare expressions sit inside `if/else`; an operator-authored CPU IPython fixture confirms that this normally emits nothing. Cases3–5 have intact observations. No transport defect is established. This is failed protocol feasibility, not proof of an intrinsic inability to commit computed answers. The campaign's proposed continuation, validation4/6/8, fixed selection and transfer remain unrun at this slice. Original-weight scope completed after this slice and is not pooled into E29.

[^35]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Historical"
[^36]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Queue"
