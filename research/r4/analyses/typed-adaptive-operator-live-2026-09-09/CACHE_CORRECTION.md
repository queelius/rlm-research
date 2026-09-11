# Additive correction: cached and uncached input are known

This note supersedes only the original REPORT/METRICS statement that cached input was unknown for all120 calls and uncached totals could not be reported. Original REPORT.md, METRICS.json and SEAL.json remain unchanged. Main's independent primary audit identified the error; a fresh implementer recomputation from all120 raw role-wire records confirms it and matches MAIN_PRIMARY.json on every group and joint-success cost field.

Cause: the original analysis used normalized `native_response.usage.cached_input_tokens`, which is null. The original wire response is separately preserved as a JSON STRING at `native_wire_response.body`. After JSON decoding, `usage.prompt_tokens_details.cached_tokens` is an integer for every call. Thus null in the normalized representation was information loss, not missing server evidence. For example request4e52ae1577294b80bfbba114ff2cf23e has1125 prompt tokens and1120 cached tokens in the raw wire body, despite normalized cached_input_tokens=null.

| Physical arm | Calls | Prompt | Cached | Uncached | Completion |
|---|---:|---:|---:|---:|---:|
| User all16 | 48 | 55,258 | 51,616 | 3,642 | 6,931 |
| User filter16 | 8 | 7,786 | 6,944 | 842 | 568 |
| Shared global, counted once | 64 | 73,648 | 63,968 | 9,680 | 9,238 |
| Physical union | 120 | 136,692 | 122,528 | 14,164 | 16,737 |

For the six jointly correct user pairs, all→filter cached input is51,616→5,200 and uncached input is3,642→632, an82.65% uncached-input reduction. Original call/prompt/completion reductions remain87.5%/89.4%/93.8%. These token quantities are observed resource accounting, not directly measured FLOPs or billing. All primary scores/nulls, syntax/classification findings, timing and infrastructure limitations remain unchanged.

CORRECTED_COSTS.json contains all120 request IDs, exact raw source paths/hashes, extraction field, per-call counts, group/paired sums and the independent comparison. `cache_correction.py` reads only those raw files plus existing metrics/main output; it makes no model call and changes no earlier artifact. MAIN_PRIMARY.json SHA `8f05db4f033e77d9defcccc860277e2ea6b9c51fd092e832bd2f1fa643f77733` independently agrees. This correction is implementer-authored; the independent evidence remains main's separate source and output. Review-verification was applied by checking the actual raw representation before publishing this correction.
