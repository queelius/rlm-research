# BROAD16 stopped before its first update

Independent CPU audit under the [pre-outcome method](METHOD.md). **Zero optimizer steps; no result for the fixed-final16 primary comparison.** The original root completed validation0 and the first 24 training attempts, then export stopped on an unrecognized spelling/boundary of an unsampled child-context rejection. This was not a failed optimizer step or proof that the curriculum has no reward variance. The original STOP, sources and outputs remain unchanged.

## What actually ran

| Stage | Planned / recorded | Raw exact outcomes | Graph-valid outcomes | Root returned calls | Child returned / rejected |
| --- | --- | --- | --- | --- | --- |
| Validation0 | 16 / 16 | 5 correct, 11 wrong | 15; five correct, one raw zero excluded | 35 | 197 / 5 |
| Training round1 | 24 / 24 | 9 correct, 15 wrong | 21; nine correct, three raw zeros unadmitted | 53 | 566 / 6 |

Every retained terminal was observable; neither collection reported episode-budget censoring. The excluded/unadmitted episodes still have their raw zero outcomes, but their training values remain null. Validation's saved export authenticates 15 admitted episodes and one existing narrow-overflow exclusion. Training export and GROUP were never committed. Of the full 560-episode plan, 520 were never attempted; they are not model failures.

The three training groups were 16-record HUM (6/8 raw exact, seven graph-valid), 32-record NUM (3/8, eight graph-valid) and 64-record ENTY (0/8, six graph-valid). The first two contain mixed rewards among unchanged graph-valid rows: **15 potentially usable rows in total**, solely a diagnostic count—not newly admitted data, a replacement GROUP or authorization to update. Size, target class and source context are confounded in this one round; do not infer a length effect from those three rates.

## Precise stopping boundary

All 11 rejected calls are depth1 requests to the authenticated fixed child, HTTP400, with no sampled graph node, usage object or native completion. Eight have decoder prompt length greater than8192 and match the already recognized family. Three requests in training episode `bc2608598befba7a342f6caed172da6b37296829eda6eaae31b51e51e09d63c8` have length **exactly8192**; the server reports that adding at least one output token exceeds8192. The inherited recognizer requires the other exact error wording and a prompt strictly greater than8192, so it raises `not the explicit decoder-context overflow rejection` before writing the training export. This is an export admission-boundary stop after collection, not a root request rejection or a GPU lifecycle race.

All862 physical attempts have corresponding request/result records: 88 root returns, 763 child returns and 11 child errors. No root unsampled rejection or request-only remainder was found. The four affected episodes used 670/862 attempts (77.7%):

- Validation `4c521e610b18…`: 155 calls, five rejected, 417.03 seconds.
- Training `06b816719944…`: 239 calls, two rejected, 535.15 seconds.
- Training `bc2608598bef…`: 170 calls, three rejected, 276.22 seconds.
- Training `fe197cdef3f4…`: 106 calls, one rejected, 333.56 seconds.

Their durations overlap and must not be summed as wall time. The three training cases account for 515/625 calls (82.4%). This identifies a useful cost/failure-mode investigation; it does not yet explain whether calls came from repeated root dispatch, child tool use or runtime recovery. That source/trace diagnosis is a separate follow-up.

## Lineage, masks and costs

Actual requests bind original root `857a7ce6…` and fixed child `c32de129…`, native Qwen3 thinking rendering, T0.5/full support and the declared seeds. Generation1 points to original step0 with no optimizer/RNG/checkpoint state. Successful complete graphs preserve physical prefix/action IDs and sampled log probabilities, root-only masks and semantic depth links. Four failed-call graphs remain unadmitted; no repair or call removal was performed. The 36 graph-valid episodes contain 66 root turns/20,423 candidate action tokens, but **none received a gradient**. There are no new adapter deltas, correction captures, optimizer state or selection/transfer results to audit.

Returned-call usage totals: 1,903,717 logical prompt tokens, 1,799,840 cached and 103,877 uncached; 132,926 observed completion tokens. Root completions were29,512; child completions103,414. Rejected requests carried another100,392 wire prompt tokens, so attempted prompt total is2,004,109; their provider-reported/billed usage is unknown, not zero. Their lack of sampled outputs is separately verified.

Campaign elapsed1170.54s; accepted child1173.78s (19.56min), exit1/no timeout. Validation collection505.36s, training583.82s, service start-to-ready42.28s, optimizer0s. Owned-service release records verify all observed parent/descendant identities gone and ports free; accepted exit records an empty GPU. Release-to-child-exit was approximately0.57s, with no large post-release analysis tail in this operation.

## Evidence and limits

[METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json") contains per-episode/raw-call projections and exact source pointers; [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") records cached identities; [SUMMARY.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SUMMARY.json") adds the saved-validation-manifest and failed-call checks. The successful snapshot performed10,357 checks in about6.3 CPU seconds, with one physical read per cached path and no per-episode source-closure hashing, GPU locks, model calls or process signals. Three focused null/admission projection tests pass.

Two analysis-only assumptions were corrected and disclosed: audit filenames are not physical request IDs, and missing completion markers are null rather than files. The latter interrupted finalization after scoring, requiring one repeated40-episode projection; no inference was rerun. This is a deviation from the intended stage-once method, not omitted from the record. No frozen/live source was changed.

The meaningful next decision is whether to preserve this precise unsampled-boundary case in an additive, explicitly reviewed continuation while retaining null admission for affected episodes; another agent owns that source decision. Independently, explain the high child-call concentration before changing any budget or role contract. No claim about broader-root learning, transfer, semantic coverage or reward hacking follows from this zero-update STOP.
