# Qwen3 versus Qwen3.5 identity comparison: CPU-ready

The approved 144-call design is implemented in [leaf-qwen35-identity-v1](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-qwen35-identity-v1/READY.json"). No GPU/model calls, weight loading, installs, service actions or historical-source edits occurred. READY was the final publication inside the source/input closure.

Exact experiment: 12 already-exposed sparse-source64 contexts (four TREC, four SST-2, four AG News), two fresh seeds, three full64 outputs (plain labels, matching-source tag objects, constant-tag objects), two released instruction/post-trained checkpoints without our adapters. Both models receive identical request bodies except model alias; physical templates/token IDs are explicitly model-specific. Explicit non-thinking, exact grammar in every arm. This is a component representation comparison, not a pretrained-base, no-grammar or end-to-end RLM claim.

## Evidence and immutable identities

- READY SHA `c62c85a4bd18fc81086c6f6883f7a608083175401b0fcf597643ba736d4ee979`.
- SPEC SHA `6d54cdea8a9698cca8d9dc72e9eb8684a20521d1c0c0d92b0b49c806177a5f64`.
- CPU qualification SHA `2a78184715e2f617cf99f5eabc18d6945a9e971cf2b99a173defb70fd8d745dc`: all144 typed/rendered requests, 18 distinct schemas per tokenizer, 162 negative grammar fixtures. Maximum complete input plus3072 output is7894, below8192; no input crop.
- Five focused tests pass (9.58s in final prepare). Four initial tests captured missing-implementation assertion failures. One two-record test fixture was corrected to match its actual64-record scoring context. The added actual-tokenizer/mock-HTTP test verifies valid/invalid/null records and ordered wire checkpointing. Two installed SWIG deprecation warnings are recorded, not hidden.
- A fresh separate `CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 .../prime-rl-5990b1b/bin/python owned.py --verify` exited0 after READY publication, confirming source closure, authenticated shard stat identities and the private base-lifecycle seam without model calls.
- All five cached full weight-shard SHA256 values were freshly computed once and exactly match the pinned cache manifests. [WEIGHTS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-qwen35-identity-v1/WEIGHTS.json"), SHA `c56952ceb2b5bcf5a25f30198022188d3166edbf23117f66f5ad8458db309794`, records them and immutable file size/mtime/inode identities. Runtime validates these identities rather than hashing gigabytes per call. Cache model/source/license metadata was also authenticated; public dataset exposure/license caveats remain inherited from the frozen sparse source closure.

Source SHA256: study `1fe4af21eb476520f93f1732cbb1075d44650761ae65f9c7b4e980415ccf680d`; driver `ea5d97df9746cacedcf4820f95925bca88685bb8710ac6243b98136a412fc689`; service configuration `ba11de5f818cb3d44be99a8054b5b36793cb36fde8912918ae3a688cf62b1db8`; source/serve `5d6aab04e29f4f5dd486fbecc03116c81940fb55d615d7462085a8ff9a8164f0`; owned `dd2325f034128371d7f719a5cbffd0533629c171acf6189bac64ce29c4fcba78`; preparation `3a5623b77e2d60bc042583f6ab2cce1f57d33dd04a5a8b649f119c1551b349aa`.

## Narrow serving and scoring changes

The new base-service launcher uses the pinned Prime configuration/environment helper. It loads no LoRA, writes an honest base-checkpoint descriptor with adapter=null, and requires `/models` to expose only the bound alias with the exact checkpoint root and no adapter parent. Config is common BF16/eager/no-prefix-cache/no research FP32-head patch/no speculative decoding; Qwen3.5 alone uses language-model-only and hybrid align. Every request supplies the approved sampling defaults and enable_thinking=false. The renderer now passes those template kwargs; the inherited helper alone would not have done so.

The qualified sparse/identity collector is reused unchanged. Strict labels are position-scored without repair. Key-set/tag/label validity is primary, tag-before-label lexical order separately recorded (grammar requires it). Completed-invalid output scores0; infrastructure/unrun remains null. Actual provider prompt IDs and input usage must agree with the correct model's frozen render. Unexpected returned reasoning marks the stage unqualified. Raw response, returned output IDs, usage/cache nulls, actual call timing and schema-bearing ordered HTTP bytes are retained.

Lifecycle is the existing suite/V2 ownership path, including PRL::Inference titles and the observed process-exit repair. Only private `c.ROLE`/`SERVE` references and base preflight are changed, so the existing owner check authenticates this new launcher's exact path/SHA rather than pretending it is the old LoRA launcher. Some inherited diagnostic text still says dual-LoRA/suite; actual binding/config/descriptor explicitly say no adapters. No new scheduler, broad cleanup or unauthenticated service stop was added.

## Launch and limitations

Parent-only exact argv is in READY: native Prime Python → `owned.py --directory .../leaf-qwen35-identity-v1/owned/attempt-001`. Use inherited actual MIG UUID/LD/API environment and established parent lock, never CUDA0. Per-model72 calls, four workers,120s/request,300s startup and900s collection;2400s work,2640s owned inclusive,2670s outer. Model order is Qwen3 then Qwen3.5. Any stage failure preserves evidence, releases its authenticated service and stops; no retry or fallback. Outputs: `outputs/qwen3`, `outputs/qwen35`; owned terminal `owned/attempt-001/TERMINAL.json`.

Actual Qwen3.5 A100 kernels/startup are still unqualified. CPU config/tokenizer/grammar success is not an observed speed or semantic-performance claim. Sequential service stage, eager execution, disabled cache and model-specific tokenization limit a speed comparison to this exact component setup. The inherited collector's model_called flag indicates a dispatch attempt, not proof of provider sampling. Small built-in summaries run before release; independent analysis belongs afterward. Source/data/master seed exclusions are the declared named-plan scan, not a global collision proof.

Preparation used executing-plans and test-driven-development skills within the explicitly approved additive namespace. Main owns source review, acceptance and any GPU launch.
