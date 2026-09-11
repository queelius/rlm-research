# Cross-generation output identity, without research adapters

Approved design: [full proposal](../../ideas/2026-09-09-qwen35-identity-design.md), SHA047114f40b19a5f2d8a60404dcc574e86cfc21987de5cdad594a6ae1469aafd5.

Exact 12 exposed sparse-source contexts, four each TREC/SST-2/AG News; two fresh seeds; plain64 labels, source-matching tag objects, constant-tag objects; exact grammar in every arm. Two released instruction/post-trained checkpoints, Qwen3 cdbee and Qwen3.5 851bf6, **no research adapters**. There is no training, model selection, new holdout or end-to-end RLM evaluation.

Source messages/system/tools remain common. Output wording/schema differs by representation, and physical templates/token IDs differ by model. Explicit non-thinking with Qwen3.5 empty-think prefix is recorded. Both runtimes use BF16, eager, no prefix cache or research FP32-head patch, explicit common sampling, no LoRA/speculation. Qwen3.5 alone skips vision and selects hybrid-cache align. These choices make a controlled new component comparison, not an exact historical throughput replication.

Primary matching-minus-constant strict assignment accuracy is reported by task/model and paired context/seed. Invalid observed arrays score0 with unavailable alignment; incomplete/provider errors remain null. Key order is a separate diagnostic, no reordered-label rescue. Matching-minus-plain, whole64 exactness, early/late positions, count errors and actual cost are secondary. Four context groups/task, two nested seeds; exposed public data and unknown pretraining overlap remain explicit.

Budget: 144 planned calls,72/model sequential;4 workers;120s/request;300s/start and900s/collection each;2400s work,2640s owned inclusive,2670s outer. Parent owns launch, inherited MIG/LD environment and shared scheduler lock. Preserve partial artifacts and stop on failed stage; release only authenticated owned service in finally. No retries, fallback service, installs or extra cells.
