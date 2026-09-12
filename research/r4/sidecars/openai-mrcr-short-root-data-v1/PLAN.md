---
schema: openai-mrcr-short-root-data-freeze-v1
status: approved_CPU_data_only
namespace: openai-mrcr-short-root-v1-20260912
training_records: 32
heldout_records: 16
GPU_queries: 0
optimizer_steps: 0
---

# Outcome-blind short-pool freeze

Use the89 singleton exact-core components among the101 source rows at≤8192 `o200k_base` prompt-content-plus-answer tokens. A singleton shares no exact core user/assistant pair with any other row in that101-row candidate pool. Rank by SHA256 of UTF-8 `openai-mrcr-short-root-v1-20260912|FULL_ROW_SHA256`, tie full-row SHA, assigning first32 training and next16 heldout. No prediction, reward, answer content, desired index, topic or target occurrence selects rows. Existing full800 overlaps and common few-shot content remain explicit limitations.

Before materializing model inputs, validate the visible final question against the target-user ask, its one-indexed occurrence and marker. Audit selected answers against all shared demos using exact and whitespace-normalized containment. A newly found labeling/demo issue stops the freeze without reranking. Preserve rank commitment and diagnostic errors; do not hand-rewrite queries.

Keep each source prompt's original JSON-string UTF-8 bytes and exact final-question text. External context is that original JSON document, not a lossy reconstructed transcript. Future model-visible metadata may state type and size only; no target/needle position, answer length, source split, parser recipe or extraction hint is added. Host gold lives separately in a0700 directory and0600 file. Raw source conversations necessarily contain their assistant messages; no additional gold answer is placed in model inputs.

New files are confined to this data sidecar: preparer/scorer/verification, committed ranking, input JSON/query files, protected gold, manifest and DATA_READY. Original dataset, inventory, existing DeepMind five-context freeze and every live owner stay unchanged. Cached Qwen3-4B tokenizer measurements are CPU-only inventory: external-file tokens are not the actual future root neural-prompt budget.

The later proposed question is whether a fresh base4B root-only update over32×G4 trajectories transfers to16 paired held contexts from disjoint short core components. No training/harness implementation or GPU admission follows from this data freeze. Runtime caps must use qualified actual V6 episode cost once available; V6 is currently not terminal.
