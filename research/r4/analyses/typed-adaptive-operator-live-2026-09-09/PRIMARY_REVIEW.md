# Independent check: filtering is a useful efficiency baseline

MAIN independently reconstructed all24 planned outcomes, the public/host answer
mapping,120 physical child responses, their actual wire usage, and the counts
supported by their source-ID maps. No experiment-author scorer was imported.
The [implementer report](REPORT.md) agrees on all primary outcomes, map accuracy
and call/prompt/output totals. Its cache-accounting statement was incorrect;
the [additive correction](CACHE_CORRECTION.md) now agrees with this check.

The clearest result is a limited but useful one: in six cases where both
hand-written procedures returned the correct user-specific count, filtering to
the relevant records first needed six helper calls rather than48. It used5,832
prompt tokens rather than55,258,428 output tokens rather than6,931, and632
uncached input tokens rather than3,642. These are87.5%,89.4%,93.8% and82.6%
reductions respectively. They are actual paired inference costs, not GPU FLOPs,
an end-to-end throughput guarantee or evidence that a model learned this plan.

| Procedure | Correct / observable | Missing endpoint | Fully clean episodes | Actual helper calls |
|---|---:|---:|---:|---:|
| Classify all records for the user query |6/6|2|2/8|48|
| Filter first, then classify |8/8|0|4/8|8|
| Classify all records for the global query |3/8|0|0/8|64|

All six observed user pairs tie correct; the two additional filtered successes
have unavailable full-record counterparts, not observed incorrect counterparts.
The missing full-record runs failed during setup before any child call. The
frozen endpoint counts completed answers despite later finalization errors;
there were16 such timeouts.22 observed answers therefore do not mean22
training-ready native graphs. The missing-finalization artifacts remain a real
limitation even though the external request logs survived.

Every one of the120 captured child responses had an exact ordered ID-to-label
map. Independent reconstruction matches all22 terminal counts to those maps,
including the five wrong global counts. Label correctness was727/768 for
full-record user runs,64/64 for filtered user runs, and980/1024 for global runs.
Correct output structure does not guarantee correct semantic classification.

This uses four exposed context groups and two seeds, with eight global runs
referenced twice in the32 logical cells. The physical union counts them once:
136,692 input tokens,122,528 cached input tokens,14,164 uncached input tokens
and16,737 output tokens. All120 actual cache counts are known in the original
JSON-encoded wire response, although the normalized response drops them. No
request-only record, duplicate physical provider ID or root-model call appeared
in the checked union.

The relevant user subsets were small and easy. Always answering2 would succeed
in six of eight cases. The filter has to read the full public record file before
selecting its subset, so reduced model work is not reduced host input reads.
The next scientific question is whether a freely acting, trained coordinator
can learn when to filter and when all records are needed. This result establishes
a concrete baseline for that question, not a novel query-optimization algorithm.

The [independent code](../../../../ARTIFACTS.md#unpublished-files "Not published: main_primary.py") and [complete primary result](../../../../ARTIFACTS.md#unpublished-files "Not published: MAIN_PRIMARY.json")
retain each coordinate, pairing, error, source-map reconstruction and cost.
Nine focused tests passed after an actual missing-module failure.
[Source hashes](../../../../ARTIFACTS.md#unpublished-files "Not published: MAIN_PRIMARY_SOURCES.json") bind394 consumed files and review
sources. MAIN_PRIMARY SHA256 is
`8f05db4f033e77d9defcccc860277e2ea6b9c51fd092e832bd2f1fa643f77733`.
The separate pre-outcome [main method](MAIN_REVIEW_METHOD.md) records the scope:
this is an independent primary/source-map/cost check, not an independent
reimplementation of the entire native harness or the implementer's ACP exporter.
