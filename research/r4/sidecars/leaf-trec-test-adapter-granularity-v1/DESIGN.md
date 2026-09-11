---
id: leaf-trec-test-adapter-granularity
status: exploratory_preparation
question: Does c32's exposed-context semantic gain transfer to the complete official TREC test source, and does batch width change that gain?
date: 2026-09-10
---

# Official-test base/c32 granularity comparison

Evaluate every one of the 500 source lines in the pinned official `TREC_10.label` file. Preserve duplicate normalized questions if any and report normalized grouping; never select or discard a row by model outcome. Use a deterministic SHA-ordered record list and stable per-source-line IDs. The source contains 500 distinct normalized groups. Eleven groups overlap the raw TREC train source, but the frozen c32 split excluded them from optimizer training; all 500 have zero normalized-group intersection with the 5,065 groups actually used for c32 optimization. The earlier c32 selected-test evaluation exposed 489/500 groups; this is therefore a partly research-exposed external validation, not a pristine test.

Cross base versus fixed c32 checkpoint0128 with wide100 and small16 contiguous batching. Each model/width condition sees all 500 records under two fresh paired seeds, 991902701 and 991902702. Wide uses five calls and small uses 32 calls per model/seed, including the unpadded final four-record batch: 148 calls total. Alternate model order within batch and arm order across seeds. Within each batch, requests differ only by model dispatch. Keep the qualified Qwen3-4B native template, six-label exact-ID grammar, temperature0.5, top-p1, maximum2,048 generated tokens,8,192 context, four workers,90-second request cap, and no tools/root calls.

Primary reporting is c32-minus-base per-record accuracy at each width, followed by the difference between those effects. Report paired seed results and coarse-class strata. A completed malformed/wrong output is observed zero for every requested label; missing or unauthenticated endpoints are NULL with bounds. Preserve every request/raw response/result; never repair partial maps or retry a scientific coordinate. This is leaf classification, not root end-to-end performance, and no artificial aggregate task is introduced.

Use 1,800 seconds outer,1,650 work,1,770 owned: startup180 within work,30 collector harvest reserve,90 release,30 finalization,30 outer margin. The result supports transfer if c32 improves over base by at least five percentage points at either width with the same sign at both widths and across both seeds; that is a practical follow-up gate, not equivalence testing or publication evidence. Class-specific regressions, NULL imbalance, or a gain restricted to the 11 raw-train-overlap groups revise the interpretation. Two seeds and correlated records/near-duplicates limit inference.
