# Leaf output-scope implementation plan

Goal: ready72-call three-arm job without GPU or server work.
Architecture: isolated new sidecar; privately import the qualified correspondence
collector/schema/weight helpers. study.py owns only request selection/mapping and
analysis; driver.py owns freeze/bind/live-metadata/collection handoff.
Spec: DESIGN.md, accepted by parent. No worktree/core edit or Git integration.

1. TDD data and request invariants in test_study.py: four exact partitions,
   byte-identical full blocks, identical targeted prefixes, no host-gold influence,
   declared enum cardinality, source order and immutable JSON round trips.
2. TDD score/cost alignment and actual inherited collector with a real HTTP mock
   transport: malformed outputs remain unaligned, wrong aliases retain costs,
   original-position quartiles/counts/pairing and repeated-prefix cost are explicit.
3. Freeze all72 bodies from sorted runtime JSON; use the existing vLLM protocol,
   XGrammar compiler and CPU chat template to validate both schemas and prompt IDs.
   Reuse exact old-weight binding and live alias/root/base gates;1200s/four workers.
4. Fresh focused tests and source/input verification; publish READY last and give
   parent the exact bind/run commands. No automatic generation or service startup.
