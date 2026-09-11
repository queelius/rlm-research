---
title: "QS semantic review, indices 000–053: additive coverage correction"
date: 2026-09-10
status: complete
scope: "49 observed endpoints among 54 planned slots"
---

# QS semantic review 000–053 — V2 correction

`SEMANTICS_000_053.json` was built with an incorrect `native.available` filter. That omitted 12 authenticated, completed traces whose native final was empty. They are observed policy failures scored zero, not infrastructure NULLs. The original files and hashes are preserved; `SEMANTICS_000_053_V2.json` supplies the missing manual annotations and corrected totals.

The corrected inventory is 49 observed endpoints and five true NULL slots among indices 0–53. Across the 49 observed traces, 47 made at least one successful child acquisition, 40 retained a complete map usable in principle, 36 displayed a computed scalar used by the final, 16 faithfully executed the requested operator and scope, and 10 were both faithful and strictly correct. Strict success remains 20: ten other correct answers did not follow the requested operation. The 12 newly included empty-final traces add no strict or faithful success.

The added failures are informative. Five retained a complete scoped/full map but never completed the requested reduction (2, 24, 33, 43, 50); six acquired some or all child labels without a usable joined map (5, 22, 28, 29, 40, 42); and one never successfully dispatched a child (9). This preserves separate acquisition, retained-state, requested-operation, and final-use judgments rather than treating an empty final as missing infrastructure.

No generated program was reexecuted. Judgments use the exact programs and recorded tool observations in `SEMANTIC_PACK.json`; `qs_problem.py` was consulted only for task semantics.
