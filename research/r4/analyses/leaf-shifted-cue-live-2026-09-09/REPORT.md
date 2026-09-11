# Shifted cues72: labels follow the forced source ID

Independent terminal audit, September9,2026. Sealed positional scoring is unchanged.
All72 planned calls were observed, strictly schema-valid and native-provenance matched;
zeroNULL, zero invalid, zero truncations. Every call stopped normally. This uses the
validation-selected c32de **research adapter**, not either released no-adapter checkpoint.

## Primary and separately declared named-record diagnostic

Each cell below has8 calls, four context clusters×two seeds,512 labels. “Shifted named”
is diagnostic only and does not replace shifted positional correctness.

| Task | Matching positional | Constant positional | Shifted positional | Shifted named |
|---|---:|---:|---:|---:|
| TREC |491/512 (95.9%)|230/512 (44.9%)|115/512 (22.5%)|487/512 (95.1%)|
| SST-2 |484/512 (94.5%)|309/512 (60.4%)|253/512 (49.4%)|483/512 (94.3%)|
| AG News |407/512 (79.5%)|194/512 (37.9%)|119/512 (23.2%)|415/512 (81.1%)|

Matching-minus-constant is +51.0,+34.2,+41.6 percentage points for TREC/SST/AG.
Matching-minus-shifted is +73.4,+45.1,+56.3 points. Both primary contrasts are positive
in every one of the24 context-seed pairs and every one of12 context means. Four
two-seed mean gains, expressed as additional correct labels out of64:

| Task | M−constant, four contexts | M−shifted, four contexts |
|---|---|---|
| TREC |31,33.5,32.5,33.5|46,48.5,43,50.5|
| SST-2 |26,14.5,24,23|33,28,24,30.5|
| AG News |25,29.5,24.5,27.5|36,36,33,39|

No array was completely correct on the positional primary:0/72 whole64. High average
classification accuracy is therefore not full-batch reliability. Two-seed totals also
agree closely: matching245/246 TREC,242/242 SST,204/203 AG; shifted named243/244,
242/241,208/207 respectively (each denominator256).

## Repeated labels do not explain the named alignment

The pre-outcome host-gold subset excludes every position whose displayed and shifted
named record have the same class. Across two seeds:

| Task | Disagreeing positions | Correct for displayed record | Correct for named record | Neither |
|---|---:|---:|---:|---:|
| TREC |398|3 (0.8%)|375 (94.2%)|20|
| SST-2 |264|17 (6.4%)|247 (93.6%)|0|
| AG News |380|24 (6.3%)|320 (84.2%)|36|

Named-minus-displayed is positive in all24 shifted calls. Per-context two-seed gains
are90/96/87/99 TREC;68/54/48/60 SST;75/71/68/82 AG (out of128 positions each).
The named accuracies approach matching's ordinary positional accuracies despite fixed
input order. This supports source-cue semantic following under the deliberately
conflicting instruction/schema package, beyond a generic varying-token benefit alone.

Gold marginal independent-label chance references range20.7–22.4% TREC,50.0–52.4% SST,
25.6–27.4% AG across contexts. These are descriptive, not independent random-assignment
tests. Full-array named scores can include same-class coincidences; the disagreement
subset exposes their influence without changing primary. Forced tags are supplied by
grammar: this does not demonstrate unconstrained ID retrieval or identify internal
attention. Shift17 contradicts “label the displayed record regardless of tag”; low
positional correctness is not rescued success at following that instruction.

Mean class-count L1 per valid64 array, matching/constant/shifted, is3.25/54/4.25 TREC,
3/31.75/1.25 SST,13.75/50.5/12.25 AG. Shift preserves the gold class histogram, so
near-correct counts alongside wrong positional labels are expected when it follows
the named records. Histogram agreement is not correspondence accuracy. Full position
profiles, class confusion, seed and dispatch-order cells are in METRICS/POSITION_LEDGER;
they remain descriptives rather than additional selected endpoints.

## Native provenance, costs and lifecycle

Independently matched all72 original request objects, ordered UTF8 wire hashes, source
ID/text maps and returned full prompt-token vectors. All24 triples have identical
native prompt IDs and request bytes apart from their declared schemas. Tag vectors and
strict tag-then-label order match the sealed public-ID/shift17 contract; all72 raw
outputs fully satisfy it. There are72 distinct response IDs,72 wire/call/coordinate
records and72 access-log POSTs, all200. No observed extra inference attempt, retry,
tool response or reasoning response. All token-vector lengths agree with raw usage.

Actual service binding, endpoint, live model cards and adapter bytes/config match
c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3 on Qwen3-4B-Instruct-2507
revision cdbee75f17c01a7cc42f958dc650907174af0554. Small source/base acquisition manifests
and the66MB adapter were hashed once; no fresh multi-GB base-shard scan was performed.
Stored adapter is cast under the qualified auto/BF16 serving configuration. Native
vLLM0.28.0,8192 context,server16 sequence capacity,client4 concurrent individual calls.
This is the native component chat/completions path with supplied tools, not recursive
root actions or a training likelihood export.

| Task/arm | Input tokens | Cached | Uncached | Output tokens |
|---|---:|---:|---:|---:|
| TREC matching |14,930|11,984|2,946|8,785|
| TREC constant |14,930|13,840|1,090|8,522|
| TREC shifted |14,930|13,824|1,106|8,792|
| SST matching |21,858|19,936|1,922|8,216|
| SST constant |21,858|17,472|4,386|8,216|
| SST shifted |21,858|19,696|2,162|8,224|
| AG matching |36,882|32,944|3,938|8,390|
| AG constant |36,882|32,912|3,970|8,272|
| AG shifted |36,882|28,944|7,938|8,410|
| Total |221,010|191,552|29,458|75,827|

All72 cache counters are known from raw response usage. Prefix caching is omitted as
an explicit override in inference.json but the actual engine log records
`enable_prefix_caching=True`; observed counters corroborate active caching. Thus
uncached-cost arm differences depend on scheduling/cache reuse and are not independent
representation efficiency estimates. Matching/shifted share tag multiset, yet shifted
uses7/8/20 more output tokens across TREC/SST/AG. Matching-minus-constant output differences
are263/0/118. No equal-realized-compute claim is needed or justified.

Actual start order equals frozen dispatch order0..71; six triple permutations each occur
four times. Calls overlap as individual workers, not sequentially locked triples.
Collection227.654s, startup42.130s, owned276.261s, outer276.775s; concurrent call-duration
sum907.777s is not elapsed time. All caps600/750/870/900 respected. Seven captured owned
process identities exited, ports were free, final operation recorded GPU processes[]
and no timeout. FINISH44f76a1b…/STATUSbd30d72a… match operation completion-marker hashes.
No late/missing raw record discrepancy. Bridge32 was a separately accepted successor;
its outcomes are not part of this audit.

## Scope and decision implication

Promote the narrow explanation that supplied source IDs can dominate positional-label
instructions in this constrained output package. A varying-token/position-aid-only
account does not explain the strong named-record alignment on disagreeing classes.
This does not establish an attention mechanism, general instruction robustness, or
whole-RLM gain. Four exposed contexts/task, two seeds and one research adapter limit
generalization; retain prior source/split/license/pretraining-exposure caveats. The
independently frozen whole-RLM bridge is the relevant next check of downstream value,
not retrospective relabeling of this failed shifted positional task.

No discrepancies with the implementer's stored schema/positional/named scores were found
after independent reconstruction. The audit author did not implement this experiment,
but proposed its motivating option and contributed to shared upstream harnesses; these
boundaries are stated in the pre-outcome METHOD. Only analysis files were written.
Source/row/position/metric artifacts and fresh parser test evidence are sealed alongside
this report; original METHOD, scientific source and outputs remain unchanged.
