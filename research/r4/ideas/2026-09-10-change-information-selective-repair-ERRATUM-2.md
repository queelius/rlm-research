---
status: additive_erratum
date: 2026-09-10
---

MAIN corrected its earlier statement about the physical ceiling mapping. The exact sealed mapping is
two 32-record chunks for each size-64 episode and eight 32-record chunks for each size-256 episode:
`4×2 + 4×8 = 40` calls. The earlier `4×16` description would imply 48 calls and was incorrect.

READY `33c91b7b...` was withdrawn before launch because its producer summary encoded that mistaken
four-chunk size-64 expectation. No scientific call or outcome existed. The v1 sidecar remains
byte-preserved; replacement v2 derives required chunk membership from the frozen 40-row plan.
