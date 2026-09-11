---
schema: lambda-rlm-supplied-plan-comparator-note-v1
status: source-grounded-proposal-not-launched
reviewed_utc: 2026-09-10
upstream_commit: 3874d393483dc4299101918cf8e9af670194bd88
gpu_calls: 0
proposed_gpu: one_A100
proposed_cap_seconds: 1800
source_sha256:
  rlm/lambda_rlm.py: 3f0e0521f92e1e124e76aa4f717a7bf29c95386ff42b3faf6057d4fa320f42e6
  benchmarks/benchmark.py: 903d8f42a5d6ab512cdc126db54429aee278021841ef07b9e9732afcb034727a
  README.md: cca28d42cf3388d0cb4233091747cae38df6c63921f8d14132752abd1033268d
  LICENSE: 7d637c22fb87aac12be94166542faa688764068b19d5825af900b9bde9abbf10
---

# What the official lambda-RLM code can—and cannot—test for our adaptive root

## Decision

The useful next comparison is a transparent **supplied exact-plan ceiling**, not a claim that
lambda-RLM learned adaptive decomposition. On our conditional-weight J1 task, the official task menu
has no matching reducer. Adding the correct J1 reducer is legitimate only if it is labeled as an
experimenter-supplied algorithm that consumes predicted child labels; it cannot be credited to the
model.

This sharpens, rather than repeats, the earlier runtime note: it specifies which parts of the official
implementation make the comparison non-equivalent and a small comparator that preserves our leaf
information boundary.

## Concrete implementation facts and limitations

1. **The learned choice is a seven-way menu selection, not a generated plan.** One model call sees
   input length, at most 100 query characters, and a 150-character prefix preview, then returns a
   digit for summarization/QA/translation/classification/extraction/analysis/general
   ([`lambda_rlm.py`, task menu](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/repos/lambda-RLM/rlm/lambda_rlm.py:131")).
   The selected type indexes fixed plan and composition tables. Thus a result from this arm estimates
   task-menu routing plus a supplied library, not question-conditioned discovery of record batching,
   state retention, or the J1 reduction.

2. **Branching and depth are fixed functions of character length and assumed accuracies.** The planner
   uses fixed composition costs, `a_leaf`, `a_compose`, an accuracy target, and a branching cap of 20;
   it does not observe actual child errors or map completeness
   ([`lambda_rlm.py`, planner](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/repos/lambda-RLM/rlm/lambda_rlm.py:346")). Our
   scale task is naturally measured in complete records and returned IDs, so character-optimal chunks
   need not be record-complete or operator-sufficient.

3. **The generic reducers do not implement J1.** Classification takes a majority vote over whole
   child strings; QA filters phrases such as “not found” and asks another model to synthesize partial
   answers; extraction deduplicates lines
   ([`lambda_rlm.py`, reducers](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/repos/lambda-RLM/rlm/lambda_rlm.py:463")). None
   computes “identify users with at least one target label, then sum weights of all target-B records
   for those users.” Calling the official classification or QA reducer a fair J1 comparator would
   conflate a known operator mismatch with planning quality.

4. **Execution cannot adapt after seeing evidence.** The emitted executor recursively performs
   `_Split → optional FilterRelevant → map all retained chunks → _Reduce`; there is no completeness
   check, targeted retry, changed batch size, or alternate reducer based on returned child labels
   ([`lambda_rlm.py`, executor](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/repos/lambda-RLM/rlm/lambda_rlm.py:563")). That is
   the controlled contrast we want against our adaptive root, but it is also why this should be called
   supplied-plan execution rather than learned decomposition.

5. **Optional relevance filtering can remove evidence using only chunk prefixes.** QA/extraction
   filtering asks YES/NO from a prefix of each character chunk and restores all chunks only when
   *none* pass; it does not recover individually false-negative chunks
   ([`lambda_rlm.py`, relevance filter](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/repos/lambda-RLM/rlm/lambda_rlm.py:538")). J1
   requires global evidence for both target and target-B labels, so filtering changes the problem
   unless disabled.

6. **The repository benchmark does not establish equivalence on our operator task.** Its names
   `oolong`, `browsecomp`, and fallback `codeqa` map to LongBench-v2 domain filters; S-NIAH has a
   separate loader. Samples are capped at 1.2M characters and evaluated with normalized token-set F1,
   contains, and exact match
   ([`benchmark.py`, metrics and loaders](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/repos/lambda-RLM/benchmarks/benchmark.py:144")).
   Both methods receive the same benchmark prompt and model sampling settings, but normal RLM gets
   depth/iteration limits while lambda-RLM gets a character-window planner
   ([`benchmark.py`, runners](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/repos/lambda-RLM/benchmarks/benchmark.py:717")).
   These mappings are useful implementation evidence, not support for transferring reported wins to
   structured conditional aggregation.

## Smallest legitimate comparator after QS Scale64

Freeze **8 supplied-plan episodes**: the existing four Scale64 clusters × sizes 64 and 256, using the
same c32 child checkpoint, the same public record text/IDs, the same J1 question operands, and paired
fresh seeds fixed before outputs. Use one harness only: the already-qualified cumulative ID-map return
with the 4,096-byte view. This keeps the focused comparison within one A100 and an 1,800-second cap.

The executor is fixed before outcomes:

1. split only at exact record boundaries into fixed batches of 32;
2. issue the *same child classification prompt and available query information* as Scale64;
3. accept only returned `(record_id, predicted_label)` entries and expose missing/duplicate IDs;
4. apply a deterministic public J1 reducer parameterized by `users`, `target`, `target_b`, record
   weights, and **predicted** labels;
5. return `Answer: N` with no root-model repair, reroll, gold label, or gold scalar access.

The deterministic reducer is an explicit supplied task algorithm—an oracle for decomposition and
aggregation structure, **not** an oracle for leaf semantics. It must live outside the root prompt,
must never read `HOST_GOLD`, and its output must be reproducible from the captured child map and public
records alone. Recompute it independently in the audit. Preserve all eight cells, including zero
gold, failures, and incomplete maps.

Primary comparison: supplied-plan strict accuracy versus the matching Scale64 sft6 cumulative cells,
reported at sizes 64 and 256 with cluster as the paired unit. Mechanism outcomes: child-map coverage,
child-label accuracy (audit-only oracle), J1 correctness conditional on the observed child map,
physical child calls/tokens, latency, and the adaptive root's acquisition/retention/reducer fidelity.
Do not treat the no-root supplied arm as compute-matched; report its cost as a ceiling/control.

Promotion rule: proceed to a larger or plan-library study only if the supplied plan materially exceeds
sft6 `faithful_and_strict` on at least 3/4 clusters at one frozen size **and** the gap is attributable
to acquisition/retention/reduction rather than different child information. If supplied-plan and sft6
are tied but both wrong from the same child labels, prioritize leaf quality instead.

## Ranked questions

1. Does the learned adaptive sft6 root close the gap to a transparent exact-plan ceiling as context
   grows from 64 to 256 records?
2. If not, is the gap due to acquisition, retained-map completeness, or execution of the J1 reducer?
3. Only after those are separated: does a broader *supplied* task-menu/combinator library improve
   transfer across operator families? Running the official generic QA/classification reducer directly
   on J1 is lower priority because it answers a task-mismatch question, not adaptive planning.

The cached repository remained clean and unexecuted; no clone, install, active-file edit, or GPU call
was made for this review. License is MIT with third-party notices; this note makes no dataset-license
claim.
