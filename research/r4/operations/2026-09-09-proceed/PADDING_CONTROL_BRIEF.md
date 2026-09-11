# Bounded follow-up: meaningful output anchors versus placeholder structure

Design decision: September 9, 2026, approximately 04:05 UTC. The user has granted
autonomous experimental design and CPU preparation without blocking questions.
This is an exploratory sidecar, not a production-harness change or a confirmed
novel method. Preparation must not disturb the active GPU chain.

## Question and why this comparison

Does a meaningful identifier before each label help beyond the extra output
structure and token allowance? The completed anchor comparison keeps both outputs
valid, but its indexed output uses about 3.2 times as many generated tokens. The
queued grammar160 already crosses weights, free versus constrained decoding and
two task domains. Do not duplicate that grid under a new name. Add the missing
meaningful-ID versus placeholder control, with bridges to the earlier formats.

## Frozen comparison to prepare

- Use only the existing old child adapter `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3` and the existing Qwen3-4B-Instruct-2507 base.
- Use eight already selected 64-item contexts from the frozen grammar160 DATA:
  the first four TREC contexts in its declared order and all four SST contexts.
  Keep their exact question order and input IDs. They are developmental/exposed
  once the predecessor runs, not new independent test data. No outcome selection.
- Seeds: 981264101 and 981264102. Cross four representations with two decoding
  modes on every context/seed: 4 × 2 × 8 × 2 = 128 calls.
- Representations: ordinary anonymous label array; the existing ID-to-label
  object; an ordered array of objects `{"tag": "q0001", "label": "entity"}`
  using each corresponding input ID; the same ordered object array with the
  task-irrelevant literal tag `q0000` in every element. This literal is not an
  input ID. The last two arms use identical object/key structure.
- Use free output and exact-schema output for each representation. Within a
  representation, requests differ only in the structured-output field. Preserve
  system/tool definitions, task definitions and ID-bearing inputs. Output
  instructions may truthfully explain the representation; record their difference.
- Exact schemas require all 64 positions/IDs, canonical label values, no extra
  properties and exact tags. Label choices remain unconstrained among the task's
  valid labels; no gold values enter prompts or grammars.
- Use the existing qualified sampling defaults: temperature 0.5, full support,
  a common 3,072 output-token ceiling and 8,192 context window, four concurrent
  HTTP calls, 120-second per-call timeout, no retries. Collection cap 900 seconds;
  proposed inclusive owned-service envelope 1,800 seconds. These are caps, not
  promised durations. Every request plus cap must fit before launch.
- Counterbalance the eight cells within each context/seed. Record dispatch order.
- Choose and report tags before inference. Audit tokenizer lengths for tags and
  synthetic label outputs across every canonical label. Do not call placeholder
  padding perfectly neutral or equal actual compute: variable labels, serialization,
  prompt text and free-response behavior can still differ. Preserve actual token
  counts and report any remaining length mismatch.

## Primary measurements

Report complete/valid output rates; strict correct assignments per planned
context; position-wise label accuracy; complete-batch correctness; and exact
aggregate counts computed offline from fully aligned outputs. Wrong cardinality,
malformed JSON, wrong tags and unexpected IDs are model output failures, not
infrastructure failures. Their semantic alignment is unavailable, not 64 proven
semantic label mistakes. Infrastructure/unrun outcomes stay null. Do not repair,
pad, truncate, accept prefixes, normalize aliases or execute generated code.

Primary contrast is meaningful-tag versus placeholder-tag within the same
decoding mode. The anonymous and map-ID arms bridge to prior results. Inference
is grouped by source context (four per task), not by 128 independent samples.
Keep TREC and SST separate. Record all raw requests, responses, token IDs when
available, provider model identity, usage including missing cache fields, wall
times, stop reasons and source/input hashes. No training or checkpoints are needed.

If meaningful tags beat placeholders with comparable realized token lengths,
that strengthens a record-correspondence interpretation. If both improve similarly,
extra structure or segmented generation is a plausible explanation. If only
grammar-constrained arms work, narrow the conclusion to decoder-supported output.
These patterns motivate follow-ups; they are not automatic publication criteria.

## Implementation boundary and completion contract

Prepare only in the new isolated namespace
`sidecars/leaf-anchor-padding-control-v1/`; keep research source/artifacts outside
the main repository and do not modify any live or frozen source file. Reuse
qualified anchor/grammar collector and lifecycle helpers with private imports
and explicit source pins. Inspect dependencies before executing them. Do not
install or mutate an environment, launch a model/service, signal processes, or
write parent acceptance. Main owns GPU launch and automatic handoff integration.

Use focused test-first checks for strict scoring, cardinality/duplicate/tag errors,
paired request equality, label-blind data selection and the complete grid. A few
real CPU boundary checks suffice; no broad suite or new framework. Compile schemas
and qualify typed-template prompt IDs in the existing native environment. Use
`apply_patch` for source edits. Raw outputs stay absent during preparation.

Deliver a readable DESIGN/README, frozen DATA/SPEC, source/input hashes, focused
test evidence, and exact proposed owned launch argv. If existing lifecycle cannot
be reused without a material interface change, return that specific issue and a
CPU-ready collector instead of building a new scheduler. READY must describe
exactly what is qualified. Do not delegate further.
