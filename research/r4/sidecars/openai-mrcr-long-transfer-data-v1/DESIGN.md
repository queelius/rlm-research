---
schema: openai-mrcr-long-transfer-data-design-v1
status: data-freeze-only
selection_namespace: mrcr-long-transfer-20260912
source_revision: f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d
planned_records: 16
gpu_queries: 0
---

# Long-input MRCR transfer prerequisite

## Question

Does the same fixed procedure transfer to OpenAI MRCR inputs whose external context is too long for
the root's 8K neural context to absorb through a whole-file dump? This data artifact enables a later
paired no-adapter base versus fixed procedural-SFT checkpoint 32 comparison. It does not admit that
comparison, alter model weights, or claim learned decomposition.

## Frozen selection

The source is the pinned 800-row `openai/mrcr` two-needle inventory. Eligible rows have inclusive
o200k prompt-content-plus-answer length 16,384--32,768 tokens. The token count describes the direct
source conversation, not the later root neural prompt: the full original JSON stays in an external
file and only the ordinary final question plus fixed harness instructions enter the root prompt.

Before ranking, exclude all 48 short records already used in local train or held readouts. Also
exclude a candidate if it shares any exact User--Assistant core pair with those records, if its
target answer appears in any exposed core, or if any exposed target answer appears in its core.
Rank what remains by
`SHA256("mrcr-long-transfer-20260912|" + source_row_sha256)`. Greedily accept rows in that order
only when the same exact-core and bidirectional target-to-core conditions also hold against every
already accepted row. The cohort is feasible only if this produces 16 rows; the length band and
cohort size are not silently changed.

Selection uses no model response, score, or answer content. Host truth is read only after the rank
is fixed and is stored mode 0600. Each public row retains the original prompt JSON bytes, final
question bytes, source row/shard/ordinal hashes, target occurrence disclosed by the original
question, official schema fields, and length measurements. The official scorer is copied
byte-for-byte from the previously pinned OpenAI MRCR data artifact.

## Later comparison—not implemented or admitted here

The smallest follow-up is one fresh frozen seed on each of these 16 contexts for both the
no-adapter 4B base root and checkpoint 32, with the same zero-adapter child, six total root/child
turns, and raw exact plus official similarity. Provisional caps are 900 seconds per owner. The
experiment-scoped whitespace-preserving terminal parser must be fixed and authenticated before an
evaluator is sealed; neither the stripped historical parser nor a repaired score may be mixed into
this data freeze.

## Claim limits

This is same-task length transfer within one synthetic public source. The common few-shot remains,
base-pretraining exposure is unknown, and exact hash disjointness does not establish semantic
independence. Passing 16 contexts would be local exploratory evidence, not broad long-context or
generalization evidence.

