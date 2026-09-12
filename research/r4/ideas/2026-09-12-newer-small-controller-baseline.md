---
status: proposed_cpu_only
date: 2026-09-12
question: Does a newer small released controller reduce our observed Python/data-access failures under the same short interaction budget?
primary: Qwen/Qwen3.5-4B
fallback: Qwen/Qwen3.5-9B
authorization: no_weight_download_no_environment_change_no_GPU_launch
---

# Try the cached Qwen3.5-4B first

Recommend the released **Qwen3.5-4B**, revision `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, as the first controller baseline. It is a newer, approximately size-matched post-trained family and already cached. Its full two-shard checkpoint is9,319,828,096bytes; the cache includes the vision component even though this experiment is text-only. Both it and the fallback are Apache-2.0. This is not a claim that it is the newest Qwen release overall or already a better RLM controller. [Pinned official model card](https://huggingface.co/Qwen/Qwen3.5-4B/blob/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a/README.md).

Fallback: **Qwen3.5-9B**, revision `c202236235762e1c871ad0ccb60c8ee5ba337b9a`,19,306,310,880bytes across four full-weight shards. It is not cached. This is a capacity escalation if the4B screen remains uninformative, **not** an architecture-compatibility fallback: both use the same hybrid family and chat template. Download and execution require a later MAIN decision; no weights were acquired here. The official HF API supplied exact revisions, file sizes and LFS hashes in the companion JSON. [Pinned official9B model card](https://huggingface.co/Qwen/Qwen3.5-9B/blob/c202236235762e1c871ad0ccb60c8ee5ba337b9a/README.md).

## Compatibility: evidence levels matter

- Actual local evidence is stronger than a support table: the September9 fresh-correspondence run served this exact cached4B through vLLM0.28, BF16, eager,8192context, four sequences, no LoRA/prefix cache, text-only and nonthinking. Its48 responses were valid, but they were classification maps, not controller tool calls. The reviewed report is `analyses/leaf-fresh-correspondence-live-2026-09-09/REPORT.md` (SHA58ae42f0…). The current allocation/driver and root-tool roundtrip still need ordinary qualification; do not transplant the old launcher blindly.
- CPU imports confirm native **Transformers5.6.2/vLLM0.28.0/Torch2.13.0+cu130**; training **Transformers5.15.1/PEFT0.20.0/Torch2.13.0+cu130**. Both HF environments resolve Qwen3.5 config/model classes. The native environment has no PEFT installation, which is not needed for this released-base inference screen. No environment was changed.
- Reuse the already exercised Qwen3.5 configuration: `language_model_only=True`, `mamba_cache_mode='align'`, `reasoning_parser='qwen3'`, `tool_call_parser='qwen3_coder'`. The installed registry supports that parser. The template uses XML-style function/parameter calls, unlike the old Hermes JSON encoding; the root bridge must consume the proper parser. `enable_thinking=False` was actually rendered CPU-side. [Official Qwen deployment/template guidance](https://github.com/QwenLM/Qwen3.5).
- Do **not** reuse old hardcoded token bounds/EOS. This tokenizer has248077entries, EOS `<|im_end|>`248046; text config has padded vocab248320 and `<|endoftext|>`248044. Derive validation from the pinned tokenizer/config and actual native stop contract. A CPU-rendered tool prompt succeeded; no tool output was sampled here.
- Installed vLLM source declares `SupportsLoRA` for the Qwen3.5 causal core, including GDN packed projections. This is source support, not a qualified HF→native adapter roundtrip. PEFT has no `qwen3_5` default-target entry: future training needs explicit language-model projection targets, frozen vision, and a tiny actual gradient/save/reload/serve test. The old Qwen3 trainer is not automatically portable.

The cached4B already demonstrated inference feasibility. The9B full checkpoint is about18GiB before runtime state; text-only short-context inference on40GB is plausible, not measured. Low-rank training with small microbatches, activation checkpointing and a short context is a later feasibility question, especially for hybrid kernels; neither9B peak memory nor either model's LoRA roundtrip is qualified. Do not budget full-parameter Adam training on this allocation.

## Smallest controller screen: at most32 physical calls

Compare released oldQwen3-4B-Instruct-2507 versus released Qwen3.5-4B, no research adapters/children. Eight shared existing, explicitly research-exposed cases: four from the frozen OpenAI-MRCR short pool and four MuSiQue cases (2two-hop,1three-hop,1four-hop). On later acceptance, select by SHA256 of namespace `newer-controller-screen-v1-20260912` plus opaque ID within these strata, never by correctness/failure. Public input files and task wording stay exact; host gold/support/decomposition stay private. This proposal does not yet designate cases.

Each case/model gets at most **two root calls**, each≤1024generated tokens and actual prefix+requested output≤8192. Up to16episodes/32calls/32768generated tokens, temperature.5, top_p1, top_k−1, nonthinking; seed202609190000+case-index shared across model arms. First call may inspect via the existing approved Python executor; second sees its actual observation. Root chooses the operation; no host answer program/retriever or forced correct tool use. An immediate valid final ends the episode without spending the spare call. Preserve protocol-valid unfinished trajectories separately from transport/provider failures and malformed finals. If a required prefix exceeds the bound, mark unavailable rather than truncate data or select a replacement.

Primary diagnostic: usable access to the supplied JSON and relevant paragraph/message **content**, not dictionary keys or a fabricated file. Also report final exact match/unchanged official score, first-step tool errors, actual observation bytes/tokens, broad dumps and all missingness. Score8paired cases, show both four-case families, not16independent outcomes. Human mechanism labels are descriptive and separate from automatic final scores. Native input templates/parsers necessarily differ, so this is a practical released-model+native-interface comparison, not an isolated weight-only intervention.

Provisional total wall cap **1200seconds including both sequential model loads**, four concurrent episodes/model, no overlap of model residency. Prior4B3.5 map calls averaged roughly27generated tokens per summed call-second, not wall throughput; this supports a short screen but does not guarantee full cap completion. Preserve partials and complete per-call raw/token/usage inventories; no hidden retries. No new benchmark suite or runtime framework.

Promote to a fresh, full-horizon controller comparison only if all16episodes have known runtime status and the new model has at least3net usable-inspection wins out of8 without lower final exact count; at least2net final wins is a stronger capability signal. These are exploratory screens, not significance thresholds. A null retires this short nonthinking recipe, not the model at its official much larger thinking budget. A runtime failure is not a zero-capability result and does not automatically trigger9B acquisition. No inference about learning delegation, useful recursive depth, long-context necessity or independent test generalization follows from this diagnostic alone.

Brainstorming was used as a bounded research spike: the recommendation stays a proposal, with no implementation or launch.
