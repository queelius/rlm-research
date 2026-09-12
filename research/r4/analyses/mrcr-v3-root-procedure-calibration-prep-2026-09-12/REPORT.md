---
title: MRCRv2 root-procedure calibration preparation
date: 2026-09-12
status: frozen-inputs-proposed-not-ready
gpu_launched: false
dataset: mrcr_v2p1_2needle_in_(32768,65536)_dynamic_fewshot_text_style_fast.csv
dataset_sha256: db030da739e427139541debbab7cfee591690942d9a69a6973d7c71395f2ab00
official_source_commit: d5637d5cfb420a040ad550b2125c6aa23f71f9e4
---

# Outcome

The smallest official 32--64K two-needle MRCRv2 object is frozen in the external
cache, its current GCS generation and bytes were reverified, and the current official
parser/scorer source is pinned in a sparse checkout. No data or GPU job was launched:
the exact 37,975,202-byte object was already cached, and the pre-existing 1.52 GB tier
was neither read nor modified.

The most important sampling limitation is that all 121 rows are target-query variants
over **one underlying long context**. The eight frozen rows therefore cover target
ordinal and needle-position strata within one context; they are not eight independent
contexts and cannot establish dataset generalization.

# Frozen sources and inspection

- Data: 121 rows, all two-needle, `context_len` 65,267--65,274; SHA-256
  `db030d...ab00`; GCS generation `1752091032747413`; Apache-2.0.
- Official source: `google-deepmind/eval_hub` commit `d5637d5...f9e4`.
  `run_evaluation.py` and `analysis_utils.py` were inspected completely. They are
  unchanged from the older cached `67b7fd...` version for these files.
- Every row parsed with `solve_mrcr_example`; the derived answer equalled the CSV
  answer, there were exactly two distinct needles, and the final query was present.
- The deterministic eight-row selector takes one row from each
  answer-position-quartile × requested-ordinal cell. It freezes full-row, prompt,
  answer, and view-operation hashes without duplicating 2.5 MB of source text.

The official scorer has a noteworthy implementation/documentation discrepancy. Its
docstring says the 12-character hash must start the stripped prediction, but the code
uses `prediction.rfind(random_hash)` and scores the text after the last occurrence.
The official implementation must remain the reward. A diagnostic should separately
record strict prefix-at-position-zero, hash absent/present, and content similarity so
format and retrieval-content failures are not conflated.

# Proposed calibration (not implemented or launched)

Question: can the unadapted cached Qwen3-4B root discover a reliable procedure for
selecting and copying the requested MRCR item from externally accessible context, and
do four samples per target yield useful within-target reward variation?

Use the cached no-adapter 4B checkpoint and the existing authenticated root runtime.
Give the root the ordinary MRCR instruction while placing the full `queries` string in
the existing external-context variable; do not pre-extract needles or reveal host
parser fields. Freeze the eight rows in `CALIBRATION_ROWS.json` and use the same four
seeds for every row: `202609121401`--`202609121404`. Allow the existing six root
iterations and 2,048 generated tokens per root turn. Preserve every native root call,
REPL observation, final response, timeout, and child call rather than silently
normalizing failures. The child/root checkpoint is the same unadapted cached 4B model;
no learned adapter is involved.

Host metrics per rollout:

1. exact official `mrcr_v2_metric` score in [0,1], using the pinned implementation;
2. exact score 1.0, hash presence, strict hash prefix, and conditional content ratio;
3. availability, finish reason, root calls/tokens/time, Python/tool calls, and child
   calls/tokens;
4. inert trace evidence of whether the root actually inspected external context
   (successful string indexing/search/splitting and returned observations), without
   executing generated code again during analysis.

The primary calibration signal is the number of eight four-rollout groups containing
at least two distinct official scores (tolerance `1e-12`), plus per-group score range.
Report continuous rewards rather than converting every partial match to binary. A
useful result is mixed reward with authenticated external-context inspection; uniformly
zero/unavailable indicates a harness/prompt/procedure failure, while uniformly high
scores make this slice too easy for RL calibration. This is a calibration run only;
there is no optimizer, checkpoint selection, or train/eval claim.

# Root-only update evidence boundary

The existing trajectory path is sufficient **in principle** to qualify a later
root-only update without a new trace framework:

- physical `WireTrace` nodes preserve exact token IDs, compact chosen-token processed
  logprobs, sampled/unsampled role, and per-token masks;
- native call records preserve model identity, sampling parameters, finish reason,
  usage, and sampled-node binding;
- the audited causal exporter reconstructs each causal prefix from graph nodes, checks
  prompt/completion usage equality, and emits `input_ids`, labels, binary `loss_mask`,
  and `old_logprobs`; unsampled prompts, REPL observations, and child replies are
  masked while the current root action is the sampled suffix.

An inspected real episode had four authenticated calls; its first sampled root node had
124 token IDs, a 121-token sampled suffix, and 121 compact logprobs matching the native
121 completion-token usage. The provider-level `sampling_mask` is disabled/null for
unconstrained root generation, but that is not itself a blocker: the graph exporter
derives the root action mask from exact sampled-node boundaries. A future trainer must
still qualify all 32 new episodes with the existing strict invariants: one-to-one
sampled nodes and calls, positive-temperature full-support sampling, exact usage
lengths, finite processed logprobs, and root-only credit. Any root/child endpoint alias
collision or missing node capture must make that rollout non-trainable rather than be
filled in.

This does **not** yet make a root update ready. No MRCR trajectory exists, no fresh
mixed-reward group has been observed, and no HF replay/probability agreement has been
checked for these 65K external-context prefixes.

# Interpretation ceiling and decision

The official MRCR documentation explicitly warns that code access makes the task much
simpler. This pilot tests learned use of an external-context inspection procedure and a
clear verifier, not semantic recursion, natural long-context retrieval, or parity with
tool-free MRCR results. Because all selected rows share one corpus, success also does
not show context generalization.

Only if the calibration produces authenticated mixed groups should a separate proposal
specify a root-only update and the previously estimated roughly 39-minute training
budget. If rewards are uniform, first change rows/context or root procedure exposure;
do not spend that budget on an uninformative update.

# Artifacts

- `SOURCE_MANIFEST.json`: object/source pins, row validation, and acquisition scope.
- `CALIBRATION_ROWS.json`: deterministic selection rule, hashes, strata, and seeds.
- External freeze manifest:
  `/project/alex_phd/research-cache/datasets/mrcr_v2/mrcr_v2p1_2needle_32768_65536_FREEZE_20260912.json`.
- Sparse inspected official source:
  `/project/alex_phd/research-cache/repos/eval_hub-mrcr-source-d5637d5`.

