# Typed operators24 — IMPLEMENTER analysis

Filtering preserved the correct user count in all eight cases while using substantially less child inference. However, the apparent8/8 versus6/8 planned-success difference is entirely two all-record setup nulls, not two observed semantic wins. Main's independent reconstruction of the primary endpoint is still required: this author implemented the experiment.

The prospective METHOD was sealed before outcomes, SHA `69ec83d889de0d977d70704d88ada7a2db7d4dc2f95a3bd3eac76c7105c66f3e`. All24 frozen physical coordinates were recorded;32 logical references include the same eight global executions twice. There are four exposed context clusters, each repeated with two fresh seeds—not32 independent trials. Exact READY/SPEC were authenticated once before outcomes; raw file bindings are in RAW_MANIFEST.json.

## Primary endpoint and infrastructure

Whole stripped ASCII `Answer: ([0-9]+)` was rescored from raw episodes against host gold, with no repair. Empty/missing answers are NULL. All22 nonempty replies were valid terminal syntax; five were wrong counts. Raw scoring agrees with stored scoring24/24.

| Physical arm | Planned | Correct / observable | Null | episode.ok | Finalize timeouts |
|---|---:|---:|---:|---:|---:|
| User all16 | 8 | 6/6 | 2 | 2 | 4 |
| User filter16 | 8 | 8/8 | 0 | 4 | 4 |
| Shared global all16 | 8 | 3/8 | 0 | 0 | 8 |

The frozen endpoint permits a completed nonblank answer despite a later task-finalize error. Therefore22 raw-observable replies are NOT22 clean episodes or training-ready graphs: only6/24 have episode.ok=true. Sixteen task finalizations timed out under the15s cap. Both NULLs are context2/user-all, one per seed: harness setup timed out during the role overlay, before any child request; episode wall times163.47s/164.59s include lifecycle work outside the120s setup stage. There is no missing planned episode, budget censoring, or child-map protocol failure.

Paired user results: six jointly observable pairs tie correct; two pairs have filter-correct/all-NULL; zero observed gains or losses. All-planned correct difference is+2/8 (+25 percentage points), a realized availability difference here, not demonstrated semantic improvement. Actual within-block dispatch order matches the frozen order; four concurrent blocks naturally interleave.

| Context (both seeds) | User gold | User all answers | User filter answers | Global gold | Global answers |
|---|---:|---|---|---:|---|
| 0 | 2 | 2,2 | 2,2 | 16 | 16,16 |
| 1 | 1 | 1,1 | 1,1 | 18 | 19,20 |
| 2 | 2 | NULL,NULL | 2,2 | 22 | 22,21 |
| 3 | 2 | 2,2 | 2,2 | 20 | 23,21 |

## Native maps and source correspondence

Planned child invocations136; observed120:48 user-all,8 user-filter,64 shared-global. The16 missing planned invocations belong exactly to the two setup-null all-record episodes. Every observed invocation has one captured native model request, a returned stop response, matching typed/role wire bodies, full prompt token IDs, correct learned-child alias, seed/temperature, exact source-bound request and requested-ID grammar. All120 IDs link to exported ACP calls; no orphan/request-only record or root model request was found. No visible additional invocation/turn suggests a retry; this is not proof against unlogged lower-level transport retries.

All120/120 answers are strict canonical maps with exact ID sets and returned source order. The preserved ordered-schema JSON/hash matches the invocation decision; the frozen hook checked actual pre-serialization wire key order. Saved JSON sorts object keys, so this audit does not independently recover original HTTP byte serialization. Decoded native prompts contain the exact contract request once; this is containment, not equality of the whole wrapped prompt to the bare request.

Raw runtime transcripts are available for10/24 episodes (52 batch claims); all52 uniquely match native request and answer records. Native operator-relation artifacts survive for6/24; these show no sampled root request/likelihood. Partial finalize export is a material provenance limitation, not evidence of absent child work. Native request coverage/source membership and aggregate counts were reconstructed separately: eight ordered16-record batches for each observed all-record execution, one exact8-record user batch for each filter execution. All22 reconstructed counts equal the actual final replies, including the five wrong counts. Root-writable transcripts alone are not treated as trusted provenance.

| Arm | Correct source labels | Query-user labels correct | Numeric false positives / negatives |
|---|---:|---:|---:|
| User all16 | 727/768 | 48/48 | 8 / 1 across all classified records |
| User filter16 | 64/64 | 64/64 | 0 / 0 |
| Shared global all16 | 980/1024 | 63/64 | 8 / 2 |

Per-context/seed classification and confusion rows are in METRICS and INFRASTRUCTURE_AND_GROUPS. These are repeated classification observations, not1,856 unique examples. All global count errors equal numeric FP−FN: the problem remaining after syntax repair is semantic classification, not arithmetic reduction. Other category errors can coexist with a correct numeric count.

## Physical cost

Shared global calls are counted once in the union:120 observed model requests,136,692 physical prompt tokens and16,737 completion tokens. All native prompt counts equal saved prompt-token-ID lengths. Cached-input usage is unknown for all120 calls; uncached-token totals cannot be claimed. Root physical requests/tokens are zero in captured records.

| Actual work, all planned rows retained | Child calls | Prompt tokens | Completion tokens |
|---|---:|---:|---:|
| User all16 | 48 | 55,258 | 6,931 |
| User filter16 | 8 | 7,786 | 568 |
| Shared global | 64 | 73,648 | 9,238 |

For the six jointly correct user pairs, all versus filter is48→6 calls,55,258→5,832 prompt tokens and6,931→428 completion tokens:87.5%,89.4% and93.8% reductions respectively. Mean episode wall time206.30→146.02s, with all six filter executions faster; startup/finalization/storage dominates enough that wall savings are much smaller than inference savings. These are observed paired costs, not a throughput guarantee or a randomized storage comparison. Across all eight user rows, mean wall times195.73s all and146.45s filter retain the null work. Summed concurrent episode time is4,420.12s, not campaign duration.

Operation exited0 at11:38:35.302UTC after1,210.547s; scientific terminal elapsed1,207.830s; collector wall1,154.777s. Owned processes exited, ports freed, GPU inventory empty; no cap overrun. The next SFT job is outside this audit.

## Interpretation and limits

This supports an operator-authored metadata-first decomposition as a useful efficiency baseline after child syntax repair: it classified the relevant eight records correctly with far fewer native calls/tokens. It does not show a learned root can discover or execute that plan. Both programs load the entire public records file; savings are in child classification, not host payload reads. All versus filtered children receive legitimately different semantic inputs; grammar constrains child actions, not merely wording, and does not validate labels.

User answers2/1/2/2 give constant2 six correct of eight, and selected subsets were especially easy; user accuracy alone cannot establish adaptive intelligence. Global variation exposes remaining classification/count errors. All four contexts are exposed developmental data with unknown dataset license. Missing finalize artifacts and the two setup nulls prevent stronger infrastructure or training-export claims. No checkpoint selection, output repair, reroll, source edit or new inference occurred during analysis. A local audit-only adapter mistake used `role_map.child` instead of the actual singleton `role_map.children` and was corrected before successful audit; no raw data or scoring changed. The frozen implementer projection ran once, then bounded raw checks produced the ledger and metrics. Independent primary review remains explicitly outstanding.
