# Child-role suffix16: no observed loop suppression or accuracy gain

The child-only instruction left exact answers at **2/8 → 2/8**: one paired gain,
one loss and six ties. All16 coordinates completed and were score-observable;
none were censored, prevented, unrun or unknown. Complete malformed/empty finals
were2 control and1 suffix; the other wrong finals were4 and5. Strict scores and
schema validity independently agree with the unchanged host scorer for every row.

Most importantly, **no child call loops occurred in either arm**. Every one of the
60 control and36 suffix child invocations made exactly one native call. Neither arm
had a structured child tool request or child tool observation. The historical
failure-enriched selection therefore did not reproduce the proposed amplification
mechanism under these fresh seeds; fewer calls cannot demonstrate its suppression.

| Exposed task/context (two seeds each) | Control exact | Suffix exact | Total calls control → suffix |
|---|---:|---:|---:|
|16 records, human being|1/2|2/2|4 → 9|
|32 records, numeric value; moderate comparator|1/2|0/2|9 → 4|
|64 records, entity, training-064-00|0/2|0/2|30 → 22|
|64 records, entity, validation-064-02|0/2|0/2|36 → 22|

These are four exposed context clusters, not16 independent experimental units.
Three groups were selected from earlier costly failures; the historical
training/validation names do not imply unopened evaluation. The selected groups
give1/6 → 2/6 while the moderate comparator gives1/2 → 0/2. Sparse gain/loss
observations do not establish a general accuracy or efficiency effect.

## Delivery and first-root variability

All eight pairs have equal actual initial-root physical prompt IDs, causal
messages, tools and sampling. All136 physical calls satisfy the fixed alias,
weight, sampling and coordinate-seed checks; all136 independently reconstruct
from the official native branches. All16 graphs are complete, all16 owned engine
overlays match the qualified control/treatment hashes, and the suffix is present
exactly once in all36 treatment child system prompts, absent from root/control.
It remains an instruction, not disabled tools. No source, score or admission changed.

Nevertheless, the parsed first-root messages differ in three pairs, before any
child can receive treatment:

- `training-016-00:human_being`, seed893350289: a local variable-name change;
- the same task, seed62794825: empty structured root message versus a Python
  tool request (this is the observed0 → 1 success pair);
- `training-064-00:entity`, seed62794825: different root programs, batch dispatch
  versus a whole-document call; both ultimately fail.

Exact pair/request IDs, raw file hashes and messages are retained in
[TERMINAL_READOUT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: TERMINAL_READOUT.json") and [METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json").
Treat this as stochastic/numerical/scheduling variability despite equal declared
requests and seeds; its precise source is unresolved. It is not an effect caused
by a suffix that has not yet been delivered. The five equal parsed messages are not claimed to have equal sampled
response IDs. No determinism investigation or replay was launched.

## Costs and concrete failure evidence

| Observed cost | Control | Suffix |
|---|---:|---:|
|All native/HTTP calls|79|57|
|Root / child calls|19 /60|21 /36|
|Logical prompt tokens|86,560|73,015|
|Explicit cached tokens|79,024|64,896|
|Uncached input tokens|7,536|8,119|
|Completion/action tokens|12,966|14,712|
|Summed episode seconds, not elapsed wall time|400.73|398.55|

The22-call reduction comprises24 fewer root-dispatched child invocations and two
additional root calls. Completion tokens rise13.5% and uncached input7.7%; fewer
logical prefixes therefore do not establish less GPU work or better efficiency.
All usage fields in this run are observed; none were imputed as zero.

Three control and four suffix child responses end at the2048-token limit. Their
recorded output repeats label strings beyond useful array completion, with root
JSON-parse errors and subsequent root dispatch/recovery attempts visible in the
saved trace. This is single-call output overgeneration, not repeated child tool
use. For example, suffix episode `dad6902889e0…` makes two such child calls;
its root acknowledges parsing failure and nevertheless ends `Answer: 0`, an
observed wrong final, not an infrastructure null. In its control counterpart
`a9711384dce9…`, the recorded root program extends a list directly with
`classification.answer` text and then counts the string `entity`, also producing0.
No generated program was executed by this audit. Child labels or non-target
classifications were not regraded, repaired or made into a stronger success rule.

## Complete attempt accounting and timing

The independent union gives136 routed wrappers =136 allowed final request hooks
=136 HTTP responses =136 returned native samples =136 trace-linked and fully
causal-verified calls. There are zero prevented, prerouting-failed, result-less,
orphan, ambiguous, unknown-delivery or unattributed attempts. The final counter
reconciles136/2048 allowed, zero prevented. The limit counts pretransport hooks,
not server receipt; the equal denominators happen to be corroborated here.

Owned collection lasted291.26s, service startup42.29s, owned envelope343.29s,
and accepted child process346.10s (exit0, no timeout, recorded empty GPU).
Before-owned-clock import/launch was2.31s; collection-end to release2.62s and
release-to-owned-terminal0.009s. Independent raw analysis took3.61s after release,
without a GPU scheduling lock. Built-in READOUT was absent and was not rerun.

[SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") authenticates734 distinct source/input/artifact paths,
each physically read once in the audit cache. The271-file pre-frozen closure is
reused, not rehashed per episode. Service credential-bearing bytes are hashed,
never copied into projections. The14 focused preparation tests passed before
outcome access; nulls, multiple matches and partial graphs were tested even though
this run has complete evidence.

Decision: do not promote this suffix as an accuracy/efficiency improvement or a
solution to child loops. Prioritize the already evidenced output-cardinality and
root-consumption failures; any future loop-isolation test needs a live control
that actually exhibits loops. This small exposed paired readout does not justify
changing training rewards or admission.
