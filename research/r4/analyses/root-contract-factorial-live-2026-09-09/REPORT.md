# Root-weight × return-type instruction: independent terminal audit

The reminder was not uniformly helpful: original-root exact success rose from 6/24 to 9/24, while step8 fell from 20/24 to 14/24. The trained root retained an advantage under both prompts. This is an exploratory result on six already exposed, child-training-supported context groups—not a demonstration that a known current string/list bug was fixed, nor 96 independent observations.

## Frozen comparison and primary result

The [method](METHOD.md) was frozen before new outcomes. Twelve existing transfer tasks, two fresh hash-frozen seeds per task, and six contexts give 24 matched coordinates in each cell. The only prompt intervention was: “The .answer field returned by rlm(...) is text, not a Python list. If it contains a JSON array, decode it with json.loads before treating it as a list.” Original `857a7ce6…` and step8 `473210b1…` used the same fixed child `c32de129…`, native renderer, sampling and episode budgets. Instruction arms were interleaved within each weight phase; original then step8 ran in separate services, leaving a weight/order nuisance.

| Root / prompt | Exact success | Valid but wrong | Malformed terminal |
|---|---:|---:|---:|
| Original / unchanged | 6/24 (25.0%) | 7 | 11 |
| Original / contract | 9/24 (37.5%) | 8 | 7 |
| Step8 / unchanged | 20/24 (83.3%) | 4 | 0 |
| Step8 / contract | 14/24 (58.3%) | 9 | 1 |

All 96 planned episodes completed and had observable terminals; none was operationally missing or budget-censored. Original prompt effect: +12.5 percentage points, with 7 paired improvements and 4 regressions. Step8 prompt effect: −25 points, with 1 improvement and 7 regressions. The weight advantage was +58.3 points unchanged and +20.8 points with the contract. The weight×prompt difference-in-differences was −37.5 points. These are descriptive matched estimates, not significance claims.

Each context below contains four matched coordinates; entries are successes out of four. Full context hashes and individual matches are in [METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json"), `primary.contexts` and `primary.matched`.

| Context | Original unchanged | Original contract | Step8 unchanged | Step8 contract |
|---|---:|---:|---:|---:|
| 1200 | 1 | 0 | 3 | 3 |
| 1201 | 0 | 2 | 3 | 2 |
| 1202 | 1 | 3 | 3 | 2 |
| 1203 | 2 | 2 | 3 | 3 |
| 1204 | 1 | 1 | 4 | 2 |
| 1205 | 1 | 1 | 4 | 2 |

The reminder reduced step8 success in four clusters and tied in two. Its original-root benefit occurred in two clusters, with one worse and three tied. Contexts and seeds are nested repeats, not new independent datasets.

## Behavior and cost: suggestive, not a causal trace explanation

Structured first-root tool calls were 15/24→20/24 for original and 24/24→24/24 for step8. The 9 and 4 original no-tool first responses ended with normal stops; no first response in any cell hit the length cap. Thus these first-action failures do not support a general token-cap explanation.

AST-observed `json.loads` occurred in 14→20 original episodes and 24→23 step8 episodes; unknown counts were 9→4 and 0→1. There were respectively 5, 7, 3 and 19 AST-unparsed code cells, retained explicitly rather than converted into marker absence. IPython syntax can be unparseable by Python AST without implying a runtime syntax failure. Direct `.extend(x.answer)` appeared in one original/unchanged episode, not a prevalent established mechanism. Root tool observations contained `JSONDecodeError` markers in 4→8 original and 3→7 step8 episodes; these can be caught/recovered errors and are not complete failure attribution. No observed `TypeError` marker establishes a widespread string/list failure. Static markers are not executed dataflow or proof of consumption.

All retained physical calls, including child calls and later truncated calls, are included:

| Root / prompt | Root + child calls | Logical prompt tokens | Cached subset | Action tokens |
|---|---:|---:|---:|---:|
| Original / unchanged | 47 + 141 | 200,888 | 181,136 | 32,030 |
| Original / contract | 57 + 179 | 264,425 | 236,624 | 47,809 |
| Step8 / unchanged | 55 + 307 | 344,357 | 322,208 | 26,786 |
| Step8 / contract | 76 + 246 | 370,713 | 340,688 | 51,968 |

Total: 1,108 calls, 1,180,383 logical prompt tokens, 1,080,656 cached tokens, 99,727 uncached tokens and 158,593 actions. Cache is a subset, not additional input. All wire cache counts were recoverable even though the inherited graph projection reported them unknown. The reminder increased action tokens about 49% for original and 94% for step8. Summed concurrent call/episode latencies are not elapsed GPU time. Later truncation counts were 6, 13, 4 and 12, retained without retry or reward repair.

## Integrity and operations

One terminal-only raw scoring pass authenticated planned coordinates, task/context/prompt bytes, episode hashes, raw terminal scores versus saved metrics, model bindings and seeds. All 1,108 wire prompt-ID sequences matched native inputs, and wire usage matched physical counts. No orphan or request-only attempts, or discrepancies in these checks, were found. [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") records 1,227 consumed-file hashes and 175 frozen source-closure hashes; raw evidence was rehashed unchanged. This is not a new complete causal-graph proof.

Collection, service startup and both verified releases finished in 1,064.10 seconds (17.73 minutes), well inside the 60-minute cap. The final service released at 04:28:38.692 UTC. The driver then retained scheduling authority while doing redundant CPU analysis. Parent interrupted only that exact CPU driver; the accepted job exited at 04:35:09.569 with code **−2**, not zero and not an inference failure. The 390.88-second (6.51-minute) post-release scheduling-lock tail was avoidable GPU idle time. The preceding 43.92-minute wait was for the prior GPU owner, not idle time attributed to this run.

The built-in `ANALYSIS.json` is absent. A [pre-outcome amendment](../../../../ARTIFACTS.md#unpublished-files "Not published: ANALYSIS_AMENDMENT.json") recorded this before independent scoring; built-in causal-proof fields remain null. The independent primary results above are available; no missing proof was manufactured. [SOURCES_ADDENDUM.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES_ADDENDUM.json") authenticates that amendment and the parent's CPU-tail decision separately from the already written raw-input manifest.

## Decision

Do not promote the reminder to a default on this evidence. Keep unchanged prompting as the working step8 condition; the reminder is a prospective intervention whose benefit depends on policy. The smallest useful follow-up is a paired replication of the step8 reminder contrast on fresh grouped contexts/seeds, with separate first-action and observed parse-error diagnostics—not output repair or an assumed string/list mechanism. For future runners, release GPU scheduling authority before independent CPU analysis and authenticate immutable phase closures once, rather than per episode. No frozen source, reward, generated program, live owner or queue was changed by this audit.
