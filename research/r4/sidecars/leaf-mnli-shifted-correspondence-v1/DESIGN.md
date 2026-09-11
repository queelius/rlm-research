# MNLI requested-tag correspondence32

Approved adaptive mechanism test on the eight already research-exposed MNLI48 contexts. The
released Qwen3-4B base receives a common final-only/no-tools prompt. Every displayed record has
an explicit `requested_tag`; matching uses its own public ID and shift17 uses the ID from
`(i+17)%48`. Both arms therefore have the identical tag multiset, text, order, grammar, sampling,
and output diversity. The generic shape grammar constrains cardinality, fields, tag pattern and
labels, but never literal IDs.

Eight contexts x two fresh paired seeds x two arms = 32 calls. Primary is strict displayed-label
count after whole-contract validation; completed invalid output is zero and unavailable transport
is NULL with bounds. Requested-tag fidelity and shifted named-record accuracy on the frozen
different-gold subset are diagnostics only; no repair, reordering or rescoring. This is not a fresh
source replication or an exact continuation of the prior MNLI80 prompt.

One released base, four workers, 90-second requests, max3072. Caps:1200 outer,1170 owned,1080
work,90 cleanup,30 outer margin; startup is included in work and capped at180 seconds. No retries.

