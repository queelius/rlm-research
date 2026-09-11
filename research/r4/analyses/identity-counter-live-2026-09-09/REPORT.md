# Identity96: source-linked tags beat an unrelated changing counter

The advantage survived randomized source IDs and two presentation orders. Tags
that referred to the actual source record produced much better record-level labels
than an equally long changing ordinal counter. The ordinal control was worse than
the constant control, not a substitute for meaningful source identity.

This is a leaf correspondence result, **not yet an end-to-end RLM result**. The
ordinal arm's aggregate class counts were much closer to correct than its poor
record-level accuracy might suggest. Receipt72 has its own frozen audit method;
none of its outcomes was read for this report.

## Independently audited result

All96 planned calls completed, all96 outputs passed the strict exact tag/shape/
canonical-label contract, and all96 were semantically alignable. No infrastructure
failures, unrun calls, length stops or tool responses. Each row below contains16
calls ×64 displayed records =1,024 assignments, with repeats nested in four source
contexts, not1,024 independent examples.

| Task | Meaningful source ID | Changing ordinal | Constant tag | Meaningful−ordinal |
|---|---:|---:|---:|---:|
| TREC | 979/1,024 (95.6%) | 287/1,024 (28.0%) | 401/1,024 (39.2%) | +692 labels |
| SST | 960/1,024 (93.8%) | 505/1,024 (49.3%) | 591/1,024 (57.7%) | +455 labels |

The primary meaningful−ordinal contrast was positive in16/16 paired calls for
each task. At the record level it gained697 and lost5 TREC assignments; it gained
478 and lost23 SST assignments. All four source contexts in each task benefited
across both presentations and both sampled seeds.

| Source-context index | Meaningful−ordinal correct assignments /256 |
|---|---:|
| TREC0 | +170 |
| TREC1 | +172 |
| TREC2 | +188 |
| TREC3 | +162 |
| SST4 | +133 |
| SST5 | +101 |
| SST6 | +111 |
| SST7 | +110 |

The secondary ordinal−constant contrast was −114 TREC and −86 SST labels. Ordinal
lost16/16 TREC paired calls; it lost13/16 SST calls and tied3, with no wins.
Meaningful−constant was +578 TREC and +369 SST labels, positive in every paired call.
No episode-level significance claim treats these96 calls as independent contexts.

## Exact aggregate counts are a separate outcome

| Task/arm | Whole64 labels exactly right | Full class-count vector exact | Mean count-vector L1 error |
|---|---:|---:|---:|
| TREC meaningful | 2/16 | 2/16 | 3.75 |
| TREC ordinal | 0/16 | 0/16 | 10.625 |
| TREC constant | 0/16 | 0/16 | 59.25 |
| SST meaningful | 0/16 | 6/16 | 1.75 |
| SST ordinal | 0/16 | 2/16 | 3.625 |
| SST constant | 0/16 | 0/16 | 32.375 |

L1 sums the absolute errors in each canonical class count for one call; it is not
record-level label error. Ordinal therefore had **worse record assignment but
better class-count distributions than constant** in both tasks. Errors can cancel
when aggregating labels. Do not translate the large record-level correspondence
gain into an equally large exact-count or end-to-end gain. The separate receipt
experiment evaluates actual final task success rather than assuming that transfer.

Positionally, meaningful stayed strong throughout the displayed batch. TREC
quartile correct counts were243,248,247,241 out of256, versus125,54,65,43 for
ordinal and218,69,55,59 for constant. SST meaningful was236,242,244,238;
ordinal147,123,117,118; constant211,127,127,126. These are descriptive output
patterns, not evidence of a particular internal attention or sorting mechanism.

## Actual compute, not just equal standalone tags

| Task/arm | Actual input tokens | Actual output tokens |
|---|---:|---:|
| TREC meaningful | 29,684 | 17,572 |
| TREC ordinal | 30,068 | 17,457 |
| TREC constant | 29,908 | 16,973 |
| SST meaningful | 43,540 | 16,432 |
| SST ordinal | 43,924 | 16,432 |
| SST constant | 43,764 | 16,433 |

Meaningful−ordinal output cost was only+115 tokens total on TREC (about0.66%) and
exactly0 on SST. Meaningful used384 fewer input tokens per task. q/p standalone
prefix/tag token lengths were qualified equal, but full instructions, grammar
constants and token identities differ; equal tag length is not equal realized
compute. Reported token IDs/usage were checked against the actual responses.

Total:220,888 input tokens,144,560 cached and76,328 uncached;101,299 output tokens.
Collection took307.553s; owned wrapper355.860s; outer operation356.431s, exit0,
not timed out. Owned release completed and operation EXIT recorded an empty GPU
process list. Per-call elapsed sums are not substituted for these elapsed times.

## Integrity and independent reconstruction

The method was frozen at06:46:26UTC before this analyst read any outcome, six
seconds before the operation completed. Audit execution was terminal-gated on
STATUS, owned FINISH and operation EXIT. The only reused component was pinned
prior raw-audit plumbing plus its independent JSON parser; saved study scores
were cross-check targets, not the basis of the new readout.

- Reconstructed label-independent source-ID bijections and both presentation
  permutations for all8 contexts from parent padding source records/master seed.
  Source question text, group IDs and gold labels were preserved. Rebuilt all96
  coordinates, sampled seeds and displayed source-label associations.
- Checked all96 exact array schemas and position-specific meaningful/ordinal/
  constant tags, full canonical enums, required fields and forbidden extras.
- Confirmed all32 triples share byte-identical ID-bearing input blocks, system
  messages, tools and all non-message/non-schema request fields. Full prompts and
  schemas are intentionally not identical across arms.
- All96 saved request bodies exactly matched wire UTF-8 bytes/hashes; actual aliases
  and sampling matched. All96 actual full prompt-token-ID arrays equaled their
  frozen arrays, usage lengths agreed, and no context truncation was concealed.
- Independently strict-parsed all96 raw responses, rejected duplicate keys and
  malformed JSON in focused tests, aligned semantics to actual displayed source
  records rather than source-ID rank, and recomputed every label/count score.
  All96 agreed with the frozen scorer and saved scores. Published six cell summaries
  and coordinate summaries also matched the reconstruction.
- Every one of6,144 emitted objects had lexical order `tag,label`. This observation
  is separate from valid field sets and does not certify semantic correctness.
- Three focused tests passed after their expected missing-implementation failures.
  Distinct input/source files were hashed once in the audit inventory (293 fresh
  hashes, two unchanged-stat reuses), without per-call model-closure scans.

No scientific sidecar was edited. No GPU/model/service call, process signal,
environment change or generated-code execution occurred during this audit.

## What this changes

The simple account that “any changing tag supplies enough positional bookkeeping”
does not explain this result. A truthful link to the displayed source record mattered
substantially in this qualified exact-grammar setting. That is consistent with
source-correspondence support, while differing tag prefixes/instructions/grammar
content prevent a pure internal-mechanism claim. A changing ordinal can still help
preserve a label histogram despite failing to assign labels to the correct records.

Keep the already frozen receipt72 comparison unchanged. Its incremental receipt
versus indexed-raw result will address a different question: whether making a helper
result inspectable improves actual final answers. A later component follow-up could
test why ordinal retains counts but loses assignments; that would be a new declared
diagnostic, not a retroactive rescore of these96 calls.

## Artifacts

- [Frozen method](METHOD.md), SHA `6d59a1ab92581377393ebff1627afb24973e0f7c337639745f8ddde0b5606ced`.
- [Audit and paired contrasts](../../../../ARTIFACTS.md#unpublished-files "Not published: AUDIT.json"), SHA `25d057793d4e0442b63a9cf04ac0d41d060a466182777ac4ef96459dc94cf9fd`.
- [Per-coordinate raw reconstruction](../../../../ARTIFACTS.md#unpublished-files "Not published: identity96/METRICS.json"), SHA `080fd7ee684ad374bcd8fa394f8a1d865312a8d9e957ab6260438937e8f2862c`.
- [Source inventory](../../../../ARTIFACTS.md#unpublished-files "Not published: identity96/SOURCES.json"), SHA `dc6ed78bed440904bf9302b90bc30f7b870bb01e2064a080a1000c1579816604`.
- [Audit source](../../../../ARTIFACTS.md#unpublished-files "Not published: audit.py"), SHA `789bd67db08a82a96f0cf839742febcc9fa43ffef1229a5ea24ca9d69a23594b`.
- [Receipt72 method, still pre-outcome](../receipt-ablation-live-2026-09-09/METHOD.md), SHA `cdd289913c488deda4f4c2cdcdcee334bc23b696c81bc35e183622e4a5a40324`.
