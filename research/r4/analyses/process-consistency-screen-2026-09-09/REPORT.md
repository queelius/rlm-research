# Process-consistency screen: insufficient evidence to promote a reward change

The screen does **not** establish hidden target-count cancellation. Every correct final answer with a complete auditable map also has correct target-class membership:25 development successes and6 readout successes, each with zero target FP and FN. Cancellation sensitivity is therefore **null**, not0% or100%. Missing/incomplete maps leave the other cases unresolved.

| Frozen sample | Development | Exposed readout |
|---|---:|---:|
| Completed episodes / source contexts |64 /4|48 /6|
| Exact final successes |25|10|
| Complete canonical maps |27/64 (42.2%)|16/48 (33.3%)|
| Exact successes with complete maps |25/25|6/10|
| Complete-map successes with target FP/FN |0/25|0/6|
| Auditable target cancellation cases |0|0|

Development comprises the original stopped campaign's first two32-episode collections; readout is the completed composition48 study,24 original-child and24 SFT-child episodes. The four development contexts contain256 normalized source-train question groups; readout contains384 source-test groups. Both normalized-text and group-hash intersections are0. Repeated tasks, seeds, rounds and child arms are nested in context—not112 independent contexts. The current live continuation and its future transfer were not read.

## What the extra checks do—and do not—show

The frozen diagnostic adds a hash-selected half-context target count and one hash-selected other-class count, computed by the host from the saved map. They are counterfactual questions, not new model answers. A correct target count does not require every other class to be classified correctly: these extra queries impose a stronger reusable full-map requirement. Failing them is **not** reward hacking, an invalid original-task success, or evidence that the root should have done more work.

Other-class label errors occur in24/25 complete-map development successes and4/6 complete-map readout successes. The extra checks detect14/24 and3/4 respectively; the half-context target query passes every such success, so all these detections come from the second-class query. Ten development and one readout incorrect full maps still pass both queries. The1 development and2 readout completely correct maps with correct aggregation receive no rejection; this tiny, partly definitional arithmetic check is not a reliability guarantee.

Concrete readout example `0a2967830123…`: the requested human-being count is correctly7 with no target FP/FN;61/64 full labels are correct, but the extra entity count is7 versus gold10. That is a failure of reuse for another question, not the question answered. Separately, the consistency check flags one already-unsuccessful episode `7eea21d9caec…`: complete child labels imply14 humans, matching gold, while the root submits0. This localizes an aggregation/submission discrepancy but does not improve discrimination among original successes.

## Feasibility and evidence boundary

Map-extraction coverage pass/fail/unobservable is27/9/28 in development and16/13/19 in readout. Development gaps include23 episodes without returned child reports,5 with only unmatched source inputs, and9 with matched but invalid/incomplete evidence. Readout has19 without reports and13 with invalid/incomplete evidence. Original-child readout maps are complete in3/24 versus13/24 for SFT-child; all four original-child exact successes remain outside the complete-map subset. This selection limits every conditional result.

Only exact question-matched, equal-cardinality, canonical JSON reports were projected; no aliases, first-element extraction, generated-code execution, stdout guessing or invented labels. Consistent repeated reports are allowed; no batch size or number of recursive calls is required. A prior hand-audited cancellation example used malformed/partial outputs and root-specific extraction; it is not silently reclassified as a complete canonical map here. Low observability can reflect the narrow retained seam or efficient target-specific strategies, not necessarily bad execution or deficient instrumentation.

All791 returned reports were reconciled with actual sampled nodes, role aliases and bound weight identities. Every initial child question prefix matches its recorded caller-message hash. All952 native entry/terminal physical-prefix comparisons match actual generate request and response IDs without retokenization. There are53 raw internal-message/caller-dictionary hash mismatches at terminal continuations (30 native,23 ChatEval), retained explicitly; initial requests still match, and native physical comparisons independently pass. ChatEval has no equivalent native physical comparison in this audit. Evidence availability does not prove how the root consumed it.

Recommendation: do not promote this into a reward objective. The80% observability criterion is unmet, cancellation sensitivity has no denominator, and stronger-map failures change the semantic requirement. If useful in a later unchanged-reward run, add **optional verifier-side** stable record-ID lineage and an explicitly committed target-membership/evidence object when a policy already produces one; keep omission unobservable and do not demand a universal six-way map or prescribed recursion. A separate reusable-map task would need to state that stronger requirement prospectively.

Method SPEC was frozen before new raw readout scoring, and code/tests were sealed at02:19:29UTC; readout scoring occurred at02:19:35. This was not scientifically unopened: earlier analyses and hard-coded examples in an inspected parser had exposed these contexts/outcomes. Five focused CPU tests passed; no GPU/model calls, reward changes, training or live-source edits. New raw scoring plus source authentication took under1second; bounded preparation, verification and reporting stayed within30minutes.

Evidence: [SPEC.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SPEC.json"), [METHOD_SEAL.json](METHOD_SEAL.json), [INPUTS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: INPUTS.json"), [DEVELOPMENT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: DEVELOPMENT.json"), [READOUT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: READOUT.json"), [AUDIT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: AUDIT.json"), and [SUPPLEMENT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SUPPLEMENT.json"). The JSON retains exact source paths/hashes, per-record predictions/nulls, semantic node links, query definitions, tri-state results and separate original strict rewards. MANIFEST.json authenticates this report and the full analysis artifact set.
