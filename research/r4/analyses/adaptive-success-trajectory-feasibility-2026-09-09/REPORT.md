# Complete-success training trajectory feasibility

There is enough evidence for a small **complete-success/recovery imitation package**: 27 verified training trajectories, 114 exact root turns and 15,256 supervised-action-token candidates. This is not evidence that the plans are efficient or that imitation will improve held-out performance. No training input has been exported and no model has been run.

## Fixed snapshot and result

The method was frozen before reading outcomes, after filename-only inspection identified committed rounds01–05. Only their80 training attempts were examined. Validation/query/length readouts and later training rounds were not opened. The hypothesis is posthoc; MAIN had disclosed four updates and midpoint validation2/8. The analyst authored shared collector components, so this is raw-evidence screening rather than an independent reimplementation of the harness.

| Round | Planned | Native-admitted | Strict successes | Confirmed reductions |
| --- | ---: | ---: | ---: | ---: |
| 1 | 16 | 15 | 4 | 4 |
| 2 | 16 | 16 | 6 | 6 |
| 3 | 16 | 16 | 5 | 4 |
| 4 | 16 | 16 | 11 | 10 |
| 5 | 16 | 16 | 3 | 3 |
| Total | 80 | 79 | 29 | 27 |

One attempt is a preserved runtime/trace-admission null, not a clean wrong training answer. All29 strict successes have completed clean native traces, valid source-bound typed child maps covering the entire query-relevant scope, zero target false positives/false negatives and no conflicting target membership. This rules out target-error cancellation in these observable successes. Wrong *non-target* class names occur in some global maps; they do not invalidate the count actually asked.

For27, individual static inspection shows the source scope, `strict_map` child returns and explicit target-label sum. The reducer's child calls are identified by actual semantic call edges; their union exactly matches the requested scope. Separately, the official physical branch containing the final root call matches its native/wire prompt and completion IDs. Its tool-observation node contains the computed integer subsequently submitted. Child return contents need not themselves be printed to the root model: the REPL can consume them and display the computed result. Semantic call edges were not mistaken for physical visibility. No generated code was executed.

Two remain provisional, not wrong or automatically unusable: `e398724d3d19…` has a complete child map and correct final4 but no explicit computed reduction; `dc1da5b04946…` sums a model-retyped32-entry literal map, whose complete copying lineage was not established in this bounded screen. Their exact pointers and reasons are retained in CANDIDATES.json.

## Diversity, duplicates and plan quality

Confirmed candidates cover7 training contexts and8 context-query pairs: train00/single_user1; train01/global1; train02/single_user4; train03/global6; train04/global3 and single_user3; train05/single_user5; train07/single_user4. Thus10 global and17 single-user trajectories are nested repeats, not27 independent tasks. There is no successful candidate from train06.

Their final-answer distribution is0:1,1:4,2:3,3:4,4:6,6:5,9:1,14:3. The29-success pre-gate distribution differs only at3:5 and4:7. Zero is therefore not dominant, but answers and strategies remain narrow. The original80 attempted queries were balanced40 global/40 single-user; outcome selection creates the new scope skew.

All27 candidates begin with the exact taught four-record helper cell. Fourteen contain visible tool-error indicators before recovery. There are27 distinct full root action sequences but26 distinct code sequences: one code sequence repeats with different action-token material. These are evidence-supported *successful trajectories with recovery*, not purified optimal plans. Keeping all root turns would teach the initial probe and recovery behavior as well as the successful final reduction. Removing those turns or choosing only short traces would be a different, prospectively specified intervention.

## Feasibility decision

Recommend a small fixed-step success-imitation comparison starting from the unchanged interface-SFT final4 root, with fresh Adam and the same frozen typed child. Use only the27 confirmed training trajectories; retain exact native teacher prompts/actions and mask child, environment and prompt tokens. The candidate manifest contains pointers and diagnostics only; it is not training-ready data. Fresh export must authenticate these exact pointers and preserve physical tokenization without manufacturing behavior probabilities.

Compare that fixed final checkpoint with the unchanged interface-SFT control on fresh paired seeds over the existing context-disjoint validation/query/length readout coordinates. Those readout tasks are exposed, not newly discovered test data. Freeze weighting, order, optimizer budget and readout seeds before preparation. Episode/turn balancing should be explicit because both task counts and trajectory lengths vary. This estimates a complete-success-imitation package; more tokens, different epochs and additional optimization prevent an isolated claim about example content.

## Evidence boundary

METHOD.md, SCREEN.json and SOURCES.json preserve the initial screen. CANDIDATES.json/METRICS.json and STATIC_REVIEW_SOURCES.json add the reduction/physical-visibility decision without rewriting it. Immutable campaign/source/export/raw closures were cached once; this screen does not repeat a tensor/Adam checkpoint audit. Native action/prompt/logprob equality and root/child admission are checked, not recreated. The small analysis script initially used the role-audit field name `native_response` for a typed-audit object; it stopped before publication and was corrected to the actual `response` field. This was an analysis setup error, not an experimental failure or data repair. No evaluation outcomes, source modifications, training exports, GPU operations or service locks were used.
