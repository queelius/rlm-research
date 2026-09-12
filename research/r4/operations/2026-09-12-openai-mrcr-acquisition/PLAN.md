---
schema: research-asset-acquisition-v1
created_utc: 2026-09-12T13:32:00Z
owner: MAIN
status: acquired_hash_verified_CPU_inventory_in_progress
dataset: openai/mrcr
revision: f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d
license: MIT_as_declared_in_pinned_dataset_card
expected_data_bytes: 457342038
acquisition_cap_seconds: 900
GPU_queries: 0
---

# A separate source for a more substantial conversation-transfer test

Question enabled: does a learned external-context retrieval procedure transfer
to new conversations, rather than new questions over the same conversation?
Acquire only the two public two-needle Parquet shards and pinned card. Do not
execute dataset-provided code. A read-only CPU inventory will determine actual
row count, length distribution, distinct contexts, exact dialogue-pair overlap,
and scoring/schema compatibility before any split or GPU admission.

This is OpenAI MRCR, not the Google DeepMind MRCRv2.1 CSV release used by the
current calibration. Its card declares MIT and documents a December2025 data
correction. Its shown scorer requires the marker at the beginning of the answer;
our existing DeepMind scorer searches for the last marker. Neither scorer may
be silently substituted for the other. [Pinned primary dataset card](https://huggingface.co/datasets/openai/mrcr/blob/f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d/README.md).

HF metadata was read without authentication at13:31UTC. Expected LFS SHA256:

- `2needle/2needle_0.parquet`,190822058bytes:
  `1c297b254bf64a31856b74918cd7db889a214503e0b67daa834e84f20df6aa93`.
- `2needle/2needle_1.parquet`,266519980bytes:
  `a5a1dc9ccc945623253d04d33c03d89aee2d676c88955ce368da2ab16a0ce94d`.
- `README.md`,4672bytes,Git blob
  `db895a636cce2ea3406f900b9817099b98303a9a`; record local SHA256 after retrieval.

New MAIN-owned cache only:
`/project/alex_phd/research-cache/datasets/openai-mrcr-f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d`.
No cache migration, deletion, model queries, training split designation, or
changes to existing frozen five-context data. A future small comparison might
use32 train conversations and16 held conversations, four training samples each,
one root-only update and paired evaluation, on one A10040GB. Its runtime cap
must be informed by the currently queued actual-root calibration.

Promote this asset if its inventory supports genuinely disjoint new contexts
and a clear authentic query/answer contract. Revise or retire if overlap, data
errors, or context representation make it unsuitable. Acquisition overlaps the
active GPU run and does not displace any ready experiment.
