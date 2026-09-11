# Fresh join worlds: file-only improves reachability/cost, not a resolved accuracy advantage

Across eight newly generated worlds, file-only(E) produced16/16 authenticated native finals and12 correct; inline+file(I) produced10/16 finals and9 correct. E's observed output tokens were7200 versus I's43772, with three additional unknown-usage I attempts. The strongest transfer is a packaging/strategy effect: E actually loaded the real file16/16, while I copied records into code16/16 and never loaded a file. Full-source join competence remains imperfect and order-sensitive.

## Shared strict primary and pairing

| Cell | Correct / planned | Native available | NULL | Planned correctness bounds |
|---|---:|---:|---:|---:|
| I/random |5/8|6/8|2|5–7/8|
| I/reverse |4/8|4/8|4|4–8/8|
| E/random |6/8|8/8|0|6/8|
| E/reverse |6/8|8/8|0|6/8|
| I total |9/16|10/16|6|9–15/16|
| E total |12/16|16/16|0|12/16|

All26 authenticated finals satisfy the strict sorted/unique/known-ID JSON-array format;21 are correct, five semantically wrong. No final has finish_reason=length. Conditional accuracy is I9/10 and E12/16, but neither this selected denominator nor operational9/16 versus12/16 resolves the NULL-sensitive accuracy comparison. The operational E−I difference is+3/16; with missing native outcomes unconstrained its correctness difference spans−3/16 to+3/16.

The eight worlds—not32 endpoints—are clustering units. Of ten same-world/order I/E pairs with both finals, I wins two and eight tie; E wins none. The other six pairs are not silently dropped from the primary. E has both orders correct in five worlds, both wrong in one, and opposite order-specific errors in two. I has both native finals only in four worlds; all four pairs are correct. Shared seeds do not make different prompt/observation trajectories identical randomness or equal compute.

| World | I/random | I/reverse | E/random | E/reverse |
|---|---:|---:|---:|---:|
|0|1|1|1|1|
|1|0|NULL|0|0|
|2|1|NULL|1|1|
|3|1|1|1|1|
|4|1|1|0|1|
|5|NULL|NULL|1|1|
|6|NULL|NULL|1|1|
|7|1|1|1|0|

## Actual computation, not file-name mentions

All44 authored-by-model tool actions were authenticated against actual native tokens and the immediate subsequent assistant/observation pair. Forty-one observations have exact physical continuation-token verification; three remain genuine retained tool outputs followed by pretransport context rejection. No sampled program was executed by the audit. Every program's control statements were inspected; large literal payloads were separately checked for record fidelity.

- E loads all48 real facts in every episode. Twelve execute source-supported correct joins on those complete facts and propagate the observed list to the final. Its four wrong finals are also actual computed outputs, not format failures. Four E episodes encounter NameError; two recover faithfully, two switch to fabricated data.
- I attempts record copying in all16 episodes and has observed syntax/JSON failures in eight. Nine execute correct grouping/intersection on copied data and propagate the actual output. Only six of those copies contain all48 records; three omit one record without changing this answer. World7/reverse omits queried N fact r72927/c9191 (customer lacks M); world3/random omits unqueried S; world4/reverse omits unqueried L. Thus correct scalar/list agreement is not full evidence preservation.
- All six I NULLs follow copy/repair errors: world1/reverse,5/reverse,2/reverse end in pretransport context overflow (8628,8493,9339>8192 respectively); world6 both orders and5/random have in-flight timeouts. Preserve these NULLs; the causal contribution of execution, queueing and provider latency to the latter three is not isolated. World1/random returns a wrong final after three failed programs, without a computed join observation.

The `valid_join_algorithm_executed` mechanism field means a valid **source-supported** join here, not merely a structurally valid algorithm on invented data. E world1's fabricated-data intersection is executable but not such evidence.

## Concrete order/repair failures

1. **World4 E/random:** action6728972d… loads evidence.dat correctly but repeatedly resets K/S buyer sets inside the record loop. It prints[] and returns[]. E/reverse's action7e37b584… eventually adds a complete accumulation pass and returns all seven true customers. This is both data-order and generated-program variation, not a controlled replay of one fixed algorithm.
2. **World7 E/reverse:** action3f619f29… reaches NameError after actual loading. Repair5dc361b2… records M buyers only as encountered and accepts N only if M appeared earlier. It returns c2998, missing c3713. Random-order action65a353a8… instead recomputes two complete sets and returns both. Equal6/8 aggregate scores hide these opposite reversals.
3. **World1 E/both:** after an uninitialized-set NameError, actions1002ec4d… / b0d953e9… replace loaded evidence with12 fabricated r1…r12 single-product records. A valid intersection on these invented records produces[]. The real gold contains seven customers. This is a failed error-recovery/state-use mechanism, not failed retrieval.

## Physical costs and closure

| Representation | Physical attempts / returned | Known input tokens | Known output tokens | Unknown-usage attempts |
|---|---:|---:|---:|---:|
| I |37/34|103863|43772|3|
| E |36/36|28010|7200|0|

There are76 logical calls,73 physical attempts and70 returned native completions; all are root calls, zero child calls/acquisitions. Observed cache tokens are0; missing usage remains unknown. E uses approximately6.08× fewer observed output tokens, not a measured equal-FLOP/billing comparison. Owner elapsed522.002s; collector481.833s. OWNER_TERMINAL is complete/released with no error, SHA `b3a008da275ee786b8aea73cc622693785c11b4e552b2bdfd3ea7602d1ec44a6`. All352 retained output files were pinned before outcome rescoring. Strict rescoring has zero producer disagreements.

## Scope, provenance and next decision

The method was sealed before launch (1789004987.326), parser post-launch but before reading outcomes (1789005282.959). Independent source checks regenerate all eight worlds/32 coordinates and native prefixes. Gold sizes8,7,8,5,7,5,7,2 arose without gold-conditioned resampling. Novelty covers customer/record IDs and facts against four explicit manifests only; familiar schema/operators and adaptive follow-up choice preclude a broad or confirmatory claim. I/E evidence.dat/query match within order, but context.txt also changes with inline visibility: this is a representation package. I contributed prior runtime/native plumbing and the motivating proposal, not this implementation/generator.

Observation helper ambiguity from repeated call_0 IDs was corrected additively after outcomes by exact immediate-turn/token verification; original helper outputs and all primary scores are unchanged (OBSERVATION_ADDENDUM.md). No source/output rewriting or rerun occurred.

Ranked next questions: (1) test faithful error recovery on genuine loaded-file/NameError states versus fresh starts, keeping real files available and no solution/gold hint; the fabricated fallback is a concrete remaining bottleneck. (2) test fixed generated join programs' order sensitivity via a separately authorized sandboxed/trusted mechanism design, or a new controlled operator study—this audit does not execute them. (3) replicate availability/copy costs on a different task/source family before promoting file-only as a general harness default. More purchase-world repetitions without a distinct mechanism contrast are lower priority.
