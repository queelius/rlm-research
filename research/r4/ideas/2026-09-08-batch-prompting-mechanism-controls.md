# Batch-prompting controls for the observed batch64 collapse

2026-09-08 UTC. Bounded primary-source check; recommendations only. No GPU calls, curriculum edits or frozen-audit changes.

## Decision

Run indexed correspondence first, position balancing second, adaptive granularity third. The [sealed local audit](../analyses/leaf-batch-shape-2026-09-08/REPORT.md) already separates singleton cardinality repair from batch64 semantic failure: selected schema64 is valid in 24/24 coordinates but only 698/1,536 labels correct; first/last-quarter accuracy is 374/384 versus 81/384. All actual inputs contain the complete 64 questions. Do not explain this away as input truncation or claim batch-size/position sensitivity as new.

## What the four papers actually establish

| Primary work and inspected revision | Method, relevant evidence and boundary |
|---|---|
| [Batch Prompting](https://aclanthology.org/2023.emnlp-industry.74/), Cheng–Kasai–Yu; EMNLP Industry, December 2023. Associated [arXiv v2](https://arxiv.org/abs/2301.08721v2), 2023-10-24. | Groups demonstrations and queries into batches; explicitly marks inputs and responses with position identifiers to preserve correspondence. Studies batch size, task difficulty and similarity/diversity grouping; reports up to fivefold savings at size six. Indexed batching is already established. Most headline experiments use small batches and API-era overhead: neither cost scaling nor correspondence reliability is established for our 4B, 64-label, cached local service. See §2.2 and §4 of the [proceedings PDF](https://aclanthology.org/2023.emnlp-industry.74.pdf). |
| [BatchPrompt](https://arxiv.org/html/2309.00384v3), Lin et al.; ICLR 2024, v3 dated 2024-07-15 (first submission 2023-09-01). | BPE permutes the same inputs and votes; SEAS removes examples after consecutive matching, confident answers, shrinking later batches rather than refilling them. Its position study rotates records through every position. It also warns that voting can accumulate wrong answers when the starting model is weak. Published token savings exclude generated output tokens; experiments use few-shot GPT-3.5/GPT-4 at temperature zero, unlike ours. Position-aware ensembling and confidence-based shrinking are not new. [Official ICLR record](https://openreview.net/forum?id=Agyicd577r). |
| [Auto-Demo Prompting](https://arxiv.org/html/2410.01724v1), Feng–Hong–Zhang; v1, 2024-10-02. | The operative change is to repeat each input question before producing its answer, so earlier generated question–answer pairs enter later decoder context. Optional embedding retrieval groups similar questions. Evaluates GPT-4o/mini, temperature zero, primarily sizes 8–32; no native 4B training or size64 guarantee. This is more than printing an index. Copying may help correspondence or worsen long-output repetition; its in-context-demonstration interpretation does not establish the mechanism in our model. See §2 and Appendix A. |
| [Cascaded Batch Prompting](https://arxiv.org/html/2608.27038v1), Hoshino–Zhang; v1, 2026-08-27; marked EMNLP 2026 Findings. | Stage 1 generates short class names; stage 2 maps them to symbols. Crucially, the [PDF limitations/appendix](https://arxiv.org/pdf/2608.27038v1) specify N/b batched first-stage calls plus N individual second-stage calls, which also see the original question/options. This is not two batched calls or pure deterministic reformatting. Cardinality checking is orthogonal; its reported size128 repair is small/non-significant. GPT-4.1 MNLI does not improve over conventional batching. Our outputs already use semantic class names, so applicability is weaker than the abstract suggests. |

Our 1,321–1,361-token inputs also do not establish the papers’ broad long-context explanations for our failure. Validity, source correspondence, class semantics and final count must remain separate endpoints. A correct count can hide cancelling classification errors.

## Official implementation readiness

The [xlang implementation](https://github.com/xlang-ai/batch-prompting/tree/5e7d55c5781953ad72e0faeb0146fe15628cf9e0), commit 5e7d55c5781953ad72e0faeb0146fe15628cf9e0 (2023-10-24), confirms indexed input construction and an initial answer prefix. Its legacy [extractor](https://github.com/xlang-ai/batch-prompting/blob/5e7d55c5781953ad72e0faeb0146fe15628cf9e0/humanprompt/components/extract/extract_regex_batch.py) strips prefixes, lowercases and inserts empty placeholders; it is not our strict ID-bijection/JSON contract and should not be transplanted. No repository-wide LICENSE was found in the complete pinned tree; inspect rather than assume reuse permission.

The [Microsoft implementation](https://github.com/microsoft/BatchPrompt/tree/ac3c354803c7f202f5a8366c909ca6b4e41f32f1), MIT, commit ac3c354803c7f202f5a8366c909ca6b4e41f32f1 (2024-05-02), predates paper v3. In [adaptive_batch_run.py](https://github.com/microsoft/BatchPrompt/blob/ac3c354803c7f202f5a8366c909ca6b4e41f32f1/adaptive_batch_run.py#L151), the active stopping condition checks two equal answer entries; the stronger confidence-condition line is commented out. Do not call this an exact SEAS reproduction without resolving that difference. Neither legacy runner is a ready native-harness baseline. No official Auto-Demo/Cascaded implementation was identified in the inspected papers and bounded search; this is not proof none exists.

## Three smallest falsifiable comparisons

All proposals use ONE warm 4B service on ONE A100 40GB, four concurrent calls, complete per-call checkpoints/costs, no root LLM. Freeze one exact adapter before outcomes. Use the first 256 questions in the existing clean 300-question validation manifest, without consulting labels to choose/order them: four source-order groups of 64, two fresh paired seeds. This is exploratory reused validation, not a new test set. Keep source-test results report-only. Proposed seeds 981261401/981261402 require collision checking when a future specification is frozen.

### 1. Indexed correspondence versus question echo — 24 calls, estimated 2–4 minutes; five-minute cap

Three arms: current anonymous question/label arrays; explicit input IDs with an output ID→canonical-label map; the same indexed mapping plus a generated verbatim question copy before each label. The last is the Auto-Demo-inspired arm. Use exact-cardinality/enum contracts throughout and strict duplicate/missing-ID checks, never guessed positional repair. Score question-copy fidelity separately.

Give all three fresh arms the same 3,072-output-token allowance and check actual input-plus-cap lengths on CPU; do not compare the longer representation against a reused 1,024-cap baseline. Retain definitions, sampling and question order. This tests the representation package, not input indexing alone.

Promote an indexed/echo arm if late-half canonical accuracy improves at least 10 percentage points with no more than two-point early-half loss and no coverage loss; thresholds are exploratory decisions, not significance claims. If only echo helps, compare its extra output cost before adopting it. Retire a semantic claim if gains are solely validity, or copied questions are correct while associated labels still collapse.

### 2. Balanced position relocation, without voting — 32 calls, estimated 1–3 minutes; five-minute cap

Reuse the anonymous exact-length label contract at 1,024 output tokens. Apply cyclic offsets 0/16/32/48 to each 64-question document under each seed, then invert the known permutation on the host. Every question visits each quarter; retain both question identity and output position. No ensemble is needed to answer the causal diagnostic.

Promote position/reset remedies if the same questions improve when moved early and degrade when moved late across documents/seeds. If errors instead track question identity with little relocation effect, retire a predominantly positional explanation. This deliberately reproduces a known BatchPrompt diagnostic in our specific trained/schema-controlled regime. Majority voting is deferred: correlated entity collapse could survive permutation and become confidently wrong.

### 3. Fixed size16 versus explicit adaptive recomputation — at most 80 calls, estimated 3–6 minutes; ten-minute cap

Compare four fixed 16-item calls per document/seed against: one 64-item call, one five-item audit call on predeclared positions 1/17/33/49/64, then four 16-item calls only if any audited labels disagree or the large output violates contract. In that branch replace the entire large-batch result. This is an explicitly measured experimental policy, not a silent retry or modification to the existing runtime. Use 1,024 output tokens for size64 and 256 for sizes5/16.

This rule uses no gold or model self-confidence, but agreement can still be jointly wrong. Measure missed semantic failures, trigger frequency, all-call input/output costs and host-derived count accuracy. Promote only if it matches fixed16 semantic accuracy within one percentage point and availability while reducing logical input at least 20%, without offsetting completion/wall-cost growth. If nearly every document triggers, prefer fixed16: adaptivity adds cost without useful selectivity. This is especially decision-relevant after the already approved mixed-size curricula, whose frozen recipes remain untouched.

## Scope and provenance

The brainstorming skill kept the recommendations at design-only comparisons, separating established methods from the local mechanism test. These are not runnable jobs and do not authorize replacing queued experiments.

Retrieved 13 small primary artifacts totaling 3,081,930 bytes on 2026-09-08. [Source manifest](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/2026-09-08-literature/batch-prompting-T1g47Z/SOURCES.json") records exact URLs, revisions, licenses, byte counts and SHA-256 checksums. Paper licenses: ACL CC BY 4.0; BatchPrompt/Cascaded CC BY-NC-ND 4.0; Auto-Demo arXiv perpetual non-exclusive license. No external code was executed or dependencies installed. OpenReview presented a browser challenge; the versioned arXiv paper, indexed primary conference PDF and official repository supplied the substantive evidence.

