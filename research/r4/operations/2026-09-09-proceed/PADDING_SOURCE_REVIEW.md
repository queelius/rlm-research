# Padding128: independent bounded source review

Reviewed 2026-09-09, approximately 04:23–04:27 UTC. Verdict: no Critical or Important
blocking finding in the inspected scientific design, strict scoring, source binding or
single-adapter lifecycle. This is an exploratory CPU-ready comparison, not a live-service
qualification claim. Main retains acceptance, shared-lock/empty-GPU checks and launch authority.

Read the complete PADDING_CONTROL_BRIEF.md and PADDING_PREPARATION_REPORT.md; complete new
study.py, driver.py and owned.py; and the relevant inherited request/scoring, typed wire,
descriptor, suite lifecycle and complete serve.py paths. No broad tests, GPU/model calls,
process signals, outcome reads or frozen edits were performed. Parent runs the focused tests.

Independent read-only checks authenticated all 72 SPEC source/input hashes. The eight selected
contexts retain the exact source records/order/IDs; 128 coordinates use seeds981264101/981264102.
All64 free/exact pairs differ only in structured_outputs, and each of the eight cells occupies
each dispatch position once per task. The output directory was absent at review.

Scientific/scoring checks:

- Selection is first-four TREC plus all-four SST by declared source order, without labels or
  outcomes selecting contexts. The source is developmental/exposed; four groups per task,
  repeated seeds and cells are nested. TREC and SST remain separate.
- Meaningful/placeholder objects use the same keys and64-position structure. Tags derive only
  from stable input IDs or fixed q0000. Exact schemas constrain tag/shape and the full canonical
  label vocabulary, not gold labels. Free/exact bodies preserve the same prompt, tools and
  sampling. Serialization preserves insertion order; tag precedes label in schema properties.
- Whole-output JSON parsing rejects duplicate keys, missing/extra IDs, wrong cardinality,
  wrong tags, noncanonical labels and extra object properties. No prefix credit or response
  repair. Invalid completed outputs have zero strict correct assignments but unavailable
  semantic alignment; infrastructure and unrun strict outcomes are null.
- The primary meaningful-minus-placeholder contrast is paired by context/repeat/decoding mode.
  The disclosed26-token prompt difference, synthetic rather than realized length matching,
  and placeholder non-neutrality limit a pure mechanism claim; they are not blockers.

Two nonblocking readout cautions should survive the eventual report:

1. Free JSON objects are validated by key set, not lexical key order. A free response may place
   label before tag and still be semantically valid. Inspect retained key order before claiming
   that an identifier *before* the label caused an effect. Do not change scores post hoc.
2. Current cell summaries pool aligned gold/prediction label histograms. They do not by
   themselves measure per-context exact aggregate-count agreement: errors could cancel across
   calls. Per-call aligned records are retained, so compute those count comparisons separately
   in the additive results analysis before making an aggregation-accuracy claim.

Binding/lifecycle checks:

- Both the disk weight closure and actual endpoint are checked against c32de adapter/config
  and the fixed Qwen3 base. All128 frozen requests already use the one authenticated old alias;
  there is no model-name substitution at collection.
- Although the inherited helper is called dual-LoRA, start/preflight/serve iterate binding.models
  and do not require two entries on this path. With one alias also designated root, serve writes
  endpoint-original.json, exactly what the new wrapper consumes. The unused suite.final_binding
  two-model helper is not called.
- The wrapper privately imports the hash-pinned suite, which verifies the lifecycle manifest.
  It launches into a new owned directory, uses the existing authenticated PID/start/UID/PGID and
  observed-descendant release path in finally, and does not signal the predecessor. The1800s
  inclusive clock reserves120s, collection is900s, and parent provides serialization/ownership.
  Actual live version/model cards/typed prompt IDs are still checked during the run.

Reviewed identities (SHA256):

| Artifact | SHA256 |
| --- | --- |
| study.py | d8cc897b670929acc3b19c75ff9b01ee963afecf13935d92a426f88b14060a9b |
| driver.py | 045355caa4955addd1936cfb756b0ff35f8578492045cc41644c03ccc2cdbe83 |
| owned.py | 206e50a913727e0f66b6bb26002ff07ec75d7c763a4a23715f6e56c4cff65f53 |
| SPEC.json | 90d3ed6ca7acfee9f5e5c3f3dae4000ac6fc1e0f2dacceeba5fd500d69cf1f94 |
| READY.json | 9a53e3d0d758a7235376e1e12f842d08b9197da081a6ffbc2162f1fda5350521 |
| inherited suite.py | 6fa84af486efbf5bad17352553d36cd590fb6f7e386c2273df27dd8deb7c8fd1 |
| inherited serve.py | 84c23753624bcbd5694c45f81e49712a78164500bf6fe63592217085a464a835 |

Returning to terminal-only root96 monitoring. This review does not authorize a launch or edit.
