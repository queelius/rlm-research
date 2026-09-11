# Root-only RLVR campaign: terminal three-update analysis

The eight-round campaign stopped after **three verified updates**, at about 01:00:13 UTC on 2026-09-09 (2,074.014 seconds / 34.57 minutes after launch). Round 4's export triggered the frozen native integrity stop. No fourth optimizer update occurred. This is neither a completed eight-round experiment nor a negative transfer result.

The only validation evidence remains initial **2/8 versus step 2's 3/8**: two newly correct, one newly wrong, one retained correct, four retained wrong. All eight first-root physical prompts and sampling objects match, but all eight first-root actions differ. The latest checkpoint, step 3, has **no validation score**. There is no SELECTION.json, final step8 checkpoint/result, or new-context transfer result. The planned original/selected transfer cells each had 24 coordinates; neither ran. Their scores and effect are null, not zero.

## Actual learning execution

| Update | Credited episodes / root turns / tokens | Actual Adam step | Gradient norm | Adapter delta L2 | Optimization seconds |
|---|---:|---:|---:|---:|---:|
| 1 | 28 / 63 / 23,130 | 1 | 0.12961346 | 0.14762313 | 59.732 |
| 2 | 20 / 41 / 11,091 | 2 | 0.13349472 | 0.13932442 | 30.214 |
| 3 | 20 / 46 / 14,399 | 3 | 0.14389445 | 0.11790219 | 36.168 |

Total: 48,620 credited root action tokens; 126.114 optimization seconds, distinct from service/rollout/serialization wall time. Step 3 has 504 actual Adam states with nonzero first moments, binds the exact step2 optimizer/RNG/policy, and its safetensor delta is independently reproduced. Root-only current-action masks and labels were checked against actual input IDs; prefix observations and child actions receive zero credit. The fixed child is still `c32de129…`; no child update occurred. All three update distribution guards passed. Steps 1/2 reuse the immutable earlier audit; step 3 and later collection evidence were authenticated once by the additive analyzer.

Last root checkpoint SHA256: `6cd68cb764ea1dc46f2e0adf1a5d692d53ebc12cd5e5ef9d9c6dbd7d949fffcb`. This is the **last committed** root, not a validation-selected root and not the fixed final step8 root.

Fresh-seed collections at root steps 0/1/2 produced 12/32, 13/32, and 12/32 admitted successes. These are unpaired samples, not a learning curve with matched trajectories. Round 3's five mixed groups supplied 20 episodes; two all-wrong groups (`00:0`, `00:1`) and one all-correct group (`03:0`) had no group-relative gradient. Their outcomes remain in the task scores. Round 4 produced 12 successes among 29 export-admitted outcomes, out of 32 planned/recorded episodes; report those denominators separately rather than silently treating three exclusions as ordinary wrong answers. No training GROUP was emitted for that generation and no salvage update was applied.

## Why three round-4 exclusions are not the same event

| Episode prefix | Task / seed | Observable outcome | Export admission |
|---|---|---|---|
| 07dfc161… | 01:0 / 1078367534 | Incomplete; no terminal, no strict reward | Excluded: duplicate/failed/incomplete trace |
| ca1caf2a… | 03:0 / 1032809284 | Completed, terminal-valid, strict **wrong**, with recovered ProviderError | Excluded: failed audit or actual trace model mismatch; triggers integrity stop |
| efde0052… | 03:0 / 1462724262 | Incomplete; no terminal, no strict reward | Excluded: duplicate/failed/incomplete trace |

The middle episode is not an unfinished run and its recovered error must not erase its observed wrong outcome in descriptive trajectory analysis. Equally, its exporter-null reward must not be replaced with zero for training eligibility. Its recorded native metrics have 73 calls, 64 recursive subcalls, and a valid but incorrect terminal; exporter integrity and terminal correctness are distinct. Current_literature owns the separate causal diagnosis of the failed-audit classification; this report neither duplicates that code audit nor claims a wrong-model routing event merely from the generic exception wording.

Round 4 records three ProviderError labels and one HarnessError label at the native episode-metric level, versus two call-level provider-error events in the independently reconciled role view. These are different counts, not interchangeable inference/retry totals. Inherited nano retries are a source capability; no extra inference duration/count is inferred from retry capability or long elapsed time. Idempotent replay may avoid inference. The sealed bounded retry note is `sidecars/mrcr-computed-commit-v1/RETRY_NOTE.md`.

## Orchestration and cost evidence

| Collection | Successful audited root / child calls | Root / child action tokens | Root / child length stops | Recursive episodes | Invalid admitted terminals |
|---|---:|---:|---:|---:|---:|
| 1 | 70 / 372 | 25,261 / 51,582 | 1 / 14 | 21/32 | 13 |
| 2 | 64 / 176 | 19,867 / 18,922 | 1 / 7 | 20/32 | 10 |
| 3 | 68 / 251 | 20,460 / 28,221 | 1 / 11 | 26/32 | 6 |
| 4, no update | 78 / 317 | 26,032 / 37,419 | 2 / 15 | 26/32 | 6 |

Round 3 has 319 successful audited calls and no provider errors. Round 4 has 395 successful audited calls plus two call-level error events; native metrics count 397 calls. Known successful token usage is retained even in the excluded episodes, not treated as zero-cost. Input-token totals in the structured snapshot are logical provider prompt IDs, not a claim of uncached physical compute.

Child outputs in round 3 comprise 240 JSON arrays and 11 non-JSON texts; round 4 comprises 283 arrays, 30 non-JSON texts, and four no-text outputs. These are parse shapes, not exact cardinality, semantic accuracy, or record coverage. Structured/executed root-tool totals are 36/36 in round 3 and 52/49 in round 4. Rising recursion usage and fewer invalid terminals are potentially interesting format/orchestration observations, but fresh seeds, changed trajectories, and the absence of later validation prevent attributing them reliably to learning. The earlier round-1 cost concentration in two wrong trajectories remains relevant, but no tail-cost intervention was made here.

## Decision-relevant conclusion and followups

This run demonstrates three genuine fresh-generation root-only updates with persistent optimizer state and a fixed child. It does **not** establish improved orchestration: the only paired validation change is one net success on eight trajectories, with no matched unchanged-policy replay, no evaluation of step3, and no new-context transfer. The separate pilot's 2/8 → unchanged 4/8 → post 2/8 is useful noise context, not a comparable campaign control.

Ranked followups, requiring a new explicit experiment rather than rewriting this STOP:

1. Use the independent integrity diagnosis to qualify recovered-error evidence/admission behavior before another training campaign. Preserve the observed completed wrong outcome and frozen exclusion separately; never fabricate missing logprobs or relax credit authentication to rescue this run.
2. If checkpoint quality is decision-relevant, predeclare a small paired original-versus-fixed-step3 evaluation with an unchanged-policy replay control and fresh seeds. Step3 must be designated prospectively as the last committed checkpoint, not retrospectively presented as validation-selected. This is a proposal only; no GPU calls were made.
3. For a later campaign, assess fresh-context transfer and terminal-valid correctness separately from coverage/aggregation and child-call tail cost. The already-prepared transfer contexts are root-held-out but child-SFT-train-supported; use that limitation explicitly. Three steps must not be represented as adequate RLVR training or a rejection of the eight-round learning hypothesis.

## Evidence and analyzer scope

`TERMINAL_METRICS.json` contains the concise structured result and exact excluded IDs. `snapshots/20260909T010428.775556Z/{METRICS,AUDIT,REPORT}` and per-stage/update `cache/` artifacts pin the full source/export/mask/checkpoint evidence. Snapshot audit identity: `ca50ca68338a4784ff7f5353e82b22181961eef5491bb5915052dc7f75636a17`.

The additive analyzer's three CPU tests passed (cache-once, null-safe pairing, earliest-tie selection/policy identity). It ran once and exited on STOP; no continuing watcher, experiment resume, GPU/network request, or input mutation occurred. First-two analyzer/results remain unchanged. Selection/transfer code paths were CPU-qualified but never exercised against real results because those results do not exist.

Minor snapshot presentation caveats, corrected explicitly here without mutating the frozen snapshot: the reused helper's absent-transfer placeholder says planned32, but the frozen PLANS specifies **24 per arm**; its empty paired counters are empty-set counts, **not a measured zero transfer effect**. `TERMINAL_METRICS.json` uses the correct counts and null effects. These do not affect any actual recorded outcome, checkpoint audit, or campaign execution.
