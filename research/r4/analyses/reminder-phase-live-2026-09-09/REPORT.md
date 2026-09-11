# Moving the reminder changes accuracy on the same records

Independent phase192 audit, September 9, 2026. **The source-matching advantage is
largest at the reminder and smaller three records later in all 12 context means
and all 24 context-seed blocks.** Unlike the earlier distance profile, this test
moves reminder positions while holding the same records and full prompt fixed.
All 192 outputs are schema-valid, all calls observable, and all finish normally.
The result is not caused by format failures or censoring.

## Prespecified primary: matching advantage at distance 0 minus distance 3

Percentage points below are equal-context means over four contexts per task, with
two seeds per context. The same 61 records at positions 4–64 contribute at every
distance. Matching-minus-constant is abbreviated M−C only in this table.

| Task | M−C at reminder | One record later | Two later | Three later | Primary decline |
|---|---:|---:|---:|---:|---:|
| TREC | 61.27 | 50.82 | 22.75 | 5.33 | **55.94** |
| SST-2 | 39.96 | 36.68 | 23.16 | 12.30 | **27.66** |
| AG News | 52.05 | 28.28 | 6.56 | 1.23 | **50.82** |

Every task has eight complete seed blocks and four complete two-seed context
means. Context-primary ranges are TREC 50.82–63.11 points, SST 25.41–30.33, and
AG 34.43–65.57. There are zero unknown blocks/context means. These are nested
repeats over 12 exposed contexts, not independent samples of thousands of labels.
All block/context values are retained in [AUDIT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: AUDIT.json").

The underlying accuracy profiles clarify the effect:

| Task / output cue | At reminder | One later | Two later | Three later |
|---|---:|---:|---:|---:|
| TREC matching | 93.24% | 85.45% | 54.71% | 38.11% |
| TREC constant | 31.97% | 34.63% | 31.97% | 32.79% |
| SST matching | 94.47% | 92.83% | 80.94% | 69.06% |
| SST constant | 54.51% | 56.15% | 57.79% | 56.76% |
| AG matching | 81.76% | 59.63% | 39.75% | 33.81% |
| AG constant | 29.71% | 31.35% | 33.20% | 32.58% |

This substantially narrows the explanation that anchor positions merely held
easier records. The same record occupies each distance through the four phases,
and the constant-tag control is comparatively flat. It does **not** isolate hidden
attention or a memory time constant: phase also changes preceding generated
labels, object/string positions and the constrained autoregressive action space.

## What ran, and what was verified

Twelve exact previously exposed sparse-study contexts—four TREC, four SST, four
AG—were reused without text/order/ID/gold changes. Fixed historical trained child
`c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`, config
`ec773bc3b9de58af98a7c4dce9a40af795a4d05cd47284dbbfb27eac99b74174`, on Qwen3-4B-
Instruct-2507 revision `cdbee75f17c01a7cc42f958dc650907174af0554`. This is not a
released-checkpoint-only comparison and does not involve a recursive root.

Master 981310001 and sampling seeds 981310011/981310021 are the pre-inference
collision amendment, not the superseded proposal's 981308 family. Each call has
16 tag-then-label objects and 48 plain canonical strings; the four phases move
objects among positions modulo four. Matching tags contain the current record's
source ID; constant tags are `p0000`. Temperature 0.5, max output 3,072 and all
other request fields are identical within each eight-call context-seed block.

Independent checks reconcile all 192 CALL requests with the exact frozen ordered
request bytes and separately captured wire bytes, every position's schema,
the bound alias, actual response model, output-token length and provider usage.
All 192 physical provider prompt-token vectors equal the frozen vectors and a
fresh CPU rendering using the actual typed-tool serialization. There are exactly
12 unique physical prompt vectors. All eight bodies within each block differ
only in structured schema; the schema was not silently inserted into different
text prompts. Native tokenizer/template files and the actual adapter/config were
authenticated once, not per call.

All 24 actual eight-call sequences retain their assigned Williams order and do
not overlap within a block. Maximum observed call concurrency is four. Each
coordinate has exactly one physical call: no shared execution or replacement.
All 192 response finishes are `stop`, none is `length`, and no provider error,
request-only tail or unavailable usage/cache field appears. The HTTP-hook
`model_called` flag alone was not used as evidence of provider completion.

The independent parser rejects duplicate/extra/reordered keys, wrong phase types,
wrong tags, noncanonical labels, short/long arrays, invalid JSON and trailing prose.
All completed invalid arrays would score zero with unavailable alignment; missing
or provider-unavailable calls would stay NULL. Here none requires either rule.
Positions 1–3 remain in whole-array totals but not any primary core; prior distance
is undefined before the first actual anchor, never circularly wrapped.

## Secondary whole-array outcomes and cost

Each task/arm below has 32 calls and 2,048 scheduled label assignments. All are
aligned and valid, but **no complete 64-record array is entirely correct**.

| Task | Matching correct | Constant correct | Matching mean count L1 | Constant mean count L1 |
|---|---:|---:|---:|---:|
| TREC | 1,409 / 2,048 | 726 / 2,048 | 27.19 | 57.19 |
| SST | 1,734 / 2,048 | 1,187 / 2,048 | 7.63 | 34.81 |
| AG | 1,134 / 2,048 | 701 / 2,048 | 33.44 | 60.44 |

Count-vector L1 is secondary and permutation-insensitive; it is not another
correspondence proof or a substitute for exact per-record scoring. All 24 phase
cells, per-call confusion counts and boundary diagnostics are in METRICS.json.

| Task | Matching output tokens | Constant output tokens | Matching summed call seconds | Constant summed call seconds |
|---|---:|---:|---:|---:|
| TREC | 17,240 | 16,515 | 207.15 | 198.34 |
| SST | 16,291 | 16,319 | 194.86 | 195.10 |
| AG | 15,795 | 15,326 | 194.17 | 187.44 |

Total provider usage is 592,816 input and 97,486 output tokens, with 562,144 cached
and 30,672 uncached input tokens; no usage fields are unknown. Actual output cost
is close but not identical between arms. Because every pair is valid/observed,
all-observed and jointly-valid cost supports coincide. Provider counters are not
measured GPU FLOPs; parallel summed call seconds are not job wall time.

## Original zero-call failure versus accepted continuation

The original launcher failed after **47.711 owned seconds**, before entering
collection: the privately extracted `run()` referenced unbound `time` on its first
line. It did not create the scientific attempt directory or make a model request.
Its failure log and owned-release record remain intact. A separate latent copied
96-call status/completion assumption was corrected in the recovery runner before
any sampling; it was not an observed failed 192-call result.

MAIN's additive accepted runner supplies `time`, changes the three copied
96-call metadata/completion strings to 192, routes to unused attempt-002, and
keeps the frozen scientific requests/model/seeds/scorer unchanged. The recovery
records **303.827 collection seconds**, **353.397 owned seconds** and **353.923
parent seconds**, exit 0/no timeout/GPU processes empty afterward. Both attempts'
owned release markers pass. Counting both owned attempts gives **401.108 seconds**;
the first failed startup is not hidden or mistaken for scientific sampling cost.
The new accepted envelope is reported explicitly, not called an automatic retry
or evidence from two independent samples.

The immutable original READY still names attempt-001; executed attempt-002 is
bound by the recovery acceptance/runner and its actual ATTEMPT/STATUS/EXIT records.
SOURCES.json includes these paths and hashes; no live process was touched for this
audit.

## What this changes, and what remains open

This is a strong within-record component result under the fixed trained child:
source-matching reminders help most locally, and their benefit declines across
three subsequent records. The result is not explained by easier anchor examples,
invalid-array exclusion or changed input tokens. Moving reminders changes generated
history, so it does not isolate the underlying mechanism beyond that package.

The decision-relevant follow-up is a separately frozen new-source or released-model
phase replication, or an intervention holding more generated history fixed—not
additional training without a defined uncertainty. True fresh TREC clusters are
not available from the now-exhausted source pool; the separate feasibility report
requires an explicit freshness/task change. No automatic new study or data reuse
is authorized by this report. Whole-RLM planning/counting improvement is untested.

Limits: four exposed contexts per task, two generation seeds, one TREC-trained
checkpoint, public pretraining exposure unknown, underlying licenses unresolved,
constrained output grammar and shared autoregressive history. All twelve positive
contexts support the descriptive direction but are not a confirmatory population
effect or a hidden-state mechanism measurement.

## Reproducibility and independence

METHOD and strict parser were sealed before outcomes, after parent terminal-only
metadata. Three focused CPU fixtures pass. No author scorer was imported. The
auditor authored some shared component ancestors, not this phase implementation
or recovery; this is independent outcome reconstruction, not independent framework
authorship. A local renderer validator's input mutation was isolated with a deep
copy, documented in AUDIT_ADAPTATION.md; actual requests and sealed scoring method
were unchanged. No experiment/source/GPU changes occurred.

Primary evidence: [frozen design](../../sidecars/leaf-reminder-phase-v1/DESIGN.md),
[recovery runner](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../operations/2026-09-09-phase192-launch-recovery/runner.py"),
[STATUS](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-reminder-phase-v1/outputs/attempt-002/STATUS.json"),
[independent raw audit](../../../../ARTIFACTS.md#unpublished-files "Not published: AUDIT.json"), [compact metrics](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json"),
[method](METHOD.md), and [source inventory](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json").
