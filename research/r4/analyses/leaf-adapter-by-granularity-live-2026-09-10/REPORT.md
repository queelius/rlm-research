---
id: leaf-adapter-by-granularity-independent-audit
status: sealed_independent_exploratory_audit
study: leaf-adapter-by-granularity-v1
date: 2026-09-10
planned_calls: 152
native_authenticated: 152
null_calls: 0
claim_level: exposed_context_diagnostic
---

# The c32 adapter improved labels at both widths; smaller batches narrowed its advantage

Across the two purposively selected 256-record contexts and two paired seeds, the c32 adapter outperformed its unmodified Qwen3-4B base at both batch widths. With wide 100/100/56 partitions, c32 classified 864/1,024 records correctly versus 683/1,024 for base: a gain of 181 labels, or 17.68 percentage points. With contiguous batches of 16, c32 scored 900/1,024 versus base's 766/1,024: a gain of 134 labels, or 13.09 points.

The adapter advantage was therefore 47 labels (4.59 points) smaller at width 16 than at wide batching. That interaction is not evidence that the adapter harms small batches: c32 still gained 27–39 labels over base in every context/seed block. Rather, the unmodified base benefited more from reducing batch size (683→766) than c32 did (864→900).

| Context / seed | Wide base | Wide c32 | c32−base | Small base | Small c32 | c32−base | Effect change, small−wide |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Location-weight / 1 | 173 | 223 | +50 | 190 | 226 | +36 | −14 |
| Location-weight / 2 | 168 | 221 | +53 | 189 | 228 | +39 | −14 |
| Numeric-count / 1 | 170 | 213 | +43 | 191 | 223 | +32 | −11 |
| Numeric-count / 2 | 172 | 207 | +35 | 196 | 223 | +27 | −8 |

Host-computed target aggregates support the wide result but are more mixed at width 16. Wide c32 reduced absolute location-weight errors from 52/55 to 5/5 and numeric-count errors from 11/13 to 6/7. At width 16, c32's location errors were 5/7 versus base's 4/8, and numeric errors 2/3 versus 2/2. These host diagnostics were calculated from returned leaf labels; no root execution occurred, and they should not be reported as task success.

## Native, lifecycle, and cost audit

The independent reader validated every frozen request body and coordinate, exact model dispatch, wire hash, HTTP/raw response identity, unique provider request ID, model identity, native token/logprob and usage correspondence, finish branch, exact-ID canonical-label map, and producer score. Crucially, grouping includes `model_policy`; base requests used the full pinned base-model path while c32 requests used the bound child alias. All 152/152 planned calls were native-authenticated and whole-map valid, with no NULLs, extra physical request directories, or producer-score disagreements.

The owner was complete, error-free, and released after 262.204 seconds. Its parent exited 0 without timeout after 262.826 seconds, recorded the exact owner-terminal hash, and found no GPU PIDs after exit. Physical usage was 238,632 input tokens, 68,981 output tokens, and 177,440 cached input tokens, with no unknown usage fields. Billing and equal-FLOP cost were not measured.

## Interpretation and next comparison

This passes the study's practical semantic-effect gate: the adapter advantage exceeds five points and has the same sign in both contexts. The strongest next step is a new-source-group validation that retains both widths and the exact base/c32 dispatch control. The width interaction also argues against treating batch fragmentation and adapter training as interchangeable fixes.

The evidence remains narrow. Both contexts were chosen because earlier root runs exposed difficult child errors; there are only two context clusters and two seeds each, while record labels within a context are dependent. Width changes request count, prompt/output length, cache behavior, and overhead together. Some TREC category boundaries may be ambiguous. This is strong evidence for these exposed contexts, not a general leaf-model or task claim.
