---
id: mnli-host-identifier-join
status: exploratory_preparation
question: Does moving identifier attachment into ordinary code reduce wrong-record labels?
created_utc: 2026-09-10T16:57:00Z
---

# Let the model classify; let code attach identifiers

Our prior identifier interference survives explicit same-record instructions.
This deployment-oriented comparison asks whether the model needs to emit
identifiers at all. It is distinct from swapping the order of two fields:
the shorter answer contains only semantic labels, and a fixed positional join
attaches the requested tags afterward. The join cannot fix wrong labels.

Freeze three input reference conditions (misleading, unrelated, aligned)
crossed with two output formats (tag-first objects, label-only array).
Use the same eight exposed wording-control contexts without reselecting
individual cases. Every condition receives fresh calls,48 total, with
seed983626101+context index shared within each block. This design is frozen
before either output-field-order or host-join experimental outcomes are read.
No proposed field-order result is used to choose this second experiment.

Both formats classify48 displayed records in the same order. Identical input
objects retain both id and requested_tag, even when the model does not copy
either to its answer. Explicit instructions still define requested_tag as
an opaque address. Tag-first reproduces the previous explicit prompt/schema
except fresh seed and cache namespace. Label-only replaces just the output
instructions and schema, using an exact48-string array with the same three
allowed labels. No evidence from gold enters prompts, grammar or host join.

The host maps array position i to the requested_tag of input record i only
after the entire48-element array is native-authenticated and well formed.
No repair, truncation salvage, sorting, resampling or partial-array join.
Primary score counts correctly classified displayed records under the exact
declared whole-output contract. A malformed authenticated output is0; an
unavailable native result isNULL. Report model-emitted ID fidelity separately:
it is not applicable, not a model success, for label-only outputs.

Fixed released Qwen3-4B Instruct2507, no adapter/tools/thinking, temperature0.5,
top_p1, max3072output/context8192, four workers,90seconds/call, prefix cache
off. Outer1440seconds includes1320work, startup180 and release90. Save each
request, raw response and result, all48 planned slots. No retries.

Primary difference-in-differences: label-only versus tag-first improvement
in the misleading condition minus its improvement in the aligned condition,
computed across eight context clusters. Advance on at least10percentage
points of selective improvement in6/8contexts without reduced availability.
Report every condition, NULL bound and per-context contrast; this practical
screen is not a significance test. Unrelated-reference interaction and wrong
named-record predictions are secondary. All records share only128premise
groups; contexts/seeds/labels are not independent interchangeable replicates.

This is a harness strategy package: schema shape, generated tokens and natural
instructions change together. Measure cost; do not call it equal-FLOPs or a
pure attention intervention. If useful, replicate on new groups and another
task/model before promoting. If ineffective, test removing redundant input
identifiers, then consider targeted correspondence training. MAIN authors and
reviews locally; old sealed runs and artifacts remain unchanged.
