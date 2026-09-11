# Ledger16: partial totals encouraged stopping, not completion

The source-bound ledger was operationally delivered, but this small exploratory comparison worsened strict task success: **map-only 3/8, appended ledger 0/8**, with three paired losses, no gains and five ties. All16 episodes completed with clean native graphs; there are no NULL/unrun/censored outcomes. These are eight seed-pairs within four previously exposed contexts, not16 independent tests.

| Exposed context / global target | Map-only | Ledger | Paired mean difference |
|---|---:|---:|---:|
| validation-00 / NUM /32 records |1/2|0/2|−0.5|
| validation-01 / HUM /32 records |1/2|0/2|−0.5|
| validation-02 / ENTY /64 records |0/2|0/2|0|
| validation-03 / LOC /64 records |1/2|0/2|−0.5|

## What happened

All eight pairs had identical full initial native request bodies, task hashes, sampling/seeds **and sampled first-root action tokens**. Every first action queried the same four-record helper example. In the ledger arm, all eight then received a344-character appended summary with resolved=4, partial=true and28 or60 unqueried records, and all eight ended without another child call. Six produced a strict final matching that partial target total, not the global answer; two NUM cases produced non-strict explanatory text. More strict formatting (6/8 versus3/8) was not more correctness.

Map-only continued to complete delivered coverage in five cases. All five complete maps had the correct global target count and zero target false positives/false negatives; three ended with the corresponding strict answer, while two had non-strict final text. The other three map cases also stopped after the four-record example. No child used a multi-call loop: each of the29 child invocations made exactly one model call. The call reduction therefore reflects less root dispatch, not suppression of a child loop.

Concrete paired example: validation-01, seed981306021. Both roots first requested q0001–q0004. The ledger summary accurately reported0 human-being labels among those four, resolved4/32, unqueried28, partial=true. The next root response was `Answer: 0`; gold was6. The map-only root instead requested all32 records and returned `Answer: 6`. This supports premature use of a partial total in this selected example, not a defect in counting or transporting the returned labels. It does not establish an internal attention mechanism or general treatment effect.

Exact pointers: ledger episode `91979bfc44eb3ffc2c1a64328327b5c2b7eb5a1b13cc1e477da1d1f2a96f6408`, child request `dd2c0ff0f4554abd99c503daae30b925`, ledger event3, observation graph node6 physically precedes root node7. Paired map episode `c05b0c62d374be041086d79bb72546295beea5b0b772d329cf6dc64348992e0d` has the full32 child request `15d09fd9ed474ab0b1ee1ad667470287` and final root node11. Absolute raw paths and SHA256 values are in METRICS/SOURCES.

## Independent checks and limits

All67 captured native attempts match role/typed request hooks, returned HTTP200 responses and committed physical graph calls:38 root,29 child. All exact prompt/completion IDs, sampled logprobs, masks, .5/full-support sampling, seeds, aliases and efab-root/c32-child identities agree. Root grammar is absent; child maps use the fixed typed contract. All29 ledger child-result claims uniquely match source-bound native terminal maps and semantic child-return edges. Equal repeated IDs are deduplicated;24 repeated delivered IDs occurred in map-only, none in ledger, with no conflicts. Every actual original tool observation retains the qualified truncation behavior; none needed truncation here. All eight appended summaries are byte-exact, unsampled environment text physically included before the subsequent root call.

The JSONL ledger is root/runtime-writable and is **not** an independent authority. Cross-checks support native-produced, source-bound maps, broker-flushed delivery claims, semantic returns and actual model-visible summaries. `write_frame`/`drain` is not a caller-read acknowledgement; visibility plus matching final counts does not by itself prove causal reading or every Python state transition. Static assignment diagnostics retain AST missingness; no sampled code was executed by the auditor. The four exposed source contexts and two seeds limit generalization.

An audit-only JSON insertion-order defect made V1's eight `suffix_exact` flags false and downstream last-summary values null. Original METRICS remains intact. PROJECTION_AMENDMENT and OBSERVATION_PROJECTION_V2 independently verify the exact frozen runtime key order and correct only those observation projections. Seven focused tests pass, including the reproducing regression; no experiment source, outcome, answer, or score changed.

## Cost and next decision

| Recorded cost | Map-only | Ledger |
|---|---:|---:|
| Root / child native calls |22 /21|16 /8|
| Logical prompt tokens |49,344|25,962|
| Known cached prompt tokens |42,128|25,216|
| Root / child sampled action tokens |2,477 /2,078|794 /298|
| Returned completion tokens |4,555|1,092|
| Summed episode wall seconds (overlapping) |394.43|289.87|

Cache fields were present for all67 calls. Collection elapsed181.735s; scientific owned run233.247s; accepted child process233.766s, exit0/no timeout, owned service released and no remaining GPU PIDs. These are overlapping accounting dimensions, not additive GPU time. No unreturned or uncommitted hook attempts were observed.

The next informative comparison is map-only versus always-visible counts versus **coverage-first summaries that withhold class totals until full unconflicted coverage**, optionally crossed with the completed success-trajectory SFT root. Keep source data, child, first prompts and budgets fixed; do not force completion or repair answers. This tests a concrete presentation/plan interaction and whether richer root training changes it. It is not yet a validated harness improvement.

Artifacts: METHOD/METHOD_READY (frozen before any outcome access), METHOD_INPUTS (768 source/input paths authenticated once), EARLY, METRICS, OBSERVATION_PROJECTION_V2, SOURCES, SOURCES_V2 and SEAL. No GPU/model calls, process actions or accepted-source changes by this audit.
