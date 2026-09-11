---
title: Fresh-context positional anchors restore late MNLI batch correspondence
date: 2026-09-10
status: complete_native_audit
study: leaf-mnli-positional-anchor-new-context-v1
---

# Question and result

On sixteen inventory-excluded MNLI contexts, does explicitly numbering input records interact
with emitting the same row number before each label, especially at positions 17–48?

Yes, strongly in this exploratory panel. The prospectively primary late-position interaction
was +657 correct labels out of 1,536 paired label opportunities, or **+42.77 percentage
points**. Every one of 16 context-level interaction contrasts was positive. All 192 calls
were natively authenticated and contract-valid, so there was no availability loss. The
frozen promotion gate (>=10 points, positive in >=12/16 contexts, no availability loss)
passed.

# What changed

Late-position row-first minus labels-only gains with input rows present were:

- wrong visible references: +235/512 (+45.90 points);
- unrelated alien references: +242/512 (+47.27 points);
- aligned references: +237/512 (+46.29 points).

Pooled across relations, present-input row-first gained +714/1,536 late labels (+46.48
points). With input rows absent, row-first gained only +57/1,536 (+3.71 points). Their
difference is the +42.77-point primary interaction.

The pattern was not confined to misleading IDs: the three present-row gains were nearly the
same across wrong, alien, and aligned reference conditions. This supports positional
correspondence as the immediate mechanism to pursue more than relief from a particular
wrong-record semantic association. It does not prove a latent binding mechanism: adding an
input field and changing the output schema form a package.

The original output-only question remains secondary. At input-row absent, the row-first
late gain was +57/1,536 (+3.71 points), positive in 13/16 contexts. Per the frozen method,
this fresh study does not move the earlier output-only gate.

# Cell results

Each cell has 16 calls and 768 labels; early and late each contain 384 labels.

| Relation | Input row | Output | Total | Early | Late |
|---|---|---|---:|---:|---:|
| wrong | absent | labels only | 395 | 201 | 194 |
| wrong | absent | row first | 379 | 183 | 196 |
| wrong | present | labels only | 414 | 200 | 214 |
| wrong | present | row first | 667 | 218 | 449 |
| alien | absent | labels only | 385 | 197 | 188 |
| alien | absent | row first | 409 | 184 | 225 |
| alien | present | labels only | 402 | 198 | 204 |
| alien | present | row first | 665 | 219 | 446 |
| aligned | absent | labels only | 385 | 190 | 195 |
| aligned | absent | row first | 401 | 188 | 213 |
| aligned | present | labels only | 409 | 201 | 208 |
| aligned | present | row first | 664 | 219 | 445 |

# Native and cost audit

The reader reconciled every frozen coordinate with its exact ordered request bytes, body
hash, expected native prompt IDs, model, unique choice, completion IDs, tokenizer-rendered
message, finish branch, and recorded score. The physical union contains 192 REQUEST, 192
RESPONSE, and 192 RESULT artifacts; all responses were HTTP 200, choice-bearing, authenticated
native `stop` completions. There were 0 NULLs and all twelve cells were 16/16 available and
16/16 contract-valid. Usage was 758,868 input tokens, 63,008 output tokens, and 0 cached
tokens, with no unknown usage fields.

The owner completed and released cleanly in 434.457 seconds. Its parent exited 0 without
timeout in 437.266 seconds and reported no GPU processes after exit.

# Interpretation and next comparison

The practical next step is a fresh-context use test that keeps record numbering and the
row-first output contract but asks a downstream root/controller to consume the resulting map.
This result establishes leaf-level late-position correspondence, not root-level usefulness,
general MNLI accuracy, or independence from the exact row-number wording. A later permutation
control should distinguish ordinal values from stable one-to-one position anchors; it was
correctly excluded from this replication.

The sixteen contexts are correlated batch units and were excluded only from named prior
inventories, not claimed globally or pretraining unseen. One paired seed per context limits
sampling-generalization claims. The author also authored the producer and prospective reader;
the method predates output inspection but is not an independent analysis.

# Evidence

- Native audit: `AUDIT.json`, SHA-256
  `09bd2921c9100491012bb3198235b6473273635dfd1c880e97713c3488c1ace9`.
- Frozen method: `METHOD.md`, SHA-256
  `90a6c56d70722f3f65f57e9232bb3fcf49256013aa51622b98cbe51bc693e4d9`.
- Producer READY: SHA-256
  `5ae8a97ce267b6f8918ea01562d162cde596cd38aea113a1e7b531fdb0a29db6`.
- Owner terminal: SHA-256
  `ed26e44e8dff2c2e0f020ac05703727af479125c38b704c727b2632f50add393`.
- Parent EXIT: SHA-256
  `b3fd7d5a58cabd245d1e3c5fd58d07f3dfd775c46eeaf3f44ec6f0ca01a68bbb`.
