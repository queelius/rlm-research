# Fresh adaptive helper implementation plan

Goal: implement the approved DESIGN.md as a thin, CPU-qualified 152-call native owner; MAIN alone reviews and launches.

Architecture: adaptive_study.py builds the frozen public-only request inventory and reuses sealed size/target wire seams. adaptive_metrics.py owns gold-free routing, staged collection and four-policy accounting. owner.py manages one native service and terminal host scoring. seal.py pins these sources, data and inherited runtime closure. test_adaptive.py contains exactly two focused fixtures.

Constraints: external independent sidecar; no changes to sealed dependencies, production repository, environments, model weights or queued jobs. Fixed original/A/B/single components, live routing commit before B/nonselected singles, 152 physical calls/512 requested output slots/128 unique records, 1100 owner/1200 external caps. Same c32, temperature0, output1024, context8192, ordered schema and five-observed-class TREC limitation. No gold read by the live selector, retries, fallback, training, best-rule selection, automatic continuation or GPU launch.

## Task 1 — implementation and CPU qualification

- [ ] Write and run two failing fixtures: actual staged routing/three-way tie/shared-cost/missing-map behavior, then real frozen partition/schema/context/native-decoder inventory.
- [ ] Add adaptive_study.py: `make_schedule()` returns 152 fixed request rows; `schedule()` restores ordered schema; `wire_send()` and `attest()` bind unchanged sealed seams; `verify()` verifies the complete closure.
- [ ] Add adaptive_metrics.py: `route(calls, public)` uses only valid O/A labels; `collect(rows, public, call_one, commit)` commits routing before further calls; `summarize(calls, rows, public, gold, routing)` separates physical and logical accounting.
- [ ] Add owner.py with immediate per-call progress, immutable routing receipt, terminal-only gold load, cleanup and full runtime evidence.
- [ ] Run the two fixtures with CUDA_VISIBLE_DEVICES empty, perform focused formatting/static checks, then seal source/data/runtime hashes and save exact command/result/environment receipts in CPU_TESTS.json and READY.json.

## Task 2 — MAIN review and launch

- [ ] Send MAIN the complete source inventory, READY hash, 152-call/context inventory and CPU receipts. Preserve sealed artifacts.
- [ ] MAIN independently reviews and may launch under the shared flock/1200-second external cap; this agent does not launch.

Execution follows the approved design inline; the user-requested external research layout and two bounded tests supersede a production branch workflow or broad suite.
