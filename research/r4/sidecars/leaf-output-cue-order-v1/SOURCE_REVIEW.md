# CPU preparation and material seams

Implementer's preparation report, not an independent code review. Parent owns
independent review and any GPU acceptance. No historical sources, environments,
model weights or live services were changed. All new files live in this sidecar.

The approved plan and focused TDD workflow shaped this implementation: six study/
ownership assertions failed before their code existed; three driver assertions
failed before the driver existed. All nine pass after implementation. Final
CPU_TESTS.json records a fresh run's exit/stdout/stderr. Tests exercise real study
selection/dispatch, unchanged paired messages, ordered-body identities, strict raw
order validation, duplicate/extra/cardinality rejection, honest diagnostic versus
primary score, null/invalid separation and shared-work cleanup reserve. Six fake
HTTP successes cover both orders ×three tags using the actual inherited collector;
a separate single500 fixture proves stop/null/no retry (seven fake requests total).
Those fake token IDs are not the native physical-prompt proof.

CPU_QUALIFICATION.json independently reproduces all48 approved feasibility
requests through installed vLLM typed tools, native cached tokenizer and actual
XGrammar compiler/matcher. All24 order pairs have identical full prompt IDs.
All48 designated complete64-object strings are accepted and all48 opposite-order
strings rejected. Sixteen distinct *ordered* schemas are compiled; valid reuse
occurs across repeated seeds and task-identical constant/ordinal grammars, never
by sorted-key identity. Max input2838 plus3072 allowance=5910. Synthetic labels
are the first enum only for grammar proof; actual output tokens may differ.

study.py reads authenticated identity384 SPEC and selects its lowest two indexes
per task. It preserves complete original request bodies except approved seed,
neutral instruction and schema-order changes. Exact request/schema/token hashes
must reproduce the parent's a8fad088 feasibility proof. Scoring parses duplicate-
rejecting raw ordered objects first, validates assigned order, then passes original
unchanged content into the frozen semantic scorer. Wrong-order raw output is not
repaired or silently interpreted under the other arm. Raw order counts and all
original bytes remain available. Previous-record agreement is explicitly secondary.

driver.py privately extracts the hash-authenticated counter collector's run and
weight-authentication functions. Only48-call count and780/900 clocks change in
run. The ordered wire hook rejects a properties-only reorder even when Python
dict equality and canonical hashes match; captured bytes are exact. Existing
version/models/alias/token-ID/usage checks and no-retry null behavior remain.
READY retains canonical request hashes for inherited interfaces *and* distinct
ordered request/schema identities. No grammar deduplication uses insensitive keys.

owned.py privately adapts the qualified single-adapter lifecycle for48 and780/900
clocks. It reuses the observed process-exit-race fix by authenticating and extracting
only observe_or_absent from root-seed-lifecycle-continuation-v1: only missing/exited
process exceptions become absent. The frozen suite/V2 lifecycle retains process-
start identities, PRL::Inference handling and owned-only cleanup in finally. No
acceptance or scheduler is created. Counter/source patch counts and derived source
hashes are frozen in SOURCE_ADAPTERS.json. Fixed c32de disk/config/base identity
is authenticated once per stage, with ordinary auto/BF16 inference cast recorded.

SEED_AUDIT.json names exact searched source paths/hashes and scope. It is not a
global seed uniqueness claim. All source/provenance closures and new assets enter
SPEC; READY is the last preparation publication. No further source changes after
READY. `owned.py --verify` is the final read-only acceptance check.

Limitations: exposed contexts, two clusters/task, one historical child, same-support
public data, unknown historical/pretraining overlap; generic JSON-order effects
are not novelty. Concurrent order/cache exposure is not perfectly controlled.
Collection600/work780/owned900/outer930 are distinct; pre-main import time belongs
to outer. The small built-in summary precedes release, while independent audit
must follow it. An attempted dispatch does not prove server sampling. Invalid
outputs have zero strict score but unavailable alignment; nulls are not negatives.
