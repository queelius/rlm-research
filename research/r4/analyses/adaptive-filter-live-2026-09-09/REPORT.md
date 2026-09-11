# Adaptive filtering: child-contract failures and root heuristics prevent a clean planning comparison

Completed terminal audit, September9,2026. **The filtered operator succeeds in3/8 user tasks; the full-file operators answer none; the free root succeeds in0/16 tasks and never calls a child.** This is primarily an interface/semantic-feasibility result, not evidence that a successful learned planner chose the wrong cost tradeoff.

The auditor did not author the adaptive scientific source, operator or scorer. Prior exposure was the independent source review, saved CPU qualification fixtures, frozen inputs and the separate uptake study. The main-authored [METHOD](METHOD.md) and preparation seal were unchanged; model outcomes were first read after the explicit terminal trigger and confirmed owned-service release. The implementer's `INDEPENDENT_PROJECTION` was not present when this audit ran and was not invoked. All40 stored per-episode derived endpoint/execution values agree with this independent projection.

## Completion and units

All40 physical executions completed: no unrun/censored coordinates, setup/incomplete episodes, endpoint replacements or provider errors. Eight shared global fixed executions have two logical references, giving48 logical cells but only40 observations. Only four128-record contexts are independent context clusters; two seeds and user/global questions are nested within them.

The exact512 TREC groups, public full texts,16 synthetic users/context,8 records/user, deterministic selection/user allocation and host labels/counts were independently reconstructed from the source partition and named exclusions. The source pool is leaf-training-supported and excluded from named prior root compositions—not globally unseen, semantic-near-duplicate-free or pretraining-clean. Source license remains unresolved. Root is fixed historical step8 `473210b1…`, child `c32de129…`; current broad/independent-seed outcomes did not select them. Actual native aliases, endpoint/base/config/binding, overlay hashes, graph/wire token arrays, logprobs and sampling agreed with the frozen contracts.

## Primary endpoints: null is not wrong

The declared strict endpoint requires the entire trimmed reply to be `Answer: N`, ASCII nonnegative digits. A completed nonempty malformed reply scores0. Empty/unanswered replies remain null. They are not silently treated as infrastructure failures or negative labels.

| Family / policy | Recorded | Observable | Correct | Wrong/malformed | Empty/null | All-planned success coverage |
|---|---:|---:|---:|---:|---:|---:|
| User full-file operator | 8 | 0 | 0 | 0 | 8 | 0/8 |
| User filtered operator | 8 | 3 | 3 | 0 | 5 | 3/8 |
| User free root | 8 | 7 | 0 | 7 | 1 | 0/8 |
| Global shared fixed operator | 8 | 0 | 0 | 0 | 8 | 0/8 |
| Global free root | 8 | 8 | 0 | 8 | 0 | 0/8 |

Filtered observed accuracy is3/3, but coverage is only3/8. Its attainable success-count range including nulls is3–8; full-file0–8; user free0–1. These are missing-outcome bounds, not confidence intervals. User filter-minus-full-file has **zero complete endpoint pairs**, so there is no measured paired accuracy advantage. Free-minus-filter has two complete user pairs, both losses; six remain unknown. All other fixed/free endpoint comparisons lack complete pairs. Global all16/filter16 references are identical by construction; their shared nulls are not empirical proof of accuracy equivalence.

Exact context/seed outcomes (two seed values in each cell):

| Context | User gold | Filtered reply | User free reply | Global gold | Global free reply |
|---|---:|---|---|---:|---|
| 00 | 2 | `Answer: 2`, empty | prose/code, `1` | 16 | `5`, `2` |
| 01 | 1 | `Answer: 1`, `Answer: 1` | `20`, empty | 18 | `7`, `13` |
| 02 | 2 | empty, empty | prose/code, `0` | 22 | `18`, `12` |
| 03 | 2 | empty, empty | `0`, prose ending `Final answer: 0` | 20 | `5`, `2` |

Both full-file fixed executions are empty in every context/seed. User gold skew still permits constant2 to obtain6/8; no positive adaptation claim should ignore this baseline.

## Fixed operators: useful labels sometimes arrive, but the whole contract usually fails

The24 operator executions attempted44 of136 planned child sessions. They stopped at the first invalid map;92 later sessions were never executed, not measured failures. Each session can contain multiple sampled turns:44 sessions produced72 physical child calls.

| Operator | Planned / attempted sessions | Complete native-matched maps | Empty map failures | Correct labels among valid maps |
|---|---:|---:|---:|---:|
| User full-file | 64 / 18 | 10 | 8 | 154/160 |
| User filtered | 8 / 8 | 3 | 5 | 24/24 |
| Global fixed | 64 / 18 | 10 | 8 | 154/160 |

All23 valid maps have exact complete duplicate-free canonical IDs and actual normal-stop native-return matches. They provide332/344 correct classifications conditional on valid output. That conditional semantic accuracy does not cover the failed/missing batches or establish a reliable end-to-end policy.

All21 failed maps have empty **parsed** content despite nonempty sampled output:19 normal-stop, two length-stop. A separately labeled post-outcome wire diagnostic found18 outputs emitting `{id, type}` label records inside `<tool_call>` delimiters, instead of the requested ID→label object or a valid function call. The remaining three attempt Python tool envelopes: one has an invalid JSON escape; two run to2,048 tokens without a closed tool block. No decoder repair, alternate alignment or rescued labels enter primary scoring. This is a child protocol failure, not an HTTP outage or zero generation.

All24 operator ancestry records corroborate a real child invocation parented by an operator invocation with no spawning model request; actual sampled root-call count is zero. No root likelihood, root action graph or RL-training credit is fabricated. Runtime-writable transcripts alone were insufficient: canonical requests were reconstructed from public records, matched against native prompts and returned answers, and reductions recomputed by ID.

**Linked success:** [filtered context00/seed0](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/runs/rlm-research-r4/sidecars/adaptive-filter-pilot-v1/outputs/attempt-001/rollout/episodes/f4faf296707e1f079c9752f566e21f35ab469372d5f43752262e00efa429f86f.json") requests only the eight target-user records. Child invocation `08afb737c51e4ffab1ecca178f6781e0`, terminal request `4e5a153adc2b4a01a4b8bf8eded3e3a8`, supplies8/8 correct labels; the independently recomputed reduction and final reply are2. This demonstrates one feasible filtered trajectory, not general reliability.

**Linked failure:** [full-file context00/seed0](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/runs/rlm-research-r4/sidecars/adaptive-filter-pilot-v1/outputs/attempt-001/rollout/episodes/16e56bd32b5a593fcf167763806d8f70e0f1e5c1bfb26396181102ceb244f5d3.json") obtains two16-record maps, then request `a89685721ac346988f40db0c6f7291fa` emits label records inside tool-call delimiters. The operator detects an invalid map and leaves its final answer empty. Its earlier useful work remains charged; the empty endpoint remains null.

## Free root: no child use, visible direct heuristics and output-contract failures

All16 free episodes have complete native capture and **zero child calls**, so this is observed non-use, not inference from missing logs. Forty root model calls are retained. Direct root computation was allowed and is not itself a failure. However, the visible code uses keyword heuristics rather than the capable child, sometimes mishandles metadata, and never produces a strict correct final answer.

Twelve final replies are bare numerals; every one differs from the host gold even before considering the missing `Answer:` prefix. This is an explicitly post-hoc descriptive check, not a relaxed score: repairing the prefix alone would not rescue these cases. Three other nonempty finals are explanatory prose/code; one parsed final is empty.

**Question neglect:** [user context01/seed0](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/runs/rlm-research-r4/sidecars/adaptive-filter-pilot-v1/outputs/attempt-001/rollout/episodes/29a9d2ae58fff96a73fd84478e982bc12364710a50db1c8f8a52a0c24115d60a.json"), sampled root request `7509f29cd7c7418c958b929d1e44d318`, reads all records and counts keyword matches without selecting the queried user. The actual tool observation is20; final reply is bare`20`, versus user gold1. No host execution of this sampled program was performed by the audit.

**Metadata recovery does not imply completed computation:** [user context00/seed0](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/runs/rlm-research-r4/sidecars/adaptive-filter-pilot-v1/outputs/attempt-001/rollout/episodes/23d5a500141b4d395ad73cdbdfdd8c71554c59c672abc788471b04ec24471a2c.json") first indexes `synthetic user` and receives a KeyError. A later tool observation explicitly shows actual keys `id,text,user` and a zero count; the final response offers corrected code in prose rather than executing it and submitting a count. Source-level intent is not counted as successful selection or consumption.

**Semantic heuristic error:** [global context00/seed0](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/runs/rlm-research-r4/sidecars/adaptive-filter-pilot-v1/outputs/attempt-001/rollout/episodes/aaacd5a14c90841ad7afadb43953cc3f54d6ccf9a0c490abd4a144a9edc2f732.json"), request `216fc5c484fe406b95c408471b785854`, applies keyword-priority rules to original question text. Tool observation5 and final bare`5` differ from gold16. This illustrates a semantic failure beyond final formatting; it does not prove all direct-root strategies are inadequate.

## Physical cost and timing

| Physical policy group | Root / child calls | Input | Action | Cached input | Uncached input |
|---|---:|---:|---:|---:|---:|
| User full-file | 0 / 31 | 45,144 | 11,558 | 41,264 | 3,880 |
| User filtered | 0 / 11 | 12,459 | 2,646 | 11,312 | 1,147 |
| User free | 24 / 0 | 36,497 | 4,580 | 33,760 | 2,737 |
| Global shared fixed, counted once | 0 / 30 | 41,283 | 9,992 | 36,176 | 5,107 |
| Global free | 16 / 0 | 24,016 | 5,664 | 23,792 | 224 |
| Union total | **40 / 72** | **159,399** | **34,440** | **146,304** | **13,095** |

All112 physical attempts have HTTP200 results, authenticated sampled tokens and known usage. There are no request-only tails, duplicate request-ID ambiguities, unassigned work or observed infrastructure errors. Wire finishes:110 stop,2 length. Retry capability remains inherited, but no extra retry is inferred from capability or from multiple turns within one child.

Filtering uses less total observed work than user full-file, but full-file usually aborts early and neither comparison guarantees a completed answer. Per context/seed filter-minus-full-file model-call differences are−3,−2,+1,+1,0,0,−13,−4. These are not a clean matched-success efficiency estimate.

Operation elapsed489.90seconds, scientific owned elapsed487.17seconds, collection status elapsed434.45seconds; no cap overrun and owned service release confirmed. Sum of concurrent physical call latency405.05seconds is not allocation wall time. Both null and wrong trajectories retain their costs; cached-token counts are actual wire usage, not GPU-FLOP estimates.

## What to do next

The evidence supports **qualifying the child-map interface and teaching environment/output competence before interpreting this as a planner-learning benchmark**. The three filtered successes show the scripted policy can work;21 operator protocol failures prevent a reliable all-versus-filter opportunity baseline. The free root also has distinct metadata, semantic-method and final-output weaknesses. A child-only repair would not fix those; root-only teaching cannot make an unreliable child contract reliable.

A separately declared interface warm start is reasonable to test—not established as effective. It should teach faithful metadata access, a real child request, strict map/coverage handling, and observable final reduction using native root tokens. Scripted operator traces remain demonstrations only if explicitly authored as SFT targets; their zero-root histories are never sampled RL likelihood. Any later terminal RL campaign needs valid competing trajectories; an efficiency reward is a new objective, not a revision to these outcomes.

Do not claim learned adaptation, an attention mechanism, a whole-RLM generalization gain, or an accuracy-preserving filtering speedup. Inputs are four exposed-by-this-run, leaf-training-supported contexts, and the user answer skew is strong. Keep held-out-query/length evaluation separate from these diagnostic cases.

## Artifacts and reproduction

[METRICS](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json") contains every primary logical pairing and null bound; [RAW_LEDGER](../../../../ARTIFACTS.md#unpublished-files "Not published: RAW_LEDGER.json") contains all40 independently projected executions and native/code/operator references; [PHYSICAL_ATTEMPTS](../../../../ARTIFACTS.md#unpublished-files "Not published: PHYSICAL_ATTEMPTS.json") counts the112 attempts once. [MECHANISM_SUPPLEMENT](../../../../ARTIFACTS.md#unpublished-files "Not published: MECHANISM_SUPPLEMENT.json") retains exact post-hoc empty-completion bytes, native hashes, free-root programs/observations and per-context cost differences. No model program was executed on the host.

The sealed runner executed once, exit0, with zero identity or author per-episode score disagreements. Ten focused CPU fixtures passed before outcomes. `supplement.py` produces descriptive tables only; it does not change the sealed score or labels. [SOURCES](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json"), the supplement's source inventory and [FINAL_MANIFEST](../../../../ARTIFACTS.md#unpublished-files "Not published: FINAL_MANIFEST.json") bind exact inputs/code/results. Parent400-path authority was reused honestly, with bounded source/data reconstruction—not repeated heavyweight model hashing per episode.
