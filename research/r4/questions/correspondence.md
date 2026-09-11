---
schema_version: "rlm-question-card-v1"
id: "rq:correspondence"
title: "When do output source cues improve semantic alignment and survive full-RLM use?"
status: "promising_exploratory"
updated_utc: "2026-09-11T00:24:00Z"
evidence_cutoff: "2026-09-09T17:32:51.282711+00:00"
living_update_cutoff_utc: "2026-09-11T00:15:00Z"
source_catalog:
  path: "/project/alex_phd/runs/rlm-research-r4/analyses/research-factory-2026-09-09/CATALOG.json"
  sha256: "e0fa23412505eee178d27041816e84f7931d6da01b02e13f664393a6586ff39c"
related_questions:
  - "rq:reduction"
claim_ids:
  - "claim:output-addresses-help-and-interfere"
  - "claim:fresh-correspondence"
  - "claim:shifted-cue-following"
  - "claim:same-record-distance"
  - "claim:bridge-no-task-gain"
reports:
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-stable-anchor-vs-sequence-counting-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-stable-anchor-qwen8b-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-positional-anchor-new-context-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-positional-anchor-new-context-live-2026-09-10/ERRATUM.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-field-order-replication-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-positional-anchor-binding-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-fixed-output-visible-reference-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-new-context-alien-correspondence-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-new-context-correspondence-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-alien-tag-correspondence-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-fresh-correspondence-live-2026-09-09/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-shifted-cue-live-2026-09-09/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/reminder-phase-live-2026-09-09/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/root-child-representation-bridge-live-2026-09-09/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-local-cue-replay-live-2026-09-09/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/audit-report.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/free-id-audit-report.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/leaf-role-tool-audit-report.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-correspondence-live-2026-09-09/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-shifted-correspondence-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/leaf-mnli-exact-tag-correspondence-live-2026-09-10/REPORT.md"
publication_readiness: "not_publication_ready"
---

# When do source cues survive full-system use?

## Current question — September 11, 00:24 UTC

Matching arbitrary tags preserve much of the benefit of ordinary row numbers.
On the smaller Qwen model, later-label accuracy was34.2% without matching tags,
85.4% with sequential numbers,86.1% with shuffled numbers, and84.9% with arbitrary
tags. Thus ordinary counting order is not required under this supplied-key interface.

On the same16 inputs, Qwen3-8B gave31.5%,85.5%, and81.1% for no tags, sequential
numbers, and arbitrary tags. Both tag types helped in all16 inputs for both models.
The larger model did better with ordinary numbers than arbitrary tags in this
realization. These are two released models from one family, not a controlled size
experiment. The software fixes tags and answer order, not semantic labels.

Two questions now matter most: does this improvement survive the main model's
final count or sum, and must the input/output tags literally match? The whole-task
comparison is queued; the balanced matching control is in CPU preparation.
Neither is evidence yet. A draft of the latter accidentally removed the public
reference field and is preserved unlaunched; the corrected protocol must restore
the actual reference manipulation before the three conditions are meaningful.

[Arbitrary-tag evidence](../analyses/leaf-mnli-stable-anchor-vs-sequence-counting-live-2026-09-10/REPORT.md) ·
[Second-model evidence](../analyses/leaf-mnli-stable-anchor-qwen8b-live-2026-09-10/REPORT.md).

## Historical findings at20:45 UTC

The matched input/output numbering result replicated on16 inventory-excluded
contexts: primary late interaction+657/1536 (+42.77 points), positive16/16,
all192 native/valid, frozen gate passed. Matching rows on both sides gains714
later labels versus57 from output-only numbering. MAIN rebuilt192requests,
recounted192 literal outputs, verified576capture pins and replayed the audit.
Report wording originally misstated the segment denominators; the additive
erratum corrects early256/late512 per relation cell without changing results.
Next test actual downstream consumption and a discriminating correspondence
control. No full-RLM benefit or latent attention mechanism is established.

## Historical findings at19:43 UTC

The16-new-context field-order replication points in the same direction, but its
9.765625-point selective effect narrowly misses the frozen10-point threshold.
It is directional support, not a formally promoted result.

The complete ordinal96 factorial gives a stronger separate lead: matching row
numbers on input and output improves total accuracy590→933/1152 and later-record
accuracy292→620/768. Output numbering without input numbers gives only16/768
more correct later labels, failing its original gate. All96 responses are native
verified and valid. The matched package helps under allthree reference conditions;
it is not specifically a cure for misleading identifiers. The fresh16-context,
192-call full factorial is accepted after the queued RL run. No replication result
or full-RLM benefit is claimed yet.

[All cells, provenance and limitations](../claims/output-addresses-help-and-interfere.md).

## Historical output-interface findings at18:20 UTC

The field-order pilot gave a modest selective gain: label-first improved wrong-ID
cases by7.81points and reduced aligned cases by3.91points, for11.72points of
interaction. A16-new-context replication is accepted. The host-join pilot shows
a larger interaction but not a universal gain: labels-only improves misleading
cases14.06points while harming aligned cases34.38points. MAIN read both complete
native audit implementations and reports, reproduced12 focused tests, and
verified228/225pins without mismatch.

Post-hoc examination of all48 host-join calls reveals a late-position problem:
labels-only accuracy drops from77–84% on the first16 items to34–37% on the
remaining32. Each of the eight contexts declines in all three reference conditions.
Aligned tag-first answers remain83% in both ranges. This does not prove position
tracking is the cause, and the16/32split was chosen after inspecting the profile.
A96-call input-number×output-anchor factorial is being prepared with fresh calls.

[Finding and limits](../claims/output-addresses-help-and-interfere.md) and
[new primary-literature connections](../ideas/2026-09-10-batch-position-and-symbol-grounding.md).
The earlier observation that plain labels can underperform matching IDs remains
important and consistent with the new tradeoff; do not discard it.

## Historical fixed-output mechanism control at04:52 UTC

Holding requested tags/grammar fixed and changing visible IDs gives aligned
610/768, misleading289/768, unrelated620/768. All48 native responses satisfy
the exact contract; aligned and unrelated each beat misleading in all16 contexts.
On530 positions with different named/displayed gold labels,362 follow the named
record,106 the displayed record and62 neither. MAIN verified all932 sealed pins.
[Complete audit](../analyses/leaf-mnli-fixed-output-visible-reference-live-2026-09-10/REPORT.md).

This is exposed-panel evidence of misleading-reference interference, not a
necessity claim for aligned IDs, an equivalence test, an internal-mechanism
identification or a whole-RLM improvement. All contexts were retained without
outcome selection. Additional exposed-panel repetitions have lower priority than
new task-family transfer or a genuinely discriminating intervention.

## Historical sealed replication at04:24 UTC

The three-arm comparison is now independently sealed on16 additional context
groups: matching611/768, misleading298/768, unrelated618/768. All48 outputs are
native/full-contract valid. Matching and unrelated each beat misleading in all16
groups; unrelated minus misleading is+41.67 percentage points. On530 positions
with different displayed/named gold labels,361 outputs follow the incorrectly
named record,110 the displayed record, and59 neither. These are new selected
inputs under explicit inventories, not pretraining-unseen or new-domain data.
[Audit](../analyses/leaf-mnli-new-context-alien-correspondence-live-2026-09-10/REPORT.md).

The next accepted experiment holds requested tags and exact output grammar fixed
and changes only visible source IDs. It reuses all16 contexts without filtering,
so it is an exposed mechanism test. A labels-only interface is lower priority:
earlier local data favored matching IDs over plain labels. Its possible value is
a measured accuracy/token-cost tradeoff, not a new batch-demultiplexing invention.

## Historical mechanism and breadth checks at03:29 UTC

An unrelated-alias control substantially narrows the interpretation: matching
619/768, misleading visible-reference284/768, unrelated628/768. All48 native
outputs satisfy the entire exact-tag contract. Both matching and unrelated
conditions beat misleading IDs in all eight context groups. On522 differing-gold
shifted positions,368 predictions follow the named record and87 the displayed
one. Alien strings have no invented named gold. Actual input totals match across
arms, but equal tokens do not establish equal FLOPs or equivalence of unrelated
and matching conditions. [Independent audit](../analyses/leaf-mnli-alien-tag-correspondence-live-2026-09-10/REPORT.md).

This argues against varied tags or copying effort alone explaining the deficit.
It supports wrong-visible-reference interference on this repeatedly exposed panel,
not an internal-attention claim or a whole-RLM gain. The new-context matching/
constant32 is now sealed:639/768 versus398/768, all32 full-contract native outputs,
all16 context groups favoring matching. Its256 new premise groups are new only
under named study exclusions, within the same four validation genres. It is a
breadth check, not itself a replication of the three-arm mechanism contrast.
[Independent new-context audit](../analyses/leaf-mnli-new-context-correspondence-live-2026-09-10/REPORT.md).

A direct three-arm replication on16 further context groups is accepted and waiting
behind active training. It uses48 endpoints and one paired seed per group; matching,
shifted-visible-reference and unrelated exact tags all permit every semantic label.
The parser/method is being independently sealed before outcomes. Do not treat its
READY status as evidence or pool it into the earlier exposed-context results.

## Question

When do output source cues improve semantic alignment, and under what conditions does that
component effect survive downstream planning and reduction in a complete RLM?

## Why it matters

A reliable source-to-output correspondence mechanism could make decomposed outputs easier to join
and audit. A local label preference is useful only within its measured scope, however, and should
not be mistaken for an end-to-end recursion advantage.

## Evidence so far

At the catalog cutoff, `claim:fresh-correspondence` reports that matching source IDs beat same-shaped
constants in all 16 task/model/context means in `exp:fresh96`. `claim:shifted-cue-following` reports
that deliberately shifted IDs pulled outputs toward the named record in `exp:shifted72`.
`claim:same-record-distance` adds a same-record phase control: distance-zero minus distance-three
effects were positive in all 12 context means in `exp:phase192`. See the sealed [new-record
comparison](../analyses/leaf-fresh-correspondence-live-2026-09-09/REPORT.md), [shifted-cue
control](../analyses/leaf-shifted-cue-live-2026-09-09/REPORT.md), and [phase
control](../analyses/reminder-phase-live-2026-09-09/REPORT.md).

The contrary whole-task evidence is material. In `exp:bridge32`, ID maps improved count-label
agreement from 567 to 593 of 628 while count stayed at 1/8 and checksum stayed at 0/8; checksum
paired uptake was only 3/8. See the sealed [bridge report](../analyses/root-child-representation-bridge-live-2026-09-09/REPORT.md).

### Later sealed updates outside the catalog cutoff

The [teacher-forced local-cue replay](../analyses/leaf-local-cue-replay-live-2026-09-09/REPORT.md)
holds the prior output history fixed and changes only the current tag. Matching-cue probability
improves in 14/16 positions for each of AG News and SST2, while shifted cues often favor the named
record. This strengthens the bounded conditional cue result, not an attention claim or free-running
RLM result.

The sealed [three-root bridge audit](../operations/2026-09-09-allocation-5780/audit-report.md)
retains checksum 0/8 in both array and map arms for all three roots. RL4 gains two count successes
with maps, but higher-rate SFT8 has one count win and one loss and no net count gain. The update
therefore does not show a robust across-root whole-task map benefit.

The [free-output audit](../operations/2026-09-09-allocation-5780/free-id-audit-report.md)
is now independently sealed (report0f946a5980255a2dc43b8dcf398fbac4681fd0f26c1cb4790438c9462082259f;
finalbb92443c9c310e3c2e481ccdfe48948303b73d85f136640e521b7ae7ab31ee46).
All96 actual calls are available. Exact grammar produces48/48 fully valid outputs;
free decoding only4/48. Exact matching beats both controls in each of eight exposed
context groups. However,35 free outputs pursue the advertised Python route and nine
unfinished arrays already exceed64 items. The four valid free arrays have all IDs
correct. This is not an isolated ID-copying failure: the inherited system describes
a coding agent and advertises a tool in every cell. Exact grammar controls route,
stopping, shape and IDs together. The next discriminator is the leaf role/tool
contract before another specialized-ID training run.

### Role/tool comparison completed

The [role/tool96 audit](../operations/2026-09-09-allocation-5780/leaf-role-tool-audit-report.md)
is sealed, REPORT5e1b42fe…/FINALdd755480…. All96 actual responses are available,
with no strict scoring disagreement. In the classifier/no-tools setting, exact
matching IDs label218/256 records correctly versus129 constant and123 plain;
matching wins each of four contexts (two news, two sentiment). Matching's free
validity increases0/4→3/4 when either the coding role or tools are removed. Its one
remaining classifier/no-tools failure contains all64 correct ordered IDs but uses
a forbidden neutral sentiment label. No ID repair is applied. This separates some
tool-routing/format failures from the surviving semantic representation advantage.
One seed and fixed role/tool order remain limitations; these are four context
clusters, not256 independent treatment trials. This released-base result does not
automatically describe c32 or whole-RLM performance.

### Sentence-pair correspondence and conflicting requested IDs

The MNLI comparison moves beyond short-topic classification to deciding whether a
hypothesis follows from, contradicts, or is undetermined by a premise. On eight
label-blind48-pair contexts, matching/free output obtains628/768 strict correct with
16/16 valid batches. Constant/free output is valid JSON but has49–54 rows instead
of48 in every batch. Under generic shape control, matching scores591/768 strict
versus380/768 constant; one matching batch has a contract error, and its separate
positional-label score is627/768. These diagnostics do not repair the strict primary.
[MNLI audit](../analyses/leaf-mnli-correspondence-live-2026-09-09/REPORT.md).

The subsequent generic shifted-ID experiment cannot by itself support its planned
contract-gated mechanism diagnostic: all16 shifted batches fail the requested-tag
contract, leaving zero eligible batches. A later **exact requested-tag** experiment
constrains that tag in both arms while leaving all three labels free. It obtains
matching622/768 versus shifted280/768, with32/32 native whole-contract-valid batches.
All eight context means favor matching. Among522 positions where displayed and
named records have different gold labels,373 predictions follow the named record,
80 the displayed record, and69 the third label. This is semantic redirection under
the specified decoder, not spontaneous ID copying or recovered historical outputs.
[Generic shifted audit](../analyses/leaf-mnli-shifted-correspondence-live-2026-09-10/REPORT.md),
[exact-tag audit](../analyses/leaf-mnli-exact-tag-correspondence-live-2026-09-10/REPORT.md).

The exact-tag comparison uses the same exposed eight contexts, new paired seeds,
released Qwen3-4B and no tools. Its audit inherits a prospective method but its final
analyst had seen aggregate outcomes before parser construction; this timing is
disclosed in the sealed report. All32 physical calls return, with121288 input and
30592 output tokens. No independent-context or internal-attention claim follows.

## What remains unknown

The evidence does not identify an internal attention mechanism, freely learned ID retrieval, or a
general recursion benefit. Prompt/schema changes, forced grammar, bounded dataset selection,
unknown pretraining exposure, adaptive child widths, and downstream scope/reduction errors remain
live explanations. Repeated seeds within exposed contexts are not independent task replications.

## Smallest discriminating next experiment

First compare a misleading visible-record ID against a one-to-one unrelated alias,
with matching IDs as an anchor and all requested tags exactly enforced. The unrelated
dictionary differs in strings, even when shape and token lengths are matched; it is
not a perfectly neutral reference. Second replicate matching versus constant on
new MNLI premise groups selected without using gold, excluding all named prior
experiment inventories. These are CPU-preparation priorities, not launch approvals.
Do not use dense label-first persistence as proof of input binding: after the first
position, a label still follows the previous emitted tag, and the existing sparse
order experiment already shows next-label effects. Then test the useful leaf change
inside the RLM while retaining root tools and measuring actual returned-label
consumption. The
[decision memo](../ideas/2026-09-09-learned-correspondence-sft-design.md) retains why another
specialized-ID SFT was deferred. A paired whole-RLM test still follows only when actual
batch width, child-format exposure and root reduction are measured. Active launch authority
and exact budgets live in the queue, not this question card.

## What would justify a stronger claim

Promote the component claim after replication on genuinely new contexts or sources with the same
causal controls. Promote whole-RLM usefulness only if adequate-exposure replications improve strict
end-to-end outcomes across new context clusters. Revise toward uptake or reduction bottlenecks if
labels improve without answers, and retire the broad system claim if adequately exposed whole-task
replications remain null.
