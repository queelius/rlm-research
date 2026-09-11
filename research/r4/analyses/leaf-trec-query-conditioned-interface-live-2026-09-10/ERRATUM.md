---
id: leaf-trec-query-conditioned-interface-v1-report-erratum
date: 2026-09-10
status: additive_correction
---

# Report interpretation and method correction

The report's proposed follow-up—projecting a completed six-label map in ordinary
code—duplicates the study's existing `full6` scoring path. Full-six outputs were
already host-projected to A/B/other for the common comparison. The supported
local decision is therefore to prefer the existing full-six-plus-host-projection
interface. Distinct future questions are whether training on the new compact
contract with new training groups changes this result, or whether a root can
consume the host-projected map. Repeating the same projection is not informative.

The report also overstates this audit reader's request check as independently
“re-rendering” prompts. This reader compared every recorded parsed body and
transport-byte hash to the frozen request bodies, then authenticated native
model/token/usage/finish/content fields. It did not rebuild tokenized prompts
from source text. MAIN's separate adoption check may do that; it is not evidence
produced by this reader.

All numeric results, native availability, costs, and the original sealed files
are unchanged.
