---
id: question-sensitive-sft-new-corpus-replication-v1
status: CPU-prepared; no model outputs
date: 2026-09-10
---

# New-corpus replication of question-sensitive root SFT

Question: does the six-update QS SFT effect recur when the entire teacher corpus is rebuilt from
different TREC-train source questions, with a fresh optimizer, while the fixed24 start, c32 child,
objective, and metadata72 readout remain fixed?

The source allocation is the first 128 eligible groups by SHA-256 ordering under this namespace,
after a new named-manifest collision scan. It forms eight 16-record contexts and the same nine task
families per context. Every one of 72 teacher trajectories must contain one genuine c32 acquisition;
wrong child labels remain in the trajectory. Any incomplete corpus blocks training. Training uses the
fixed24 root adapter, fresh Adam at step zero, the qualified 504-parameter LoRA mapping, unchanged
role weights and objective, and six full-corpus updates. Only the new checkpoint is evaluated on the
existing research-exposed metadata72 plan; unchanged and original-QS6 results are referenced, not
rerun.

The planned denominator is 72. A completed wrong/malformed final is observed failure zero. Missing,
unverified, or infrastructure-failed endpoints are NULL with bounds. This is an independent training-
corpus realization, not a new evaluation panel and not confirmation by itself.

Budget: 4500 seconds outer, 4470 owned, 4320 work: 1500 capture, 1200 training, 1500 readout,
120 finalization, with 150 cleanup and 30 outer margin. No retry, refill, teacher repair, checkpoint
selection, or baseline rerun is permitted.

The approved rationale and superseded order-only proposal remain in
`ideas/2026-09-10-question-sensitive-sft-new-corpus-replication-revision.*` and
`ideas/2026-09-10-question-sensitive-sft-independent-order-replication.*`.
