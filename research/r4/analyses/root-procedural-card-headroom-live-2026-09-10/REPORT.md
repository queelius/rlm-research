# Procedural-card headroom48: limited but genuine operator uptake

The shared procedural card produced **7/24 strict answers versus3/24 control**, but the more informative result is **six genuine requested computations versus zero among available finals**. Four card computations were correct; two correctly reduced actual child predictions but were wrong against dataset labels. Three other card score successes and all three control successes were wrong-operation/scope coincidences. The card therefore shows bounded prompt-level procedural headroom—not seven faithful solutions, learned composition, primitive preservation, or broad task competence.

This analyst authored the experiment and this outcome audit; author-analysis overlap is explicit. MAIN independently reviewed source and will check outcomes. METHOD_READY `fc1dc117…` was frozen09:14:24.406UTC, before actual launch09:19:13.182UTC. Outcomes were opened only after MAIN's terminal relay. All old sources, READY, method/parser and raw outcomes remain unchanged. No sampled program was reexecuted.

## Native primary results

| Arm | Correct/planned | Native available | Observed wrong | NULL | Native missing-answer bounds |
| --- | ---: | ---: | ---: | ---: | ---: |
| U original |3/24|18|15|6|[3,9]/24|
| P shared card |7/24|16|9|8|[7,15]/24|

Available-only accuracy is16.7% versus43.8%; planned operational correctness is12.5% versus29.2%. These answer different questions. The observed planned difference is+4/24; native missing-answer difference bounds are[−2,+12]/24. Among13 jointly available pairs:4 favorP,0 favorU,1 both correct,8 both wrong;11 pairs include NULL. Missingness is not assumed random. All48 were attempted;42 have RESULT. One available U final is `Answer: True`, an authentic malformed final scored0, not NULL or extracted as1. All33 other available finals satisfy the frozen scalar format.

| Requested family,8/arm | U correct / available | P correct / available | P genuine requested computations |
| --- | ---: | ---: | --- |
| Users with A-weight total>5 |0/5|3/6|2 correct|
| Maximum per-user A-weight |2/7|1/5|1 correct,2 child-error wrong|
| B-weight among A-bearing users |1/6|3/5|1 correct|

U has0 genuine requested composed computations among18 available finals. Nonzero strict answers:U2/20,P6/20; zero answers:1/4 each. All four genuine P successes are nonzero. Zero and best-constant baselines were frozen at4/24 and6/24, respectively; no zero filtering occurred.

All eight exposed contexts remain, each with three queries. Entries are strict correct/native available (planned3):

| Context | U | P |
| --- | ---: | ---: |
|00|0/3|1/2|
|01|0/1|1/1|
|02|0/2|2/3|
|03|1/3|1/3|
|04|1/3|0/2|
|05|0/2|1/1|
|06|1/1|1/2|
|07|0/3|0/2|

Operational context means improve4/8, decline1, tie3. These are eight clusters, not24 or48 independent observations. Three contexts contain the four faithful-correct endpoints; five contain the six faithful computations.

## What actually executed?

Manual annotations cover **all34 available finals**, not just successes. `EVIDENCE.json` retains every recorded program/observation, exact child maps and paths, labels versus source gold, and per-endpoint judgments. `CLOSURE.json` authenticates six complete child-map → actual program → observed scalar → native-final links. Host scalar agreement never assigns faithfulness automatically.

All three supplied procedures have at least one observed faithful implementation in P:

- **Threshold:** rows26 and29 form per-user totals, then count users whose total exceeds5. Row26 prints totals `{u0:7,u1:7,u2:0,u3:6}`, then3. In context02, P row29 returns1 after grouping; paired U row28 returns pooled9 **on the identical complete child map**. Partial uptake also occurs: P row30 groups but sums qualifying totals rather than counting users (coincidental0); row38 groups/counts correctly over four categories instead of the requested human-being category, after a repaired TypeError. P row25's unavailable trace attempts grouping/counting but loops on a `record` NameError; this is not successful execution.
- **Maximum:** P rows2,41,45 actually group A-weight by user and take the maximum; outputs9,2,10. Only row45 is dataset-correct. Row2's child calls “What is after death?” numeric instead of entity, adding weight4 to u0 and moving maximum8→9. Row41's child misses the human-being label for “Who is the Incredible Hulk in reality?”, moving maximum9→2. These are faithful wrong answers, not operator failures. Paired P41/U40 have the same complete predicted map; P takes maximum2 while U pools4. The implementations do not demonstrate an empty-map default; the relevant observed maps are nonempty.
- **Conditional:** P row14 retains the full original labels, obtains location-owner membership, selects numeric records belonging to those owners and sums each once, yielding1. Extra subset child calls do not replace the retained full label variable. P row37 also implements membership-conditioned weighting but restricts A-owners to u1..u8, omitting actualu0: conservatively a wrong-scope coincidence8. P row33 prints an A subset but never uses it to filter the B sum; its3 is a coincidence. P row13 compares user IDs with category strings and reverses category roles, yielding0—not successful conditional computation.

These patterns are consistent with partial uptake of the instruction/context package. Neither keywords nor the card's guaranteed presence prove causal mediation for an individual endpoint. Other P executions still pool weights; U had no genuine requested composed final computation on this sample. The treatment's six faithful reductions versus none in U is the relevant exploratory process signal, distinct from score differences and availability.

The remaining strict coincidences are explicit: U16 uses hard-coded u3/u4/u5 rather than deriving A-users; U19 pools an empty target set rather than maximizing; U44 pools all numeric weight rather than maximizing. **U44 does genuinely accumulate two8-record child batches through `record_map.update` and uses both in the pooled result.** This is real state retention but the wrong requested operation. It must not be promoted to correct composed multi-batch reasoning—or erased to claim no accumulation anywhere. P30,33,37 account for all three non-faithful P successes. No available endpoint's requested semantics remain unreviewed.

## Failure and physical-cost closure

The14 NULLs comprise7 sampled malformed-tool/no-final paths,6 timeout failures after root context rejection, and1 unresolved broker `_queue.Empty` after repeated singleton decoder misuse. All six missing RESULTs were attempted, not unrun; their last rejected root inputs had8271,8528,8211,8319,8406,8291 tokens. They timed out around181.1–181.6s. Retained actual request histories show repeated empty-map reconstruction/KeyErrors, treating NDJSON as one JSON document, malformed generator syntax, reusing one child response for two ID sets, a grouping NameError, and fabricated category/type fields. These are policy-induced looping/context-exhaustion paths with transport manifestations, not random exogenous availability losses. The broker timeout's ultimate cause remains unresolved.

Other notable failures: P row1 repeats an incomplete triple-quoted print58 times, never acquiring a child; P row9 repeatedly overwrites8-record responses then validates against all16 IDs; P row42 makes24 four-record child calls without completing a retained full map or final. The card neither fixes retention nor guarantees acquisition. Observed native-final NULL stays NULL; operational non-return is unsuccessful.

| Arm | Physical root / child / total | Returned choice completions | Known input / output / cached tokens | Unknown usage calls |
| --- | --- | ---: | --- | ---: |
| U |219 /50 /269|266|789386 /25089 /740400|3|
| P |284 /58 /342|339|1193895 /30638 /1143856|3|
| Total |503 /108 /611|605|1983281 /55727 /1884256|6|

All611 attempts received an HTTP response;605 had authenticated native choice completions, six were HTTP400 rejections. All108 child calls returned. Acquisition endpoints were U24/24 versusP21/24. Unknown usage is not zero, and rejected attempts are not established GPU generations. Billing/FLOPs are unknown. Physical repeats remain separately counted; no orphan returned native completion or unplanned physical directory was found. Historical training cost is not new evaluation inference. SUITE_PREFLIGHT queried model metadata only, not a sampled generation.

All605 typed/native records match exact request body and full prompt/completion token/logprob identity and model alias. Repeated identical-seed child bodies sometimes have identical token/logprob returns: their physical occurrences are additionally resolved by the typed response provider-ID matching the raw provider-ID. The UUID namespace remains distinct. `FULL_BRANCH_JOIN_NOTE.md` records this additive all-branch refinement; the frozen34-final reader and scores did not change. Malformed tool-argument strings are compared raw, never repaired or executed by this audit.

Actual served fixed24 adapter is `94022838…`, c32 child `c32de129…`; model directories/configs, actual endpoint binding and8192 context configuration are checked. All48 root first-prefixes and2048/.5/top_p1/paired seeds match frozen requests. Task setup reproduces every original file byte in both arms; only P's prompt appends the exact183-token card. Source records/queries and128 groups were already exposed by composition/interface studies and child training/catalog; no fresh-data claim. Owner complete/released, elapsed684.182225s, SHA `89825c21…`; parent exit0 at epoch1789032637.861325, outer684.673128s, released GPU. No timeout extension or rerun occurred.

## Decision

Promote only the narrow claim that a short explicit procedure card can sometimes redirect this fixed checkpoint from pooled substitutes to genuine grouped/conditional operations. Do not promote general composition, learned competence, primitive non-regression, no-NULL efficacy, or reliable state retention. The two faithful child-error failures argue for keeping evidence quality separate from operation use. A contemporaneous U/P replication on predetermined operator-separating counterfactuals is informative if an offline separation gate succeeds; that is a new exposed diagnostic challenge, not a repaired score or unseen confirmation. No current reward or model change follows from this audit.

Artifacts: `NATIVE_AUDIT.json`, `EVIDENCE.json`, `CLOSURE.json`, prospective `METHOD_READY.json`, raw `OUTCOME_PINS.json`, and final `FINAL.json`. Per-entry indices above refer to the frozen48-row inventory in these files. Full raw paths and provider/typed identities are retained there.
