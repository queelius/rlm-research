# Independent intermediate-checkpoint audit

Fixed24 returned 15 correct native finals from 16 planned tasks; fixed6 returned 4, fixed12 one, and fixed18 three. **Twelve of fixed24's 15 successes actually execute the requested operation on live child labels**; two have wrong user scopes and one reaches zero through an unrelated text predicate. Do not equate the 15 answer successes with 15 faithful computations.

## Scores and paired uncertainty

All64 free slots were attempted. The strict unchanged `Answer: N` contract is applied to authenticated native finals after the original outer-whitespace strip; no extraction, repair, reroll or missing-RESULT promotion. The 48 teacher-first probes are separate diagnostics.

| Fixed step | Correct / planned | Native available | Correct / available | Nonzero correct /13 | Native-answer bounds /16 | Equal-context operational mean |
|---|---:|---:|---:|---:|---:|---:|
| 6 | 4/16 | 10 | 4/10 | 2 | 4–10 | 25.00% |
| 12 | 1/16 | 2 | 1/2 | 0 | 1–15 | 4.17% |
| 18 | 3/16 | 5 | 3/5 | 2 | 3–14 | 16.67% |
| 24 | 15/16 | 15 | 15/15 | 12 | 15–16 | 91.67% |

Each policy has three zero-gold tasks; zero-correct counts are2/1/1/3. Always-zero therefore scores3/16. Bounded operational failure is0 when no answer returns, while the native-final primary remains NULL; bounds let those unknown native answers range from all wrong to all correct. These NULLs are not randomly missing observations.

For24−6, nine pairs have both finals: six wins, zero losses, three both correct; seven pairs include NULL. Planned operational difference is11/16=68.75 percentage points; conservative native-answer difference bounds are5/16 to12/16. Equal-context operational difference is66.67 points, with10 positive, one tied and one negative context. For12−6 no pair has two finals; for18−6 only two do (one both correct, one both wrong). Corresponding conservative difference bounds are−9/16 to11/16 and−7/16 to10/16. These are descriptive bounds, not confidence intervals or an abrupt optimization-threshold estimate.

Per-context cells below are **correct / available / planned**. Four dose-new contexts contribute two tasks each; the eight readout contexts contribute one each, so sixteen questions are not sixteen independent clusters.

| Context | 6 | 12 | 18 | 24 |
|---|---|---|---|---|
| dose-new-00 | 0/0/2 | 1/1/2 | 0/0/2 | 2/2/2 |
| dose-new-01 | 1/2/2 | 0/0/2 | 1/1/2 | 2/2/2 |
| dose-new-02 | 1/1/2 | 0/0/2 | 0/1/2 | 2/2/2 |
| dose-new-03 | 0/1/2 | 0/0/2 | 1/1/2 | 2/2/2 |
| readout-04 | 0/1/1 | 0/0/1 | 0/0/1 | 1/1/1 |
| readout-05 | 0/1/1 | 0/0/1 | 0/1/1 | 1/1/1 |
| readout-06 | 0/0/1 | 0/0/1 | 0/0/1 | 1/1/1 |
| readout-07 | 0/0/1 | 0/1/1 | 1/1/1 | 1/1/1 |
| readout-08 | 0/1/1 | 0/0/1 | 0/0/1 | 1/1/1 |
| readout-09 | 0/1/1 | 0/0/1 | 0/0/1 | 1/1/1 |
| readout-10 | 1/1/1 | 0/0/1 | 0/0/1 | 1/1/1 |
| readout-11 | 1/1/1 | 0/0/1 | 0/0/1 | 0/0/1 |

This is a mechanically operator/scope/zero-balanced **exposed diagnostic subset**, with new paired sampling seeds. “dose-new” is a historical context name: these records were executed in the preceding dose readout. It is not a fresh transfer panel. Selection used zero-gold quotas, not model outcome fields. Stage order18,24,12,6 is fixed and serial; checkpoint comparisons retain order/runtime confounds. No best checkpoint was selected and no equivalence claim is supported.

## Executed mechanisms, not host agreement

Actual child acquisitions occurred in0/6/14/16 endpoints at steps6/12/18/24, with0/52/73/21 physical child calls. More calls did not imply better state use. All32 available-endpoint program/observation sequences were manually reviewed. [SEMANTIC_CHECK.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SEMANTIC_CHECK.json") verifies the selected live map, requested scope, actual successful program node and its observed scalar without unioning different maps or executing sampled code.

- **Fixed24:** twelve requested live-label reductions (ten nonzero, two zero). One zero success recovers a missing-ID error by reacquiring the entire eight-record scope, then correctly counts its latest map; this is scoped reacquisition, not multi-batch accumulation. Coordinate `906f7fa3c1…` (dose-new-01 distinct-all) excludes actual useru0, removing an erroneous child-predicted entity and coincidentally restoring dataset gold2; the correct operation on the full actual child map would give3. `6d3aa39bad…` (readout-05 distinct-all) excludesu3, harmless on this instance but not the requested scope. `925b0aa684…` (readout-10 weight-single) prints two child maps while overwriting the return variable, then filters record text against the entire task instruction, yielding the zero-gold answer without using category predictions.
- **Fixed18:** all three successes are requested live-label counts. One wrong final follows eight two-record acquisitions that overwrite the same map, repeated KeyErrors, then replacement of labels by numeric weights compared with `'location'`. Another compares user IDs with record IDs/category strings, producing zero. A no-final path advances slices through `records[202:204]` on a32-record dataset, repeatedly printing empty maps.
- **Fixed12:** its only success correctly reduces the complete four-record user scope after undefined-helper/dict-attribute errors. Its other available final splits an entire child JSON answer by newlines and compares each whole line with `'numeric value'`, giving zero rather than2.
- **Fixed6:** no actual child call. The four successes comprise one missing-category zero and three heuristic text-based labelings (two nonzero); these are not acquired-label reductions. Other available answers similarly use text heuristics or assume a nonexistent category field.

This run does not establish robust multi-batch accumulation. Acquisition, correct requested computation, and final return are distinct. The all-scope coincidences show why matching a host-computed scalar is insufficient evidence of faithful computation.

Teacher-context first-action syntactic acquisition intent is1/12,5/12,11/12,7/12 at steps6/12/18/24; all48 requests return authenticated branches. These actions are sampled **but never executed**, so intent is not acquisition success. The higher intent at18 than24, alongside poorer free-task completion, argues against reading the score pattern as a simple monotonic first-action threshold.

## NULL causes and physical costs

The32 native NULLs comprise22 sampled malformed-tool endings (12 with `length`,10 with `stop`), nine attempted timeout paths lacking RESULT, and one IPython broker `_queue.Empty` failure after sampled programs whose causal attribution remains unresolved. Eight of the nine missing-RESULT paths end in recorded HTTP400 rejections with actual input prefixes8213–8318, exceeding8192; the retained evidence strongly supports policy-driven context exhaustion, not random infrastructure dropout. The ninth has73 physical attempts/35 child calls and times out without a recorded HTTP rejection. Endpoint failure receipts span181.07–186.20 seconds, including observed shutdown overhead. No deadline was extended and no failed slot rerun.

| Step | Free attempts | Returned free completions | Child calls | Known input tokens | Known output tokens | Usage-unknown attempts |
|---|---:|---:|---:|---:|---:|---:|
| 6 | 39 | 38 | 0 | 87,022 | 15,083 | 1 |
| 12 | 429 | 425 | 52 | 1,709,920 | 47,471 | 4 |
| 18 | 328 | 326 | 73 | 1,099,762 | 32,872 | 2 |
| 24 | 94 | 93 | 21 | 196,200 | 9,904 | 1 |

Add48 probe attempts/completions,51,580 input and20,782 output tokens. **Total938 physical attempts,930 returned completions; known3,144,484 input and126,112 output tokens, with8 attempts' usage unknown.** Reported cached input3,052,256 is a subset of input, not extra tokens. The eight rejected requests are physical attempts, not established GPU generations. Provider billing is unknown. The producer's field `http_responses=882` counts nonempty free response bodies, not all890 HTTP status returns; independent accounting retains all eight400 statuses.

One returned c32 completion in the fixed18 timeout has no typed-result receipt: its actual raw token/logprob branch parses and its usage is retained, but no successful state insertion or final is inferred. All other881 free completions have exact raw/typed request-body, token/logprob, content/tool and finish provenance matches. All882 raw free branches plus48 probes were independently rendered; all32 claimed free finals have unique full-body/token joins. Every root's first native prefix matches frozen input IDs, with actual2048 action cap,8192 service context,.5 temperature,1.0 top-p and paired frozen seed. Recognized optional children retain the common transport behavior; no root grammar was added.

Actual service model cards, descriptor, inference configuration and adapter/config hashes bind exact6/12/18/24 plus the same c32 child and pinned Qwen3-4B-Instruct-2507 base revision `cdbee75f…`. All phase release receipts report owned processes exited. Recorded metadata preflight uses model/version GETs, not extra sampled work. New training cost is zero; the prior optimizer/corpus acquisition is reused provenance, not recounted as physical work here. Owner elapsed1486.706s; outer exit0/not timed out at epoch1789020672.6160586,1488.552s within3300s. Stage elapsed18/24/12/6 is376.352/314.714/487.801/304.172s; do not sum nested clocks as GPU kernel time.

## Audit closure and decision

Outcome reading began only after MAIN's terminal relay. The outcome-blind METHOD was sealed after launch but before outcome reads, as already recorded. The original frozen checker confused typed UUIDs with provider IDs in an extra final join: its preserved PRELIMINARY is rejected, **not scientific zero availability**. [CORRECTION.md](CORRECTION.md), two passing regression fixtures and the additive reader document the exact-body/full-token correction. The partially written EVIDENCE.json from a JSON key-serialization failure is also retained; [EVIDENCE_V2.json](../../../../ARTIFACTS.md#unpublished-files "Not published: EVIDENCE_V2.json") is the complete current evidence artifact. No scientific source, old method, score contract or raw output was changed.

The final package links every planned coordinate to raw directories, complete available programs/observations, per-context results, costs and actual bindings. Source/method and outcome pins are freshly verified at seal. The reviewer did not implement this intermediate study; no sampled program or service was executed during audit.

This supports the fixed24 package's better bounded performance on these exposed primitive questions and identifies substantial operational instability at12/18. It does **not** locate an abrupt learning threshold or establish composition/multi-batch competence. The already planned scale/state and task-spec contrasts address the observed scope and accumulation failures more directly than selecting a best intermediate checkpoint or repeating a loss-only dose argument.
