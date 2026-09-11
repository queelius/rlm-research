# What the experiments say about using decomposition well

These findings connect experiments rather than rank models on a single leaderboard. “Fact” denotes an observed, bounded result. “Inference” denotes an explanation compatible with those results. Recommendations are collected in [Next experiments](NEXT_EXPERIMENTS.md). Experiment identifiers resolve in the [catalog](EXPERIMENTS.md).

## Teaching the child helps, but its benefit is partly hidden by the surrounding system

**F1 — Local supervised learning is demonstrated; broad transfer is not.**

E01 trained the original converted 4B LoRA for two supervised epochs on authoritative TREC labels: 5,065 training groups, 300 validation groups and 489 test groups. The validation-selected second epoch improved strict item yield from 355 to 473 correct test items. Because a single noncanonical string invalidates its whole array, that score combines semantic and interface changes. Canonical per-item correctness improved from 374 to 473; accepting the declared aliases gives 376 to 473. The paired alias-sensitive comparison has 102 newly correct and five newly wrong items. There is substantial semantic learning even after removing the strict-array artifact, but the full 118-item strict gain must not be presented as pure semantics.[^1]

The test/validation gap is large: 473/489 on the test versus 250/300 on validation. Reweighting the six coarse classes does not eliminate it. The validation sample contains far more HUM groups and fewer definition questions within DESC; some disagreements concern the intended annotation ontology. Validation is not an IID 300-item miniature of the test. Training and evaluation groups were normalized and disjoint, with known source train/test collisions excluded; unknown model-pretraining and historical-data exposure remain unresolved.[^1]

The earlier prompt-only factorial supports this interpretation without substituting for training. On 300 validation questions repeated across three seeds, canonical predictions were 183/900 for the baseline, 388 with definitions, 343 with a schema, and 410 with both. Much of the baseline/schema gain is vocabulary normalization; definitions still help after alias sensitivity. The unit is 300 source groups, not 900 independent examples. The model needed a clear task contract as well as compliant syntax.[^12][^13]

**F2 — A competent child is necessary here, but does not ensure competent orchestration.**

On six newly composed 64-record contexts, a fixed five-item classifier and Python aggregation improved strict aggregate answers from 1/24 to 15/24 when only the child weights changed. The corresponding freely acting RLM improved from 4/24 to 6/24. A development role-routing check was unchanged at 2/6. These are different operational contracts, not a compute-matched decomposition leaderboard. They do show that useful child information is available in settings where the autonomous system often fails.[^2]

The trace audit localizes some losses. A trained-child episode correctly classified all target-class members but the root extended a Python list with the characters of a returned string, then counted zero target labels. Other episodes stopped with tool-looking text that was never executed, classified only part of the dataset, or guessed a final count. Coverage and parsing matter independently of leaf semantics. Among 23 fully covered composition episodes, 22 aggregated faithfully, so “roots always aggregate badly” is also too strong: the failure mixture matters.[^2]

There is a crucial causal limit. The two arms used the same root weights and identical first-root requests, yet their first-root outputs differed before any child call in 15/24 composition pairs. Such pre-child differences cannot be caused by changing a child that has not yet run. The 4→6 comparison is descriptive, not a clean estimate of a child-mediated effect. A shared-prefix intervention is needed to isolate how the root uses changed child evidence.

## Long batches expose a separate correspondence problem

**F3 — Structure, semantics, and complete alignment are distinct capabilities.**

E03 provides the clearest separation. Free 64-item outputs were unusable in all 24 coordinates per weight, often reaching the 1,024-token cap. Exact-cardinality enum constraints made every array valid, but strict aggregate accuracy remained zero. The original child was canonically correct on 645/1,536 aligned predictions; the trained child on 698/1,536. Its first quarter was 374/384 correct and last quarter 81/384. The final quarter contained 366 predictions of `entity`, versus 80 gold entities. Actual provider token IDs contained all 64 questions, at only 1,321–1,361 prompt tokens under the 8,192 limit.[^3]

This is evidence against missing input as the explanation for that collapse. The same questions in trained five-item batches remained accurate across their original positions, weakening an explanation based solely on late questions being harder. It does not yet separate loss of positional correspondence, repetitive-label continuation, attention allocation, or a learned output-length prior. Position/permutation and representation controls target those alternatives; their completed results must be read before commissioning a duplicate experiment.

The singleton control is unusually clean: the trained model's first label was identical with and without the schema on all 1,536 calls. The schema removed surplus labels; strict aggregate answers improved from 5/24 to 16/24. That is demonstrable interface repair without changed first-label decisions. It is not evidence that constrained decoding universally improves semantic reasoning.[^3]

E04 tested two mixed-size curricula: A included sizes 1/5/16/32; B included 1/5/16/64. Each saw every training record once per epoch for two epochs, starting from the same original adapter. Fixed-final small-batch test scores were 477/489 and 476/489, versus 473/489 for old all-five training. Neither produced a usable array on the frozen six-context 64-item HF test. A hit the output cap in five contexts; B instead produced closed canonical arrays of lengths 62, 58, 62, 57, 62 and 58. B changed the failure mode, not the primary outcome. Token loss and record exposure are not sufficient proxies for complete task correspondence.[^4]

A post-hoc prefix check found more early aligned labels in A/B than old SFT. Missing items make that alignment assumption uncertain; it cannot repair the declared strict score. Likewise, the original HF/vLLM “same prompt” sanity control had different physical tool serialization. The old/A/B frozen HF comparison does use the same evaluation IDs, but train/evaluation template identity needs the separate completed template control.

The completed follow-ups now give a stronger lead. On four reused TREC validation contexts and two seeds, old-SFT anonymous arrays had 181/512 correct labels, indexed output 405/512, and question-echo output 419/512; all eight calls per arm met the declared contract. The echo copied 511/512 questions exactly. All arms had the same 3,072-token cap, but the intervention changes both representation and constraints, not only an index. In the rotation control, strong early-position accuracy persisted at offsets 0/16/32/48 while later positions remained weak. This supports a position/correspondence mechanism and argues against the same intrinsically hard questions always being responsible.[^46][^47][^59]

The matched-schema validation control also clarifies mixed training: original, old SFT, A and B achieved 135, 179, 219 and 241/512 correct labels respectively, with all schema arrays valid. Mixed training therefore has a partial aligned-label benefit on these reused validation compositions, but does not recover high late-position accuracy: B's quartiles are 106, 69, 39, 27/128. “Mixed training only changed formatting” is too strong; “mixed training solved correspondence” is also false.[^48][^49][^50][^51]

SST-2 does not show a large generic transfer rescue. On 256 public validation sentences repeated with two seeds, natural5 canonical yield was 462, 459, 470, 470/512 for original, old SFT, A, B; schema64 yielded 318, 308, 326, 324. Every schema64 array was valid, but every model had zero fully correct 64-sentence coordinates. No TREC-label leakage was recorded. Weak64 behavior extends to a new two-label task, but vocabulary, semantics and prompt all change together; this is not a pure label-renaming test. Finally, fresh fixed-B HF calls with the saved training template still gave 0/6 usable arrays, as did the probe template, with no truncation. The serialization mismatch is not a sufficient explanation for B's incomplete output in that control.[^52][^53][^54][^55][^56]

There is important counterevidence to a universal batch-size claim: in an earlier synthetic six-label Qwen3-8B setup, size 64 achieved 99.3% item accuracy and valid calls throughout, although only 36/48 whole partitions were exact. Different data, model, output indexing and contract make that a boundary condition, not a rebuttal of the 4B TREC observation. “64 is too large for small models” would erase the actual scientific question.[^20]

## Input selection can help, but simplifying the requested answer can hurt

**F4 — Narrowing relevant input and changing semantic work are different interventions.**

In E12, matched supervised fixed/adaptive controllers followed their assigned routines in 288/288 episodes per arm on 18 unseen synthetic context groups. Both solved all 144 visible-metadata questions. Conditional answers were 134/144 fixed versus 144/144 adaptive, with 67.8% fewer conditional leaf-input tokens under adaptive routing. Two optimization seeds, explicit masked action targets and context-group splits make this a useful narrow learned-routing result. The failed formal gate—no room for the required visible-answer gain—must remain visible. The routines were taught, not discovered, and the readout was development data, not broad structure transfer.[^19]

The component controls are mechanistically valuable. Keeping the six-way semantic contract while filtering input to a relevant facet yielded 47/48 exact conditional answers versus 43/48 for full mapping, with substantially less leaf input. Changing the semantic task to a target-versus-other classification performed poorly: 6/48 exact in one unfiltered comparison, versus 40/48 for generic mapping; filtering plus the binary contract achieved 27/48 versus 43/48 for the generic comparison. Less text or fewer label choices is not automatically easier if it changes the task the model recognizes.[^21][^22]

The newest natural-question scope test points in the same direction. On four reused validation contexts, old-SFT all64 output scored 145/512 labels; asking for 16 at a time while retaining the full64 input scored 153/512; presenting only the requested16 scored 348/512. An unchanged-weight replay gave 143,153,349. All arrays were valid. Shortening output alone did not recover performance, whereas removing non-target input did. However, full16 also imposes a selection task: this is not proof of an attention-capacity mechanism. A reported post-hoc comparison suggests the model often labels the first visible16 rather than the requested later subset; that diagnostic must never replace the primary requested-target score.[^60][^61]

Broader-layout training was not a clean rescue. Its favorable presentation interaction coexisted with a 30.6-point loss on canonical tasks and more failures; checkpoint scores were nonmonotonic. A positive interaction alone can mean “the control deteriorated differently,” not a better usable system. This argues for absolute performance, cost and failure endpoints alongside difference-in-differences.[^24][^25]

## Root learning requires more than a valid optimizer step

**F5 — The training pipeline now makes real root-only updates; the learning claim remains open.**

The pilot made one genuine full-batch TIS/AdamW increment, crediting 10,500 current-root action tokens from 16 mixed-reward episodes. It did not credit child actions or observation tokens. Initial, unchanged and post-update validation were 2/8, 4/8 and 2/8. All first-root prompt IDs matched, but unchanged weights reproduced only two first-root action sequences. This is a direct local warning against treating same declared seeds as deterministic replay.[^5]

The subsequent fresh-generation campaign committed three updates with persistent Adam state, crediting 23,130, 11,091 and 14,399 root-action tokens. Training strict successes were 12/32, 13/32 and 12/32 on fresh seeds; those totals are unpaired. Validation was 2/8 at step zero and 3/8 at step two—two newly correct and one newly wrong coordinate. The last checkpoint is step three and has no completed validation. There is no selected checkpoint, final holdout or transfer result.[^6]

The later math audit found no established optimizer/loss defect in those increments. It reproduced actual Adam2→3 tensor updates, checked all 150 credited root turns, and verified physical token/log-probability identities. The same-forward HF reference is valid for one full-batch update per fresh generation. Its nominal PPO ratio is one before that increment, so PPO clipping is inactive: this is not multi-epoch PPO. Token-level correction is not exact trajectory importance sampling; small conditional discrepancies can accumulate over long trajectories. Those limitations qualify the method rather than negate the fact of an update.[^7]

**F6 — Admission and failure accounting can erase the very behaviors a reward should expose.**

Round four stopped after a completed wrong episode included a recovered child HTTP400: 9,972 input tokens exceeded the 8,192-token limit. Its aliases, request IDs and fixed-child hash matched. The exporter treated an unsuccessful provider attempt as identity corruption; the wrapper escalated it to a fatal campaign stop. A diagnostic projection reconstructed all 72 sampled calls with exact native token evidence. The original stop remains an authentic result under the frozen rule, but it is not evidence of corrupted routing, action capture or loss masks.[^7]

There are three different populations: completed policy negatives; fully identified failed provider attempts inside completed episodes; and incomplete episodes with unobservable outcomes. They cannot all become “infrastructure failures” or all become reward zero. The pilot's recovered overlong requests occurred inside completed wrong episodes, while two training episodes lacked observable completed outcomes and remained null. A revised training admission rule must be explicit because excluding policy-induced overlength can selectively censor difficult behavior.[^5]

Earlier runs illustrate both sides of the learning bottleneck. A hard-run exporter excluded completed policy failures because their trajectory shape differed; 18 recoverable completed cases were found later, whereas 102 genuinely incomplete cases remained null. Conversely, an 8B root executed identical, near-certain two-cell routines across 36 episodes; all within-task rewards were homogeneous, so no update occurred. More rollout seeds alone did not create learning headroom. Fix exclusion bias where it exists, but do not train a root to solve a child-only error.[^9][^11]

## Verifying the final answer does not verify how it was obtained

**F7 — Reward and process disagree in multiple independent task families.**

The direct OOLONG audit replayed 88 traces: 27 official exact rewards became 13 strict exact answers. Fourteen official “successes” were truncated outputs containing a gold mention. The four reconstructed admitted training batches contained none of those contaminated episodes, so this is a measurement defect, not demonstrated training-induced reward hacking. Strict heldout performance was 1/8 both before and after four updates.[^8]

Even correctly parsed aggregate answers can hide wrong semantics. In a recursive-example task, false positives and false negatives cancelled to produce the correct count while most canonical labels were wrong. Full-composition successes also sometimes relied on cancellation. Explicitly demonstrating recursion or accepting a final count cannot certify that decomposition was useful.[^2][^14]

The neighboring structured-decomposition work has an exact solver for a valuable extra quantity: the answer *implied by the displayed reports*. With binding wording, report adherence improved from 2/10 to 10/10, and original-task accuracy from 3/10 to 7/10 in a small reused-tuple intervention. But when reports implied a wrong answer, forcing adherence could remove an independent rescue. Natural worker and revision screens reproduced the distinction: some final-answer gains did not come from better reports at all.[^28][^29][^30]

The common mechanism is not that process supervision is always superior. It is that final reward leaves several latent pathways observationally indistinguishable: correct evidence used correctly, wrong evidence cancelled, evidence ignored and task re-solved, or answer-format loopholes. A useful verifier should expose those pathways diagnostically before changing the optimization objective.

## Report use, revision, and search need measurable headroom

**F8 — Stronger adherence or more revision can amplify bad evidence.**

In the five-root natural-worker screen, direct and compute-matched direct each scored 2/5, advisory reports 1/5 and binding reports 3/5. The result is an open development screen, not a decomposition win across a population. All successes were no-solution (`NONE`) cases; the found-solution cases remained difficult. In 15 subsequent one-report revisions, only one of eight wrong targeted reports was repaired while four of seven correct ones were damaged. No wrong implied-root tuple became correct. Revision therefore lacked the needed repair headroom; an elaborate selector would not fix an absent candidate.[^29][^30]

The synthetic selective-verification policy was more encouraging but still failed its frozen safeguard. It improved full-context correctness from 35/48 to 43/48 by reconciling batch views and singleton disagreements; the large views nevertheless agreed on 11 wrong records. Agreement is useful evidence, not a certificate. Online costs and failure dependence must be measured before teaching a root to trust it.[^23]

Evolved integrators offers a parallel lesson outside language reasoning. Search found feasible small coefficient perturbations and useful work/error tradeoffs, including a cautious held-out improvement over its seed. An aggressive candidate reduced RHS evaluations but increased family-level misses. Rediscovery across proposal runs did not create independent held-out datasets, and a tiny coefficient adjustment is not a new integration algorithm. The transferable lesson is to keep hard constraints, target tradeoffs, selection and held-out scope explicit—not to infer that code search establishes RLM orchestration.[^31]

## The harness changes what the experiment means

**F9 — Task execution, model identity and final commitment are substantive experimental variables.**

A native nonthinking/prefill qualification changed a previously nonexecuting TrainClient path into one that actually used tools. Abstract procedure hints, by contrast, produced zero observed recursion across 168 episodes over three weights; a concrete recursive-call example activated recursion in five of six original-weight tasks. Those are behaviorally different interventions. “The model cannot recurse” was an overstatement of one prompt/client condition.[^10][^14][^15][^16]

On six short MRCR documents, direct full-context answering scored 2/6 while two native RLM variants scored zero. A native direct control reproduced all six earlier Chat direct outputs exactly, weakening a client-only explanation. Retrieval mistakes, wrong occurrences, textual copying and length-capped final generation remain plausible task-level failure mechanisms. These small contexts fit the direct model's window; this is not a long-context scaling result.[^17][^18]

The local Responses-only kernel and the current Prime/nano research runtime must remain separate in interpretation. The core review reproduced omission-metadata and late-response usage bugs in the former. That does not explain current nano outcomes; the actual campaign exporter diagnosis comes from the latter. Likewise, inherited retries are a source capability, not evidence that any observed retry incurred new inference. Experimental attribution must follow the executed source and request lineage, not a shared project name.[^7][^33][^34]

## What a credible contribution could look like

**F10 — A causal account of evidence fidelity is more defensible than a generic “better RLM” claim.**

The distinctive opportunity is to connect component-level semantics, correspondence, root use, and final commitment under authenticated role-specific weights and fixed budgets. Existing work already studies recursive root training, batched prompting, order sensitivity, structured decoding, role specialization, process supervision and prompt evolution. None of those ideas alone is a novelty claim here.[^39][^40][^41][^42][^43][^44][^45]

A publishable contribution would require an additional result: a preregistered intervention that improves one diagnosed mechanism on fresh grouped data, survives an unchanged-policy control, and produces an end-to-end accuracy/cost gain without hiding invalid outcomes. A carefully bounded negative result can also be useful if it rules out a plausible mechanism—for example, perfect cardinality without recovered correspondence, or improved component semantics without faithful root use. The existing artifacts supply a strong basis for such tests, not a substitute for them.

[^1]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Supervised"
[^2]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Role,"
[^3]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Batch-shape"
[^4]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Mixed-size"
[^5]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Root"
[^6]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Terminal"
[^7]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Actual"
[^8]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Reward"
[^9]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Hard-run"
[^10]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Client"
[^11]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [8B"
[^12]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Leaf"
[^13]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Validation"
[^14]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Recursive"
[^15]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Plan"
[^16]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Post-TIS"
[^17]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [MRCR"
[^18]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Native"
[^19]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Matched"
[^20]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Synthetic"
[^21]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Input"
[^22]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Query-shaped"
[^23]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Selective"
[^24]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Layout"
[^25]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Checkpoint"
[^28]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Binding"
[^29]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Natural"
[^30]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Revision"
[^31]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Integrator"
[^33]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Core"
[^34]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Runtime"
[^39]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Recursive"
[^40]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Batch"
[^41]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [BatchPrompt](https://arxiv.org/abs/2309.00384)."
[^42]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [JSONSchemaBench](https://arxiv.org/abs/2501.10868)."
[^43]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [MapCoder-Lite](https://arxiv.org/abs/2509.17489)."
[^44]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Let's"
[^45]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [GEPA](https://arxiv.org/abs/2507.19457)."
[^46]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Representation"
[^47]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Rotation"
[^48]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [B"
[^49]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [A"
[^50]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Old"
[^51]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Original"
[^52]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Original"
[^53]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Old"
[^54]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [A"
[^55]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [B"
[^56]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Fresh"
[^59]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Intervention"
[^60]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Output-scope"
[^61]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Unchanged"
