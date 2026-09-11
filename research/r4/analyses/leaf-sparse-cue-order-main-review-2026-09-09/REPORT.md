# Moving an ID after its label shifts the benefit toward the next label

September9,2026. MAIN independently re-parsed every original response without
using the experiment author's scorer. All96 replies satisfy their full required
format, all96 are observed, and no complete64-item array is entirely correct.

The most useful result is about **where the reminder helps**. With an ID before
every fourth label, the strongest benefit is usually at that label or shortly
after it. When that ID comes after its label, the benefit at the same label
largely disappears, while the next label still benefits. The predeclared shift
contrast is positive in all24 context-and-seed blocks and all12 context means,
across question types, sentiment and news topics.

This is a controlled change to output order, not evidence that a particular
attention mechanism caused the effect. Later labels also depend on earlier
generated labels, and different distances still contain different records.

## What the model saw and what changed

The fixed fine-tuned helper classified64 records at a time on12 already exposed
contexts, four per task, with two fresh paired sampling seeds. The input always
contained source IDs. Every fourth output item was an object with an ID field
and a label; the other items were label strings.

Four conditions crossed meaningful source IDs versus constant placeholders with
ID-before-label versus label-before-ID. For an illustrative tagged item:

- ID before label: `{"tag":"q1234","label":"location"}`.
- ID after label: `{"label":"location","tag":"q1234"}`.

The ID and label are illustrative, not a supplied gold answer. Within each
field-order pair, the **entire prompt, native input token vector, sampling and
tools were identical**. Only the ordered decoding schema changed. The constant
placeholder control also emitted the same object structure, letting us ask
whether a source-specific reminder helps beyond the structure alone.

## Salient results

![Moving the ID after its label shifts the benefit toward the next label.](../../../../ARTIFACTS.md#unpublished-files "Not published: id-order-shifts-benefit.png")

The figure is generated directly from the independently reconstructed counts;
[SVG](../../../../ARTIFACTS.md#unpublished-files "Not published: id-order-shifts-benefit.svg") and [figure provenance](../../../../ARTIFACTS.md#unpublished-files "Not published: FIGURE_PROVENANCE.json")
are retained alongside the plotting source. It shows matching-ID advantage,
not raw accuracy or an internal attention measurement.

Every distance column below compares128 positions per task/order/cue:16 positions
in each of8 calls. Values are percentage-point differences in correct labels,
**matching source IDs minus constant placeholders**, not raw accuracy.

| Task and output order | At the tagged item | One item later | Two later | Three later |
|---|---:|---:|---:|---:|
| Question types: ID before label |+55.5|+34.4|+5.5|0.0|
| Question types: ID after label |−2.3|+25.8|+5.5|−3.9|
| Sentiment: ID before label |+32.0|+38.3|+9.4|+15.6|
| Sentiment: ID after label |−3.9|+35.9|+6.3|+15.6|
| News topics: ID before label |+54.7|−0.8|+4.7|−0.8|
| News topics: ID after label |−3.1|+14.1|+0.8|+0.8|

The primary asks whether moving the ID after its label shifts the matching
advantage from the tagged item toward the next item. Its task means are
**+49.2 points for question types, +33.6 for sentiment and +72.7 for news**.
These are differences of differences, not whole-task accuracy gains. Each mean
first averages two seeds within a context and then four contexts. Context means
range+28.1 to+62.5 points for question types,+25.0 to+53.1 for sentiment, and+50.0
to+84.4 for news. All24 individual seed-block contrasts are positive too.
No label-level independence or confirmatory significance claim is made.

For reference, total correct labels out of512 in each cell were:

| Task | Matching, ID before | Constant, ID before | Matching, ID after | Constant, ID after |
|---|---:|---:|---:|---:|
| Question types |321|199|216|184|
| Sentiment |408|286|336|267|
| News topics |253|179|193|177|

This does not contradict the earlier dense-ID experiment, where either order
still worked well. With an ID after **every** label, most labels still follow a
recent ID. The present sparse condition separates the label before a reminder
from the one after it. This is a compatible interpretation, not proof of an
internal state-tracking algorithm.

## Evidence and costs

All96 raw requests match the frozen requested bodies including ordered schema;
wire bytes/hash and actual complete native input token vectors authenticate.
All raw response text matches its enclosing recorded response, with output token
lengths matching usage. No tool response, length stop or schema failure appears.
Every independent primary cell and distance count matches the implementer's
projection, which was opened only after the independent aggregation.

Total provider usage:302,504 input tokens,244,288 cached,58,216 uncached and40,188
output tokens. Cache counters are known for all calls. Output totals are close
between orders and controls; exact equality is not assumed. All cases generate
four-call blocks sequentially with four blocks in flight; call durations overlap.
Collection took128.307 seconds; outer job177.793 seconds, exit0 with no remaining
GPU process. The expected ownedTERMINAL file is absent; we preserve that missing
marker instead of inventing a lifecycle artifact. STATUS and parent release
records are available and separately hashed.

Ten focused independent parser/interaction tests went RED before implementation
and then PASS in0.05s. They cover both assigned key orders, duplicate keys,
wrong cardinality/types/labels, empty content and interaction direction/NULL.
All96 calls in this completed run are actually HTTP200/available. This raw audit
checks the primary experiment and its observed provider evidence, not every
inherited lifecycle implementation independently.

[METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json") retains all96 coordinate predictions, position scores,
class-count discrepancies, costs,24 four-call contrasts and12 context means.
[SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") binds consumed files. [METHOD.md](METHOD.md) discloses
that this was a post-collection MAIN reanalysis; MAIN also reviewed the experiment
implementation before launch. Raw observations remain unchanged.

## Decision

This is a promising output-interface finding to preserve alongside the released-
model replication. The next192-call comparison moves the reminders across the
same fixed records. That directly addresses the remaining possibility that
the originally tagged positions happened to contain easier records. Its plan
was proposed without inspecting these outcomes and retains the same-record
distance0-versus3 primary; no attention or general-planning claim is added.

The stronger long-term question is whether better correspondence improves an
RLM's final answers on record-specific questions, after the coordinator can
reliably gather and combine the helper's results. This component result alone
does not answer that question.
