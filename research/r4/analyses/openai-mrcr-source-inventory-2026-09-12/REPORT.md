---
schema: openai-mrcr-source-inventory-readout-v1
revision: f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d
rows: 800
GPU_queries: 0
training_split_designated_by_this_inventory: false
raw_answers_published: false
---

# Usable source, with overlap boundaries that matter for learning

All800 rows in the two400-row Parquet shards passed schema/role pairing, desired-user-index, next-assistant gold equality, prefix, exact two-needle count, whitespace-normalized needle count, message-count and character-count checks. The pinned LFS SHA256s match MAIN's acquisition receipts. Python3.12.12/pyarrow24.0.0/tiktoken0.13.0 completed the full batchwise inventory in32.2s. No model, split or optimizer was used.

The eight fields are `prompt`, `answer`, `random_string_to_prepend`, `n_needles`, `desired_msg_index`, `total_messages`, `n_chars`, `date_added`. `prompt` is JSON messages: message0 is a few-shot user message, messages1 through penultimate form user/assistant pairs, and the last user message is the final query. All desired indices point to a core USER; removing the answer marker yields exactly the next assistant message. Target occurrence is first402 times and second398 times. All800 markers and all800 ordered core conversations are distinct.

Distinct ordered conversations do not mean disjoint constituent material. There are43,791 exact core user/assistant pairs over406,690 occurrences;43,730 pairs occur in multiple rows. Every target answer and target pair occurs in another row's core. There are798 unique target answers:796 used once as targets and2 used twice. This is not a defect in a benchmark intended for evaluation; it changes what a newly constructed training/heldout split may claim.

Both the core-pair and target-answer-exposure graphs have exactly two components:723 original-date rows (`04-12-2025`) and77 correction-date rows (`12-05-2025`). Between these components there are zero shared exact core pairs, target pairs, target answers or few-shot hashes;15 target-user requests are shared. Across all rows there are9 few-shot variants, not one global literal. A source-cohort train/test comparison could therefore be exact core/target-disjoint, but would be confounded by revision/generation cohort and based on only two material pools—not800 independently generated material units. Hash separation never establishes semantic independence or unknown base-pretraining exposure. [Pinned primary card and scorer](https://huggingface.co/datasets/openai/mrcr/blob/f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d/README.md).

## Short-candidate inventory resolves the full-pool limitation

Content-character length spans15,459–5,244,934; median313,545. Core pairs span2–3013; median170. Answer length spans158–3553 characters. We tokenized every row with at most200,000 message-content characters:329 rows total. Counts below include prompt-content plus answer under `o200k_base`, not chat framing or an actual Qwen budget.

| Candidate limit | Original date | Correction date | Total | Targets appearing in another candidate core |
|---|---:|---:|---:|---:|
| ≤8192 tokens |101|0|101|0|
| ≤16384 tokens |200|1|201|15|
| ≤32768 tokens |297|6|303|70|
| ≤200k characters |321|8|329|91|

Within the101 ≤8192-token candidates, exact core overlap consists of five nontrivial components of sizes3,3,2,2,2 and89 singleton components. None of these101 targets appears in another candidate's core. Thus a prospective32-training/16-heldout short experiment is structurally feasible from the89 singleton components, with common few-shot material explicitly retained. It need not inherit the full800-row target-exposure graph: that graph is overconservative for this restricted input pool. No split was designated by this inventory.

The cross-cohort alternative is much longer: the16th-shortest correction-date conversation has524,324 content characters. We additionally tokenized the eight previously uncounted rows among the16 shortest correction-date records: their maximum prompt-content-plus-answer is108,952 `o200k_base` tokens. A16-case corrected-cohort holdout is therefore not supported by the short≤32k inventory. External-file interrogation could preserve that full context, but external-file size is not neural prompt length and requires a separate runtime design.

## Scorer and artifacts

The reviewed official scorer requires the marker at the RESPONSE START, removes that prefix once from response and answer, then applies `difflib.SequenceMatcher(None,response,answer).ratio()`. It does not strip whitespace, normalize text, or search for the last marker. Only this pure function was extracted and checked; the card's client/download code was not executed. Do not substitute the existing DeepMind MRCR scorer. The pinned card declares MIT; no separate license file was acquired.

`INVENTORY.json` contains all800 component memberships and checks; `ROWS.jsonl` maps ordinal→shard/source-row/full-row and context/target hashes; `CORE_PAIR_INCIDENCE.jsonl` and `TARGET_ANSWER_INCIDENCE.jsonl` preserve exact incidence without raw answers. `SUBSET_INVENTORY.json` contains short-pool memberships, overlap sizes and component↔date cross-tabs. `COHORT_LENGTH_BOUNDS.json` contains per-cohort token counts and the corrected16-row length-only inventory. These are diagnostic candidate pools/order statistics, not selected training/test roles.

Original inventory manifest SHA256: `41b3d306599b930854afe44b825fc3b57a64a0ebc9c3db0a6180e19e25eeb328`. Additive subset and cohort manifests preserve their own source/artifact hashes. Existing DeepMind data, all original Parquet/card files and all live experiment sources are unchanged.
