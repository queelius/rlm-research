# Does the supplied source cue need to precede its label?

This is the CPU implementation of the [approved design](../../ideas/2026-09-09-output-cue-order-design.md)
and [main decision](../../operations/2026-09-09-continuous-allocation/OUTPUT_CUE_ORDER_CPU_DECISION.md).
Their exact hashes, historical source closure and all physical candidate requests
are bound in SPEC. No model observations inform this implementation.

Four exposed64-record contexts: lowest two original TREC indexes0/1 and lowest
two SST indexes4/5, as fixed in identity384. Retain first presentation, numerically
disjoint q source IDs and the exact canonical task contracts. No new text selection,
label quota, hidden gold, prompt crop, model training or independent-data claim.

Each context gets seeds981282011/981282021, three rules (matching source ID,
unrelated ordinal p0001..p0064, constant p0000) and two raw object orders. All48
calls use historical c32de, temperature0.5, top_p1/top_k-1/min_p0, maximum3072
output tokens,8192 context,120-second request timeout and no retries.

Both order arms say “the keys tag and label”. Only insertion order of schema
properties and required differs: tag,label versus label,tag. Actual XGrammar
CPU compilation must accept the assigned complete64-object order and reject
the opposite. The source IDs, messages, tools, sampling and full native prompt
IDs are identical within each pair. JSON semantic/dict equality cannot establish
this intervention; ordered schema/body SHA256 and actual wire bytes do.

For local context c and repeat r, rotate meaningful/ordinal/constant left by
(c+r)mod3 and reverse for odd(c+r). Original arm index j sets adjacent order:
tag-first then label-first for even(c+r+j), reversed otherwise. The two repeats
reverse each condition's first exposure. Four workers; actual asynchronous
start/completion and cache usage remain observable, not assumed balanced.

Primary score requires exact cardinality, duplicate-free two-field objects in
the assigned physical key order, correct specified tags and canonical labels.
Then labels are compared to their displayed source record. No reordering or
decoder repair. Report matching-minus-ordinal strict correct/64 within each
order and their tag-first minus label-first interaction by task/context/seed.
Constant contrasts, whole64 correctness, validity/coverage and per-call class
count errors are retained. Complete invalid outputs score strict0 with unavailable
alignment; infrastructure and unrun coordinates remain null, not policy negatives.

Previous-record agreement for positions2..64 is a secondary diagnostic. Position1
has no previous tag. Its chance reference independently permutes the observed
positions2..64 prediction multiset against the fixed previous-gold multiset;
expected matches=sum(prediction_count[label]*previous_gold_count[label])/63.
Repeated labels and many descriptive comparisons prevent an identifying attention
claim. Neither this diagnostic nor numeric-ID alignment replaces primary accuracy.

Only two exposed context clusters per task and two nested seeds: not48 independent
samples or3072 independent labels, not an end-to-end RLM effect. Pretraining/source
history remains unknown and inherited public-data license caveats remain bound.
Generic output-order sensitivity is not a novelty claim. A loss of the matching
advantage specifically under label-first supports a cue-before-prediction followup;
persistence in both orders argues against the simple immediately preceding-cue
explanation. Loss in both leaves prompt/subset/sampling effects unresolved.

Caps:600s collection,780s shared work including startup,900s owned including120s
cleanup reserve,930s parent outer. Inherited owned clock starts inside main;
pre-main imports are under the parent outer cap. Small built-in summary executes
before owned release; independent post-run auditing must occur after release.
One qualified service/one old adapter; owned-only cleanup in finally. No new
scheduler, retry, environment, shared-source edit or GPU launch in preparation.
