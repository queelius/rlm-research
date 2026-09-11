# Task-spec interface72: bounded design for MAIN review

Status: design only; no implementation, READY, source allocation, GPU or queue change. This is independent of warm-start/RL preparation and does not select a new checkpoint. Supersedes only the conditional follow-up suggestion in the earlier task-parameter inventory, not its source findings.

## Question and recommendation

**Can a discoverable, redundant machine-readable task description reduce fixed24's operator/scope substitutions, beyond merely restating the task in explicit prose?** Composition96 provides the trigger: all four correct SFT24 composed answers used wrong operators, all16 available composed endpoints lacked faithful composition, and the two faithful nonzero primitive successes occupied one context. There was genuine acquisition, so another label-map loader would not isolate this bottleneck.

Recommend **24 paired tasks ×3 arms=72 new endpoints**, using all eight current composition contexts and all three composed families (threshold-users, maximum-weight, conditional-weight). This is a deliberately smaller alternative to MAIN's full48-task ×2-arm96-endpoint candidate: it omits the24 primitive tasks by a family rule, not by model outcome or gold, and buys the important matched prose control. All24 composed tasks remain, including four zero golds and every previous failure. It tests the clearest observed operator failure and does **not** estimate primitive transfer. If full primitive coverage is required, retain all48 tasks and expand all three arms to144 endpoints; do not use historical primitive percentages as the missing control. MAIN chooses before implementation.

### Three arms, one fixed policy

| Arm | Additional task representation | Native prompt change |
| --- | --- | --- |
| U | None; current four files exactly | None: original accurate native coding role/question |
| P | `task.txt`: explicit prose field sentences | One sentence naming this redundant task description and plain-text format |
| J | `task.json`: JSON object with identical information/field order | Same sentence, naming JSON file/format |

Every arm has byte-identical original `records.json`, `context.txt`, `query.txt`, `batch_contract.py`, original question,16 facts/order and ordinary native role. Keep original query construction separate from the arm-added prompt so metadata never leaks into `query.txt`. P/J each adds one new file; neither replaces raw records, supplies predictions, restores state, computes or forces file retrieval. J−P is the primary representation contrast; J−U is the practical interface-package contrast; P−U estimates the effect of discoverable redundant explicit task wording/file affordance. The extension and serialization still bundle familiarity/discoverability and token differences; no pure-JSON or equal-token/FLOP claim.

Task fields are only `operator`, `category_a`, `category_b`, `scope`, `threshold`, `threshold_comparison`, all derived from the already public query. Use exact declared operator names `threshold_users`, `maximum_weight`, `conditional_weight`; the unchanged English question supplies their meaning. Scope says all records/all users (current usersu0–u3); null is explicit for inapplicable fields. P renders exactly the same values as prose (“Requested operator: maximum_weight. Category A: numeric value. Category B: not applicable. Scope: all records and all users. Threshold: not applicable. Threshold comparison: not applicable.”). For conditional weight, A/B are the categories already defined in the question; no selected users/IDs are provided. Threshold5 and strictly-greater comparison appear only where already instructed.

**Never include** Python expressions, formulas, group-by/join instructions, operator implementation/glossary, examples, batch sizes, algorithm/pseudocode, hidden targets, gold, acquired labels, prior outputs or correction history. No tools or decoder constraints change. c32 remains optional with the same typed acquisition route; reacquisition and non-typed requests remain legal and counted. The JSON is an input task specification, not a constrained answer decoder.

## Pairing, metrics and budget

Exact fixed SFT24 adapter94022838a64a530e1abc8daf6cd43502d8aec7d549b6bfec10dd4928b0ca9006, childc32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3; same base/native template and2048 action/8192 context. No training. Proposed master2026091900, seeds1901–1924 by context then family, identical across arms;59 prepared input-plan files scanned CPU-only, no collision through1924. Refresh that receipt before any freeze, not outcomes. Use preassigned balanced cyclic arm order across task indices and hash-fixed task order; one shared service, four workers. All arms are fresh calls—no baseline outcome reuse. Exposed exploratory replication, not pristine/confirmatory data or pretraining-unseen.

Primary source metric: strict native-final dataset success with all24 planned per arm, eight paired context means and NULL bounds. Mechanistic co-report: independently authenticated actual acquisition→parameter-faithful executed operator/scope→observed scalar→final. Correct wrong-operator coincidences remain primary successes but **not** faithful successes. Measure actual task-file retrieval and subsequent parameter use separately; imports/file-name mentions are not uptake. Native malformed answers0; missing RESULT/unverified/no-final endpointsNULL; no salvage into primary. Preserve all planned slots, failures, per-call/episode checkpoints and physical cost union independent of RESULT.

Freeze anti-coincidence diagnostics before new outcomes: for every task compute host truth and the values of the already observed wrong alternatives (pooledA weight, pooledB weight, A-record count, threshold on pooledA, as applicable). List equality flags without changing selection. Report nonzero tasks and tasks whose gold differs from the relevant simple alternative separately, plus trace-confirmed mechanisms. Actual child predictions may alter these equalities; calculate observed-map diagnostics only on authenticated complete/provably sufficient state, keeping semantic errors and actual overwrite order. No model-code execution or convenient union. The panel has20 nonzero/4zero; no gold-balanced filtering.

Proposed single-A10040GB inclusive cap **3900 outer /3870 owned /3720 work**:180 startup+3450 collection+90 harvest,150 release/emergency+30 outer margin. Existing180s episode caps and four workers imply a nominal3240s maximum across18 waves before startup/overhead; not a guarantee all endpoints return. Advance early, retain plannedNULLs, no reruns or deadline-driven task substitution. Observed composition96 finished1461s for both policies, but SFT24 alone made864 physical calls and20NULLs; do not extrapolate equal episodes to equal tokens/runtime. Expected20–55min is only an estimate.

## Minimal future implementation and decision

Reuse the corrected scale single-policy owner/physical ledger and exact composition native collector with explicit path/module aliases. Only generate redundant specs, extend setup by one file for P/J, append accurate discoverability sentence, and expand fixed plan to72. CPU qualification should prove original four-file byte identity, private-label mutation invariance, all72 actual first prefixes, JSON/prose field equivalence, exact owner→collector/service entry, and missing-RESULT accounting. No new framework, scheduler, loader, model or dataset download. This proposal is not implementation authority.

Evidence supporting further work: J improves faithful nonzero composed success across multiple contexts relative to both U and P, with observed task-file use and no availability collapse. If P≈J>U, prefer simple explicit task wording rather than crediting structure. If J merely fixes final syntax or correct-answer coincidence without faithful operators, do not promote capability. If both fail despite actual retrieval, a corpus/on-policy objective question remains—but that does not causally prove state-coverage deficiency. Do not use this panel to select a different base/checkpoint.

Read depth/provenance: full earlier parameter-inventory note; complete composition source/protocol and independent raw native audit, including all59 available endpoint programs and all37 available composed traces. No new literature claim. This differs from field/map clarity and canonical-source-loader studies: it changes query-parameter access, not category visibility or preexisting label/REPL state.

- Composition report SHA256 `80a955add6e0964ba1ef1ccd4308bad1a37ab267458e693b1fa466dbc64bdb90`.
- Composition FINAL_SEAL `4c27e028b5c247d5f00614d8fabe3135cb46896d54c6eb4f134881321eac5824`.
- Composition `ct_protocol.py` SHA256 `951e6e1c4f516427cebf621d7c43faa8e645dc756358c923b084336c2cbb351d`.
- Current scale READY (runtime reuse only) `d10c9bb2b7a5f1e8e0d5f3146f2ccc6124d6bbda4373ca6692007af932e119ac`.

Readiness blocker: MAIN design/panel/cap approval. No GPU readiness claim or new input allocation is made.
