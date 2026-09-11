---
id: leaf-trec-test-adapter-granularity-implementation
status: cpu_prepared_not_launched
date: 2026-09-10
---

# Official TREC-test adapter/granularity package

The package freezes all 500 official `TREC_10.label` source lines in a deterministic SHA order. They are 500 distinct normalized question groups; no deduplication or selection was applied. Eleven overlap the raw TREC train source, but the prior source partition excluded those groups from both the c32 optimizer corpus and its earlier selected-test evaluation. Thus all 500 are outside the 5,065 optimizer groups, while 489/500 were already evaluated in prior research and are not pristine.

The exact inventory is 148 calls: base/c32 × wide100/small16 × two paired seeds. Each of the eight model/width/seed conditions covers all 500 records exactly once; final batch sizes are100 and4. Within a batch, paired bodies differ only in the exact model field. Maximum prompt length is3,428 tokens and remains within the fixed8,192 context plus2,048 output admission. No root calls, model calls, service starts, downloads, or GPU work occurred during preparation.

The implementation reuses the qualified four-worker collector and owned dual-model lifecycle by pinned source, while the new protocol retains exact native model/choice/token/logprob/usage authentication. The new owner has the same1,800/1,650/1,770 outer/work/owned clocks and90-second release bound as the completed152-call study. Ten focused CPU tests cover source inventory and classes, optimizer intersection, all-condition coverage, variable last batches, duplicate-ID failure, exact model dispatch, paired frozen bodies, native renderer authentication, and seed collision receipt.

The underlying TREC data license remains unspecified; the cached source is pinned by content hash and source URL without inventing a revision or redistribution grant. This is a child-classification transfer test, not root end-to-end evidence.
