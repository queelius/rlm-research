# Research analyses: reading guide

Start with [what we know so far](CURRENT_SUMMARY.md) for the latest plain-language
overview, including the completed root-training and output-ID comparisons.
Read [the most promising findings](PROMISING_RESULTS.md) for the two leading
research results, their possible publication angle and the evidence still needed.
The [cross-experiment dossier](cross-experiment-synthesis-2026-09-09/README.md)
provides the wider history: its findings, catalog and source inventory let you
follow a claim back to completed evidence. The dossier has an explicit evidence
cutoff, so later work is listed separately below.

The latest additions below are current through September10,2026,21:27 UTC.
The older report table and source catalog retain their earlier explicit cutoffs;
these links do not rewrite that catalog or turn historical active labels into
current reservations.

## Latest evidence and decisions

| Analysis | What it adds |
|---|---|
| [Selective recheck](root-supplied-plan-selective-recheck-live-2026-09-10/REPORT.md), [MAIN independent recount](../../../ARTIFACTS.md#unpublished-files "Not published: root-supplied-plan-selective-recheck-live-2026-09-10/MAIN_ADOPTION.json") | Confidence71repairs/31regressions versusrandom19/28; net+40 versus-9labels, but exact downstream1/8 versus0/8 misses+2gate. All24native calls/16arm-episodes valid; four correlated exposedclusters. |
| [New-context numbering replication](leaf-mnli-positional-anchor-new-context-live-2026-09-10/REPORT.md), [denominator correction](leaf-mnli-positional-anchor-new-context-live-2026-09-10/ERRATUM.md) | Primary late-position interaction+42.77 points, positive16/16 contexts; all192native/valid. MAIN192 literal request/output checks and576capture pins. Interface package, not full-RLM benefit. |
| [Supplied-plan child bottleneck](root-lambda-supplied-plan-ceiling-live-2026-09-10/REPORT.md) | All40calls and8maps valid,1129/1280labels correct, but0/8 exact totals. Same reducer with reference labels8/8. MAIN independently rerendered40requests and recomputed8predicted/oracle totals. |
| [Confidence-based error ranking](leaf-trec-confidence-ranking-live-2026-09-10/REPORT.md) | Exact4000label spans/148calls; lowest-confidence25% covers65.8%/67.8% of trained-child errors at two batch widths. Ranking, not calibration/recheck efficacy; MAINbyte-identical replay. |
| [Controller gains excluding zero answers](controller-zero-support-strata-2026-09-10/REPORT.md), [MAIN replay and missing-outcome bounds](../../../ARTIFACTS.md#unpublished-files "Not published: controller-zero-support-strata-2026-09-10/MAIN_ADOPTION.json") | Nonzero correct-and-performed gains10→32/46,9→27/46,7→25/44. Gains persist in the composed strata under all missing-outcome assignments. Three related readouts of one checkpoint, not independent replications.432 planned rows retained. |
| [Large-input execution limits](root-qs-scale-harness-factorial-live-2026-09-10/REPORT.md), [zero-support qualification](root-qs-scale-harness-factorial-live-2026-09-10/ZERO_SUPPORT_AND_ACQUISITION_NOTE.md) | 64 planned,38 observed,9 correct,26 timeout-NULLs.12 actual-path faithful/7 also correct, but6/7 had zero gold. One nonzero success; no scale-transfer claim. MAIN150 pins, full native replay and12 independent J1 recomputations. |
| [Child interface compatibility](leaf-trec-query-conditioned-interface-live-2026-09-10/REPORT.md), [clarification](leaf-trec-query-conditioned-interface-live-2026-09-10/ERRATUM.md) | Six-label output plus host projection beats direct A/B/other. The child adapter improves672→726/768 under full labels but605→605 under compact labels. All192 responses valid; classwise tradeoffs differ despite equal totals. |
| [Matched input/output numbering](leaf-mnli-positional-anchor-binding-live-2026-09-10/REPORT.md) | Input/output numbering package improves590→933/1152 total and292→620/768 later labels. Output-only condition misses its gate. Fresh-context replication is queued; this is not yet an RLM task gain. |
| [Fresh-context field-order check](leaf-mnli-field-order-replication-live-2026-09-10/REPORT.md) | Selective effect+9.77 points, positive14/16 contexts, narrowly below the frozen10-point gate. Directional support without moving the threshold. |
| [Composed-RL long-trace diagnosis](root-composed-rl-window03-memory-diagnostic-2026-09-10/REPORT.md) | One saved RL update; next group has154 turns and647,114 causal tokens. Memory pressure followed by240s timeout. Sparse credited-position logits and an enlarged cap are being qualified as explicit infrastructure recovery, not replacement training samples. |

Current prospective work includes [matched child-interface SFT](leaf-trec-child-interface-sft-followup-idea-2026-09-10/DESIGN.md),
[typed evidence-state mechanisms](../ideas/2026-09-10-typed-evidence-harness-followups.md),
and [evidence-use interventions with primary-literature context](../ideas/2026-09-10-evidence-use-versus-evidence-preservation.md).
Proposals are not results; the [live queue](../RESEARCH_QUEUE.md) identifies accepted jobs.

## Completed and supporting reports

The [linked research catalog](research-factory-2026-09-09/README.md) connects a
bounded first slice of nine sealed reports to questions, claims, decisions and
publication gaps. The [question-centered Markdown + YAML view](../questions/README.md)
adds readable question pages without replacing the sealed catalog. For current
execution, use the [live queue](../RESEARCH_QUEUE.md); the earlier allocation
handoff and older ACTIVE labels below are historical.

| Analysis | What it adds |
|---|---|
| [Query-sensitive RL makes updates but shifts toward zero](../operations/2026-09-09-allocation-5780/query-sensitive-rl-audit-report.md) | All12 windows and10 genuine Adam updates completed;102 episodes/66,288 root action tokens entered clean updates. Final unchanged2/48 (46 available) versus trained4/48 (36 available), but all4 trained successes are zero-gold and neither arm calls a child. `all` wording is ambiguous and trained availability collapses5/16 versus15/16; unaffected scopes are availability-matched but still gain only zero answers. Report SHA `46ad5bba…843b`, final manifest `dd779277…c87a`. |
| [Native Python exposes a record-parsing bottleneck](../operations/2026-09-09-allocation-5780/native-partition-join-audit-report.md), [target-fact erratum](../operations/2026-09-09-allocation-5780/native-partition-join-audit-report-erratum.md) | Direct Python2/8 versus no-tools0/8, all16 available; six Python lexical parsers fail despite copying the real facts.24 extraction calls give5 exact/19 subset reports, so all32 report-root slots remain source-gated NULL. Corrected4/8 packages retain every relevant triple,6/8 host-join sufficient; source-contract failure is not always loss of the answer.52 physical calls. MAIN verified105 final+4 erratum pins. |
| [Joint training improves tasks through mixed strategies](../operations/2026-09-09-allocation-5780/joint-state-reduction-sft-audit-report.md), [checkpoint-wording erratum](../operations/2026-09-09-allocation-5780/joint-state-reduction-sft-audit-report-erratum.md) | Free joint8/16, reduction6/16, unchanged2/16 planned;12/14/15 available. Union7/8,4/8,0/8. Only one successful free live-variable scalar per policy; joint also uses genuine returned labels in literal calculations/manual answers. Controlled live-scalar2/8,4/8,0/8; joint costs401free requests versus281/77. Four exposed contexts, unequal training dose. MAIN verified192 final+4 erratum pins. |
| [Visible observations change actual state use](../operations/2026-09-09-allocation-5780/state-content-factorial-audit-report.md), [erratum](../operations/2026-09-09-allocation-5780/state-content-factorial-audit-report-erratum.md) | V1 old-state use18/32 versus3/32 V0; faithful reduction16/32 versus3/32. Accuracy15/32 versus14/32, so not a demonstrated task gain. Corrected full width4 merge12/32.62 available/64planned;196 new authenticated calls; four exposed contexts. |
| [Source-ID benefit survives a cleaner leaf role](../operations/2026-09-09-allocation-5780/leaf-role-tool-audit-report.md) | Classifier/no-tools exact matching218/256 versus129 constant/123 plain, matching wins all4contexts. Free matching validity0/4→3/4 by removing either coding role or tools; residual forbidden label, not ID loss. All96available; fixed order/one seed. |
| [Quoted history versus archived files](../operations/2026-09-09-allocation-5780/artifact-restart-audit-report.md) | Q10/16 correct/12faithful supplied reductions; A3/16/zero archived-state reads/42 new children; M6/16planned/one faithful reduction/twoNULL. Same16 source states, four contexts; quoting bundles code and observations. |
| [Corrective training: original incomplete readout](../operations/2026-09-09-allocation-5780/corrective-sft-audit-report.md), [separate controlled completion](root-corrective-reduction-sft-live-2026-09-09/completion/REPORT.md) | Bothfour-updatearms trained. Free unchanged10/32,producer2/32,corrective7/32planned/25available. Additive exact16 previouslyunrun controls5correct/14available, onlyone faithful supplied scalar. No free improvement or seamless repair claim. |
| [A valid final format does not solve the join](../operations/2026-09-09-allocation-5780/partition-final-interface-audit-report.md) | Free12invalid; constrained12validbutwrong; all24available. Full child evidence sufficient, original records visible. The separately sealed native-Python follow-up appears above; it does not replace this original result. |
| [A proposed curriculum duplicated completed work](../operations/2026-09-09-allocation-5780/broader-rl-duplication-check.md) | Exact data/task/schedule check retired unlaunched proposal; originalBROAD16 already completed. Low66c/interface changes did not create new breadth or fresh evaluation data. Zero GPU work on duplicate. |
| [Accurate fields help; map agreement does not prove reuse](root-map-contract-clarity-live-2026-09-09/REPORT.md) | REPORTad8f2d93…, SEAL3d3f40eb….95/96 available,58 correct. Accurate fields remove18 field-error endpoints; bundled map wording has mixed effects.48 loads versus18 actual scoped scalar/list uses. Four context clusters and one genuine NULL;367 physical calls. |
| [Free output exposes a role/tool contract mismatch](../operations/2026-09-09-allocation-5780/free-id-audit-report.md) | Report0f946a59…2259f, FINALbb92443c…ee46. All96 actual calls available; free4/48 versus exact48/48 valid.35 free outputs follow advertised Python, nine arrays overgenerate. All complete ID arrays have correct IDs. Exact matching wins all eight context means, but grammar also constrains route/stopping, so this is not isolated ID-copy dependence. |
| [Example anchoring and map visibility](../operations/2026-09-09-allocation-5780/visibility-audit-report.md) | Report SHA `7ba22267…310b`, final-manifest SHA `dcf920b5…d94`. Correctness is24/32 and6/8 in every cell across eight blocks/four context clusters. Supplied-map state is actually used26/32 (25 programmatic, one manual); six example/file endpoints reclassify and overwrite it. All inline code still opens the file, so no executed-code evidence shows the inline payload was parsed. |
| [Partition pilot exposes an insufficient final-answer instrument](root-partition-report-live-2026-09-09/REPORT.md) | Report SHA `6d72da75…206a`, final-manifest SHA `3adb397a…fdb`. Strict0/40 cannot support communication-loss or recursion claims: exact extraction is24/24 calls and384/384 triples, full reports imply gold8/8, and ordinary prose retains positive facts sufficient for4/4 cross worlds under labeled manual reduction. Full parents truncate8/8 at256 tokens. |
| [Available maps and helpers are often not used](root-supplied-map-reducer-live-2026-09-09/REPORT.md) | Report SHA `df074ae6…ec40`, final SHA `b9be310b…a884`. All32 finals available. Native-map Python5/8 versus helper3/8; privileged-map Python5/8 versus helper2/8. Only one helper endpoint actually invoked it, on fresh child output; no successful helper use of supplied labels. This is a resource-use diagnosis, not pure reducer accuracy. |
| [Adding terminal demonstrations did not repair scoped reasoning](../operations/2026-09-09-allocation-5780/complete-sft-audit-report.md) | Report SHA `46c11bdc…c7e4`. Unchanged8/16 versus1/16 in both matched trained arms; no NULLs. Scalar-copy terminal loss nearly saturated. All16 authentic examples, eight optimizer checkpoints,48 native endpoints and459 physical calls audited. This retires one recipe, not SFT generally. |
| [Three trained roots still struggle to use better child outputs](../operations/2026-09-09-allocation-5780/audit-report.md) | Full96-endpoint panel available. Checksum0/8 in both formats for every root. Count-map effects differ across roots; native traces distinguish dictionary misuse, missing reduction and changed adaptive plans. |
| [Current source IDs help with an otherwise fixed history](leaf-local-cue-replay-live-2026-09-09/REPORT.md) | All288 candidate forwards audited. Matching versus constant cues increases mean conditional correct-label probability by0.497 AG and0.277 SST. Fixed supplied history and finite label set; not sampled accuracy or attention. |
| [Child-format benefit does not yet improve whole answers](root-child-representation-bridge-live-2026-09-09/REPORT.md) | Count1/8both despite matched label agreement567→593/628; checksum0/8both with only3/8paired uptake. All32 available/744native calls. Selected last-batch reduction bug, not wrong copying of a correct scalar. |
| [Contradictory IDs redirect labels](leaf-shifted-cue-live-2026-09-09/REPORT.md) | All72 valid. On unequal-gold TREC positions, shifted outputs follow named record375/398 versus displayed3/398. SST/AG also favor named records. Behavioral cue following, not attention proof. |
| [ID benefit on newly selected records and released models](leaf-fresh-correspondence-live-2026-09-09/REPORT.md) | All96 valid; matching beatsconstant all16 context means/two released models. New only against25 named research catalogs; helper/base/pretraining exposure distinctions retained. |
| [Authored first-action training did not teach filtering](root-plan-sft-live-2026-09-09/REPORT.md) | Both trained1/16 versus4known unchanged successes and1NULL. Full relevant coverage but exhaustive selection, poorer format and more calls. Eight real optimizer updates independently verified. |
| [Query failures: label disagreement and missing reduction](root-query-failure-taxonomy-2026-09-09/REPORT.md) | Fifteen of32 repeated-context cases involve one frozen-label disagreement. All19 displayed scalars copied faithfully; six correct maps never counted. Adds one historical highLR broker-NULL correction. |
| [Four further reward updates improve longer-input answers](root-bounded-refill-rl-live-2026-09-09/REPORT.md) | Last fixed update4:7→11/24,6gains2losses; query0→0, length2→5. One pre-update broker-error empty endpoint needs availability-safe sensitivity, net[3,4].64 actual training episodes/34,116 root tokens; no extra refill or NOOP exercised. Correct-map-to-wrong-answer remains a bottleneck. |
| [Shifted-ID comparison: independent source review](leaf-shifted-cue-review-2026-09-09/REPORT.md) | Exact72 requests/24 prompt triples, +17 source rotation and positional versus named-source scoring independently checked. Prepared component mechanism probe, not a model result. |
| [Same records, different reminder distances: plain-language plot](reminder-phase-visualization-2026-09-09/REPORT.md) | Three raw-accuracy panels from sealed192-call audit; equal context/seed means on the same61records at each distance. SVG/PNG and exact numeric source, visually checked. Not whole-RLM success or an attention measurement. |
| [Larger training updates improve longer-input answers](root-success-sft-lr-live-2026-09-09/REPORT.md) | Same27 complete examples/start/eight orders, LR2e-5→1e-4. Paired8/24→14/24,9gains3losses; syntax16→24, coverage21→24. Query transfer2/8 unchanged; length1→6/8. All8 checkpoints and48 native graphs audited. No blanket successful-task cost improvement. |
| [Withholding partial totals changes continuation](root-coverage-first-live-2026-09-09/REPORT.md) | Trained root map4/8, always-counts2/8, coverage-first5/8; precursor2/8,0/8,2/8. All48 endpoints/352 native calls audited. More coverage and higher cost; primarily avoids premature-count harm rather than demonstrating superiority over ordinary maps. |
| [Bounded-refill RL: independent source review](root-bounded-refill-rl-review-2026-09-09/REPORT.md) | Fixed low-SFT8/freshRLAdam; exact variable-cardinality native admission, true no-op and separate window/update cursors.42 critical hashes and independent prefix tests checked; no material blocker. Preparation evidence, not a training result. |
| [Complete successful examples improve the coordinator](root-success-trajectory-sft-live-2026-09-09/REPORT.md) | Baseline5/24, successSFT8 9/24, RL7 9/24; SFT6gains2losses, RL5gains1loss. All72 endpoints/881physical calls audited. Format/coverage improve, firstHELPER copying remains22/24. Unequal-compute packages on8exposed contexts. |
| [Moving reminders changes accuracy on the same records](reminder-phase-live-2026-09-09/REPORT.md) | All192 valid; all24 context-seed primary declines positive. Matching-minus-constant advantage falls55.94/27.66/50.82pp from reminder to3later on identical61records. Originalzero-call failure and recovery separately costed. |
| [ID benefit appears in two released models](leaf-qwen35-identity-live-2026-09-09/REPORT.md) | Matching beatsconstant all48 paired model/task/context/seed units.143/144valid, one truncatedcontrolstrict0, noNULL; no researchadapters. Old exposed contexts; crossmodeltemplates differ. |
| [Reminder field order shifts the benefit: plot](leaf-sparse-cue-order-main-review-2026-09-09/REPORT.md) | Independent96raw audit and data-nativeSVG/PNG. Same prompt, only ordered schema changes; moving IDafterlabel shifts benefit towardnextlabel. Difference-of-differences, not taskaccuracy or attentionproof. |
| [Partial totals can encourage premature answers](root-accumulation-ledger-live-2026-09-09/REPORT.md) | Map3/8→ledger0/8; all8ledgerroots stopafterfirst4records. Actualnative suffix and identicalfirstsampledactions verified;16clean endpoints/67calls. Coverage-firstfollow-up nowqueued. |
| [Fresh-source feasibility and explicit limits](fresh-correspondence-data-feasibility-2026-09-09/REPORT.md) | Atmost9unused TRECgroups/8SSTvalidation; freshclustersimpossible there. AGtest/SSTtraining availability measured with named-input scan, phrase/near-dup/license caveats. No 'unseen to model' claim. |
| [Equal-example loss did not improve task success](root-interface-sft-row-mean-live-2026-09-09/REPORT.md) | Both models solve the same2/24; syntax and coverage lower under equal-row weighting. All48 endpoints/285 native calls reconcile. Easy terminal microexamples already have almost zero CE; no successful-task cost gain. |
| [Adaptive reward training stopped after seven updates](root-adaptive-rlvr-live-2026-09-09/REPORT.md) | Seven verified updates/68,008 root-action tokens; round8 has no within-prompt reward variation. Midpoint2/8→2/8; no original final8 readout. Three IPython broker timeout NULLs remain distinct from model errors. |
| [Complete-success training-only screen](adaptive-success-trajectory-feasibility-2026-09-09/REPORT.md) |27 confirmed complete trajectories/114 root turns/15,256 targets from fixed training rounds1–5; no evaluation candidates. Two weaker lineage cases excluded, all recovery turns retained. |
| [Sparse ID reminders: plain-language plot and MAIN check](leaf-sparse-anchor-main-review-2026-09-09/REPORT.md) | Independent raw parsing agrees with all144 primary, distance and cost cells. Dense reminders outperform sparse; cadence4 accuracy often falls away from tag-bearing positions. SVG/PNG figure and explicit cost tradeoff. |
| [Sparse ID reminders: full independent audit](leaf-sparse-anchor-live-2026-09-09/REPORT.md) | All144 valid, no NULLs or whole64 successes. Dense matching wins strongly; every sparse-versus-dense context–seed pair loses accuracy. Full context/seed/distance/count/cache/provenance tables. |
| [Supervised interface learning versus task success](root-interface-sft-live-2026-09-09/REPORT.md) | Four actual Adam updates; helper use0/24→24/24, but strict answers1/24→2/24 and final syntax19/24→9/24. All48 graphs clean. Most first actions copy the four-record example; only5.2% of supervised tokens teach final answers. |
| [Filtering baseline: independently checked primary results](typed-adaptive-operator-live-2026-09-09/PRIMARY_REVIEW.md) | Six jointly correct user-task pairs reduce helper calls48→6. Filter8/8 correct, all-file6/6 observed correct+2setupNULL; global3/8. No sampled root policy. Linked cache correction supersedes the original report's missing-cache sentence. |
| [Typed helper replies do not ensure complete answers](typed-helper-child-live-2026-09-09/REPORT.md) | Capped36-case test reconciles31raw records and28STATUS;27observable, nineNULL/unrun. Eligibletyped15/15 complete maps, but only1/3 associated roots correct. |
| [Adaptive RLVR scientific-source review](adaptive-rlvr-source-review-2026-09-09/REPORT.md) | No material defect found in bounded independent integration review and CPU probes: native likelihood/root-only masks, typed-child exclusion, fresh Adam then persistent recovery, fixedfinal8. Not an outcome claim. |
| [Matching IDs work in either field order](output-cue-order-live-2026-09-09/REPORT.md) | All48 outputs valid. Matching-ID advantages persist when label precedes ID:46.1points on TREC and32.8points on SST versus ordinal tags. Current ID immediately before current label is not necessary; no field-order equivalence or internal-mechanism claim. Two exposed contexts/task. |
| [Matching IDs on a new news task and two weights](agnews-identity-live-2026-09-09/REPORT.md) | All96 outputs valid; matching IDs beat ordinal tags by42.6–47.3points on four new AG News contexts with original and historical SFT weights. The benefit is not dependent on helper SFT. Component package effect, not whole-RLM improvement. |
| [Planning pilot: prerequisite failures](adaptive-filter-live-2026-09-09/REPORT.md) | All40physical/48logical outcomes audited. Filtered user success coverage3/8, full-file0/8, free0/16. Free roots never use children;21/44 attempted operator-child sessions end in parsed-empty replies despite nonempty generation. No clean matched-success planning/efficiency contrast. |
| [Restoring helper use does not restore accuracy](receipt-uptake-live-2026-09-09/REPORT.md) | All96 observed. Some real helper use, but only61/127 matching invocations return complete maps;65 parsed-empty and one request error. Root can also mishandle complete correct maps. Neither interface teaching nor procedure restoration establishes an answer gain. |
| [Helper-role wording pilot](child-role-suffix-live-2026-09-09/REPORT.md) | Final2/8→2/8, one gain/one loss. No child tool loops in either arm; the motivating mechanism did not reproduce. Three equal-prefix/seed pairs differ before child treatment. |
| [Broader training: completed fixed-final comparison](root-broad-equality-continuation-live-2026-09-09/REPORT.md) | Original13/48→final16 16/48, eight gains/five losses, all96 transfer episodes admitted. The64-record composition comparison is flat5/24; both models fail all four256-record cases. All16 root-only updates verified. A modest, uneven gain, not broad decomposition learning. |
| [Broader training: closer counts and contrasting examples](root-broad-posthoc-examples-2026-09-09/REPORT.md) | Post-hoc: among24 both-numeric pairs, mean absolute count error4.625→0.875 (nine closer/two worse). Numeric coverage31/48→38/48; exact primary stays13/48→16/48. Four outcome-selected trace pairs distinguish request serialization, batch/return-format errors and completed wrong counts. Not a prevalence or causal estimate. |
| [Matching IDs survive disjoint numbers and prefix swaps](identity-factorial-live-2026-09-09/REPORT.md) | All384 calls valid. Disjoint matching IDs beat counters by47–53points for question types and about35points for sentiment; all four context sums/task/prefix favor matching IDs. Numeric overlap explains part, not all, of the gap. Same exposed contexts; component accuracy and aggregate counts remain distinct. |
| [Recovered first reward-training update](root-broad-equality-continuation-live-2026-09-09/REPORT_STEP1.md) | Actual Adam1/nonzero root update,15 retained episodes and8141 root-only action tokens independently checked. Original40episodes/zero-update STOP remain separate; no rerolls or broadened admission, and no performance claim from an optimizer check. |
| [Broader training through update4](root-broad-equality-continuation-live-2026-09-09/REPORT_STEP4.md) | Validation4/16 versus original5/16,2gains/3losses. All16 new cases observable; root-only updates and training guards independently checked. Different per-round training contexts are not a matched learning curve. Fixed final16 remains primary. |
| [Broader training through update8](root-broad-equality-continuation-live-2026-09-09/REPORT_STEP8.md) | Validation9/16 versus original5/16,6gains/2losses; gain at32records,64 unchanged. Actual Adam/masks/guards pass.112 new episodes/1438returned physical calls; one kernel/ACP null excluded. Later all-one16/32 groups give no gradient despite high reward. Interim only. |
| [Broader training through update12](root-broad-equality-continuation-live-2026-09-09/REPORT_STEP12.md) | Validation8/16 versus original5/16 and update8 9/16:4gains/1loss versus original. Genuine Adam9–12 and guards pass;95/96 new training attempts admitted,55 selected. One pre-model installer timeout remains null.1,208 returned requests; interim, not monotonic or final transfer evidence. |
| [Answer-distribution controls](answer-distribution-controls-2026-09-09/REPORT.md) | Earlier final-set constant-zero0/24 and best evaluation-informed single count4/24 cannot explain15/24 or16/24. Does not exclude category/context shortcuts; documents skew in small broader evaluation strata without reading their outcomes. |
| [Broader curriculum: zero-update export stop](root-broad-curriculum-live-2026-09-09/REPORT.md) | All40 initial episodes audited; no optimizer update. Exact-full-context child rejection was unrecognized. Four excluded episodes consumed670/862 physical calls;520 later planned episodes are unattempted, not model failures. A separately prepared continuation preserves the original STOP. |
| [Independent root-training seed](root-independent-seed-continuation-live-2026-09-09/REPORT.md) | Completed continuation from exact saved weights/Adam/random state. Original9/24→selected update6 15/24,11 gains/5 losses;4 of6 contexts improve. All8 updates saved, but update8 was not evaluated. Second positive training direction on the same exposed contexts, not confirmation of general decomposition. |
| [Randomized source IDs and position counters](identity-counter-live-2026-09-09/REPORT.md) | All96 outputs valid. Source-matched tags score95.6%/93.8% on question/sentiment labels versus28.0%/49.3% for position counters at similar output cost. |
| [The counter reused source-ID numbers](identity-counter-live-2026-09-09/POSTHOC_NUMERIC_ID_REPORT.md) | Explicitly posthoc: matching ordinal outputs by source numeral gives83.9%/93.1% agreement. This diagnoses wrong-source interference, not repaired task accuracy; the completed384-call disjoint-number control above narrows the explanation. |
| [The new helper interface was not used](receipt-ablation-live-2026-09-09/REPORT.md) | Unchanged21/24 versus0/24 for both new interfaces. All72 observable and440 native attempts linked. Neither new arm invoked the helper, so consumed-receipt benefit is untested. New prompts also removed a familiar procedure; next test targets interface uptake. |
| [Root reward-training result](root-continuation-live-2026-09-09/REPORT.md) | The completed eight-update run improved from 5/24 to 16/24 on matched evaluation cases while the child model stayed fixed. There were 13 gains and two losses. This is promising exploratory evidence from one training run and six context groups, not a replicated general result. |
| [Training changes which instruction works](root-contract-factorial-live-2026-09-09/REPORT.md) | On fresh sampled runs, ordinary instructions scored 6/24 for original versus 20/24 for trained weights. The return-type reminder changed these to 9/24 and 14/24. The trained advantage appeared again, but the instruction helped one model and hurt the other. Same six contexts and trained checkpoint, not a new training replicate. |
| [What changed in the first root request?](root-first-action-screen-2026-09-09/REPORT.md) | Shows fewer malformed tool requests after training and recovers provider cache counts omitted from higher-level usage. This is a posthoc explanation screen on the same cases, not independent evidence or a causal mechanism test. |
| [Correction: the tool opener was sampled, not supplied](root-first-action-screen-2026-09-09/PREFILL_CORRECTION.md) | All48 saved first physical requests end with only the assistant-role header; every completion samples its own tool opener. The task supplied instructions and a worked example, not a prefill. Existing syntax counts and final gains are unchanged; the original report's prefill sentence is incorrect. |
| [Explicit output IDs across two tasks](anchor-indexed-followups-live-2026-09-09/ANCHOR_REPORT.md) | On identical ID-bearing inputs, returning IDs with labels substantially improved large-batch question classification and sentiment classification. Every output was valid in both conditions. This is a child-model format comparison, not a whole-RLM result or a trained-ID result. |
| [Does specialized ID training add value?](anchor-indexed-followups-live-2026-09-09/REPORT.md) | The complete matched comparison found 373/384 for the earlier mixed-size-trained model versus 374/384 for ID-specific training on six long contexts. Both succeeded with IDs and failed as plain lists. No useful extra training benefit is established; all 624 matched readouts were independently audited. |
| [Grammar, training and placeholder controls](grammar-training-padding-controls-2026-09-09/REPORT.md) | All368 calls audited. With enforced structure, meaningful tags greatly outperform constant placeholders with similar output-token counts; changing-position cues remain a confound. Extra ID-specific SFT adds no demonstrated useful advantage over mixed-size training. Free tagged outputs were invalid, leaving their semantic contrast unavailable. |
| [A concrete root-consumption failure](root-consumption-example-2026-09-09/REPORT.md) | Shows how JSON text was mistaken for a list of labels. The program computed zero and the root faithfully reported it; the model did not directly see and ignore the child arrays. One illustrative case, not a prevalence estimate. |
| [Process-consistency screen](process-consistency-screen-2026-09-09/REPORT.md) | Explains why additional checks would impose a stronger task, rather than expose invalidity of the original successful counts. No reward change is promoted; missing evidence remains unresolved. |
| [Post-SFT controls](post-sft-controls-2026-09-09/REPORT.md) | Compares output format, question order, visible input, original versus trained weights, and sentiment-task transfer. Includes the original-weight comparison completed after the dossier cutoff. |
| [Computed-answer feasibility](mrcr-computed-commit-2026-09-09/REPORT.md) | Explains why six completed model episodes produced no explicit submission and therefore no commitment-versus-restatement result. |
| [Actual RLVR harness audit](actual-rlvr-harness-review-2026-09-09/REPORT.md) | Checks the executed loss and optimizer path and diagnoses the round-four exporter stop. |
| [Stopped root campaign](root-campaign-complete-2026-09-09/REPORT.md) | Accounts for three completed updates and the unavailable later evaluations. |
| [Core harness review](core-harness-review-2026-09-09/PARENT_SCOPE.md) | Documents the two isolated Responses-harness fixes, distinct from the experimental Prime/nano runtime. |

## Current execution

This index lists sealed analyses, not active processes or prepared work. Historical stopped runs,
original seals and additive continuations remain distinct. Consult the
[live queue](../RESEARCH_QUEUE.md) for current launch authority and status.

The original independent-seed attempt's infrastructure failure is preserved in
its [separate audit namespace](root-independent-seed-live-2026-09-09/METHOD.md).
It is not silently relabeled as successful when its additive continuation completes.

The completed root-training continuation and output-ID comparison have their own
namespaces and are not part of the old stopped-campaign report or fixed-cutoff
dossier. The later root result strengthens the evidence beyond what was available
at the dossier's 01:35 UTC cutoff; do not read its earlier uncertainty as the latest
status. Consult
[the live queue](../RESEARCH_QUEUE.md) for current execution status.

## Literature and new research decisions

The [AFK primary-literature snapshot](../ideas/2026-09-09-afk-literature-and-next-tests.md)
connects batch prompting and harness–weight adaptation to bounded comparisons.
The [output-slots and error-driven search note](../ideas/2026-09-09-output-slots-and-error-driven-harness-search.md)
records a pinned official HPD repository that contains no implementation yet,
proposed output-slot tests, and cautions about treating bootstrap resamples as new evidence.
These are dated proposals, not launch-ready jobs or successful reproductions.

The [complete-trajectories and correspondence update](../ideas/2026-09-09-complete-trajectories-and-correspondence-literature.md)
distinguishes richer multi-turn supervision from our short interface examples,
and positions output-ID work against earlier batch prompting. Each proposed
comparison is tied to a question and a compute bound.

The [publication-positioning review](publication-positioning-2026-09-09/REVIEW.md)
checks the leading findings against eight primary papers and official source.
The [runtime comparison](../ideas/2026-09-09-official-runtime-comparison.md)
separates existing RLM features from specific additions worth testing. Its pinned
reference acquisition does not upgrade any active experiment.

The [recent literature update](../ideas/2026-09-09-harness-weight-literature-update.md)
explains how new work on model–harness adaptation changes our novelty claims and
suggests specific comparisons. It is separate from the dossier's earlier cutoff.
The [binding and harness triage](../ideas/2026-09-09-binding-and-harness-literature-triage.md)
connects numeric interference to mechanistic prior work, records a source-only
official-code acquisition, and limits claims about generic harness co-adaptation.


The [child-call amplification evidence](../ideas/2026-09-09-child-call-amplification.md)
and [suffix-only pilot design](../ideas/2026-09-09-child-role-suffix-design.md) connect
observed expensive Python/package loops to a small permissive role-instruction
ablation. Selected examples are not a prevalence estimate or an intervention result.

The [new-context/fixed-weight component screen](../ideas/2026-09-09-identity-new-context-weight-screen.md)
prioritizes fresh source groups over more same-context controls. Its proposed
fresh-SST membership failed: only8 unused, unreserved groups remain. The explicitly
different [AG News replacement](../ideas/2026-09-09-agnews-identity-weight-screen.md)
is the completed96-call new-task/two-fixed-weight comparison reported above.
The
[correspondence-to-planning note](../ideas/2026-09-09-correspondence-to-query-sensitive-planning.md)
explains why matching labels to records and getting a global count right are
different, and connects that distinction to the proposed user-filter/global-count
screen. The completed screen exposes interface prerequisites, not learned adaptation.

The [source-cue timing proposal](../ideas/2026-09-09-output-cue-order-design.md)
tests whether a matching ID helps if its field comes before versus after the
prediction. Its48-request model run and independent audit are complete. It cites prior work on schema structure
and reasoning order rather than claiming generic field-order sensitivity is new.

## Reading conventions

The [semantic query-planning update](../ideas/2026-09-09-semantic-query-planning-literature.md)
connects the adaptive pilot to LOTUS, Larch and NL2Pipe. It records an inspected,
source-only official clone and distinguishes established query optimization from
our unresolved question of preserving local predictions through an RLM plan.


Reports state observations separately from explanations and recommendations.
Wrong answers, invalid outputs, setup failures and unrun cases remain distinct.
Repeated seeds or permutations do not create independent source examples.
An exact count can conceal cancelling item errors, and a good child model does
not automatically imply a good end-to-end RLM.

Analysis folders retain reports together with machine-readable counts, input
hashes, and verification scripts when applicable. Earlier interpretations stay
findable; revised interpretations identify what changed rather than rewriting
raw experiment evidence.
