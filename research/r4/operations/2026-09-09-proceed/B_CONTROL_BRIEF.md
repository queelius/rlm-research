# Add the matched mixed-size-trained baseline to the grammar-transfer readout

Decision: September 9, 2026, approximately04:14 UTC, after the completed indexed
SFT comparison. The user authorizes autonomous, adaptive research without blocking
questions. This is a bounded additive control; never modify the accepted160-call
experiment or hide that this follow-up was chosen after seeing its HF baseline.

## Why the queue changed

The completed free-output HF comparison shows Bfinal373/384 and indexed-final
374/384 at size64 with IDs, both6/6 valid. That does not establish an additional
benefit from specialized ID-target training. Comparing only the old short-trained
model with the ID-trained model could misattribute mixed-size training effects.
Add the missing B baseline on the exact grammar160 tasks and decoding conditions.

## Exact comparison

- New isolated namespace `sidecars/leaf-grammar-B-control-v1/` only.
- B model is `sidecars/leaf-mixed-size-sft-v1/B/outputs/attempt-001/checkpoint-0204`,
  adapter SHA `59ad854293142161f6b5e613dd5d1e3630fed600637106d5eae2cbcd764e9200`.
  Authenticate its config and source SFT provenance too. No weight update or
  checkpoint selection. Use the existing Qwen3-4B-Instruct-2507 base.
- Reuse all ten exact contexts, order, IDs, labels, formats, schemas, tools,
  renderer, sampler, caps and seeds from frozen `leaf-indexed-grammar-transfer-v1`.
  Do not regenerate or resample its data. One weight × two formats × two decoding
  modes × ten contexts × two seeds =80 calls.
- Only the model alias/weight changes relative to the corresponding accepted
  grammar160 requests. Preserve actual prepared prompt-token arrays and grammar
  bytes, not just source text. Keep a parent-coordinate crosswalk independent of
  execution paths. Bind the chosen B alias truthfully to its exact checkpoint.
- Temperature0.5 and full-support sampling,3,072 output-token cap,8,192 context,
  four concurrent calls,120-second HTTP timeout and no retries, as in grammar160.
  Collection cap900 seconds; proposed owned overall cap1,800 seconds. These
  proposed timing caps do not change per-request generation or the accepted160.
- Freeze a deterministic/counterbalanced order and record it. B is collected in
  a later service stage, so comparison with earlier old/new readouts is not a
  contemporaneous fully interleaved three-weight experiment. Disclose this limit;
  a promising effect may merit a subsequent interleaved replication.

## Measurements and interpretation

Reuse strict whole-output parsing and record alignment. Report all four cells
per task; primary contrasts compare B with indexed-final within each format and
decoding mode. Preserve validity, semantic accuracy, entire-batch correctness,
position effects, actual model/prompt identity, raw request/response, all token
usage including missing cache fields, stops and elapsed time. Invalid output
provides unavailable semantic alignment, not64 established wrong labels;
unrun/infrastructure outcomes stay null. Do not repair, accept prefixes or
execute generated code. Source contexts are the grouping unit, six TREC/four SST.

If B and indexed-final remain close, retain the simpler training interpretation:
the chosen output interface and broad mixed-size training may suffice on these
tasks. If a gap appears only on SST or without grammar, isolate that interaction
and replicate before calling it general ID competence. The earlier HF result and
new readout are different samplers/runtimes and must not be pooled as identical.

## Implementation and handoff

Prepare CPU-only using private imports of the qualified grammar collector and
strict scorer. Do not modify any frozen module or an active process. Existing
suite/start_service supports a single alias via its binding map; the padding
control preparation is exercising that unchanged path. Coordinate the interface
with its agent rather than creating a new scheduler or installing dependencies.
The source in your own namespace can be developed independently; only reuse
another newly prepared source once it has been frozen and main has reviewed it.

Use focused test-first checks of the80-coordinate crosswalk, unchanged physical
prompts/grammar except alias, strict scoring/nulls, real fake-HTTP collection and
owned invocation bounds. Compile/qualify in the existing native Python with GPUs
hidden. Write source edits with `apply_patch`. Preserve all source/input hashes.
No service/model calls, process signals, environment changes or parent acceptance.

Return a readable design, frozen SPEC/DATA or exact immutable data reference,
test/qualification evidence, READY describing its actual scope, and the exact
proposed owned command. Main reviews and grants GPU launch authority separately.
Do not add a generic API or broad test suite. Full report belongs beside this
brief as B_CONTROL_PREPARATION_REPORT.md. No subagents.
