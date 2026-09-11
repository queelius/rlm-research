---
id: mnli-field-order-replication
status: CPU_preparation
question: Does label-first selectively reduce misleading-reference interference on fresh contexts?
created_utc: 2026-09-10T17:35:00Z
---

# Fresh-context output-field-order replication

Select 16 new contexts of 48 records from MultiNLI validation_matched, balanced as four
contexts in each of government, slate, telephone, and travel. Each context contains 16
complete three-label premise groups. Eligibility may use labels to establish the inherited
complete, conflict-free three-label group rule; ranking among eligible groups uses only a
fixed hash of master 989626001, genre, and normalized premise-group identity. Exclude every
premise group named in prepared or executed MNLI DATA, PUBLIC, or GROUPS inventories. If any
genre has fewer than 64 eligible groups, stop and preserve the insufficiency record.

Cross wrong, unrelated, and aligned visible-reference conditions with tag-first and
label-first output order. Keep the prior base Qwen3-4B Instruct2507, native template, no
adapter/tools/thinking/prefix cache, temperature 0.5, top_p 1, max 3072, context 8192,
four workers, 90 seconds per call, and exact whole-output contract. Use one paired seed per
context, 989626101+i, and rotate six-arm dispatch order. There are 96 calls. A single A100
parent cap is 1800 seconds, including startup and cleanup. MAIN alone may launch it.

Primary metric is `(wrong_label_first-wrong_tag_first) -
(aligned_label_first-aligned_tag_first)`, computed first within each context and averaged
over 16 context clusters. Positive means selectively reduced misleading-reference penalty.
Freeze strict accuracy, availability, all paired context effects, and wrong-record versus
displayed-record diagnostics. The practical pilot gate is at least +10 percentage points,
positive in at least 12/16 contexts, without lower misleading-arm label-first availability.
This is an exploratory replication gate, not a significance threshold.

The source is `nyu-mll/multi_nli`, revision
`da70db2af9d09693783c3320c4249840212ee221`, split `validation_matched`, local parquet
SHA-256 `350c26950b55f460b50d36c76aef87d64b49c78812d7abf7bf97e5fede10f186`.
License is mixed OANC permissive terms / CC-BY-3.0 / CC-BY-SA-3.0 / public-domain fiction;
the pinned dataset card and acquisition manifest are authoritative. New means disjoint from
named project inventories, not absent from model pretraining or every unrecorded analysis.

