---
status: cpu_qualified_for_MAIN_review_only
question: Does the cached newer released model use the original Python controller interface more successfully under the same two-turn budget?
acquisition: none_existing_models_data_environment_only
GPU_authority: MAIN_only
---

# Released-model controller screen

Sixteen episodes compare released Qwen3-4B-Instruct-2507 (`cdbee75f17c01a7cc42f958dc650907174af0554`) and released Qwen3.5-4B (`851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`), with no QS6, c32, or other adapter. Use the first eight lexicographically ID-sorted records from the frozen OpenAI MRCR **training** schedule. These are research-exposed contexts, not a new holdout; base pretraining is unknown. Eight paired context units, not sixteen independent observations.

MAIN's approved amendment supersedes the earlier mixed-family proposal: all eight cases are MRCR, and the 1200-second allowance is science time, with separate finite loading/release allowance. The original public JSON bytes, final question, and original root prompt stay unchanged. The root prompt retains its original generic mention of recursive children even though the actual harness disables them in both arms. Gold, target index, ordinal diagnostics and answers are host-only. No host answer program or fallback is supplied.

## Frozen experiment and budgets

Old model first, then new; one resident model at a time. Eight episodes per arm, four concurrent. At most **two ROOT turns per episode**, zero children and 32 physical generation calls overall. An immediate final ends the episode; the spare turn is not spent. One inspection followed by a final is possible, but there is no recovery turn after a poor first inspection.

Temperature .5, top_p 1, top_k -1, min_p 0, nonthinking, 1024 requested output tokens per call. Case seed `202609190000 + sorted_case_index` is shared across arms. Both models use BF16/eager, no LoRA/prefix cache, max 8192 context and four sequences. `VLLM_BATCH_INVARIANT=0` is explicit in both services, following the previously served released-Qwen3.5 recipe; no batch-invariant or bitwise sampling claim. Different templates and cache histories prevent a weight-only or matched-cost causal claim.

Every actual prefix plus 1024 must fit 8192 before transport; an overflow is unavailable, never silently truncated. Original JSON file size is not neural input length. Each episode has an at-most-180-second allowance, each arm at most 600 science seconds (1200 total), owner 1800 and outer 1900 including two sequential loads and authenticated cleanup. Partial outcomes are preserved; all eight cases remain planned even if a cap or launch fails. Unknown/provider failures are unavailable, not wrong. A clean complete inventory is not itself a capability success.

## Templates, scoring and fidelity

The old released Instruct-2507 model uses installed `DefaultRendererConfig(tool_parser='qwen3', reasoning_parser='think', enable_thinking=False)`; its first prefixes equal the official tokenizer template. Generic Qwen3Renderer inserted an extra thinking prefix and was rejected during preparation. Qwen3.5 uses installed Qwen35Renderer with its XML-style tool parser, native stop IDs and tokenizer bounds. No parser/runtime is modified.

The sole consumed prefix inventory is `inputs/PREFIXES_NATIVE.json`, computed from the actual depth-zero system and original ordered tool schema. Earlier `PREFIXES.json` and `PREFIXES_DEPTH0.json` remain immutable preparation diagnostics, not science inputs. The former included a depth-one delegation paragraph; the latter re-rendered a JSON-sorted schema with different token order. Real CPU harness prefixes now match the final saved IDs in both arms. At runtime every first request is checked against them.

Primary exact and unchanged official MRCR score use the **original harness `root_reply`**. The official marker check and `SequenceMatcher` scoring are untouched. Three separate diagnostic strings are retained: generated tokens decoded after removing only native trailing stop IDs, typed native `message.content`, and harness `root_reply`. They are not silently normalized or substituted into the primary score. CPU fixtures show old DefaultRenderer preserves two trailing spaces in native content, Qwen35Renderer strips them, and ACPHarnessSession strips the final text in both arms. This known interface loss is part of the model-package screen, not a model copying error by default.

First action diagnostics check the actual declared `ipython` schema and Python syntax; no generated code is re-executed by the analyzer. The runtime itself uses the original authorized process-isolated Python tool, not a security sandbox. Host diagnostics report matching message roles/indices, target user ordinal and assistant-successor content observed, plus broad dumps and observation bytes/tokens. Finding target content in a broad dump is not proof of deliberate correct selection or faithful reasoning. `unique_target_only` is a stricter descriptive content-observation flag, not an AST proof.

Keep the proposal's exploratory screen: all sixteen outcomes known, at least three net usable-inspection wins without lower final exact count; at least two net final-exact wins is a stronger signal. Show paired outcomes and the stricter unique-target-only diagnostic before interpreting this screen. No automatic best-model selection is implemented. Null results concern this short nonthinking recipe, not the model's longer thinking capability. No claim about learned delegation, useful recursion depth, long-context necessity or independent test transfer follows.

## Evidence and execution

`CPU_EVIDENCE_FINAL.json`: two focused tests passed in 222.80 seconds; complete preparation 228.70 seconds. Each arm used the real cached CPU container, original Python harness, actual native renderer and a fake native HTTP provider prescribing one operator-authored inspection and a synthetic final. Exactly two ROOT responses, no children, exact first-prefix IDs and complete raw wire captures passed. Separate actual service entrypoint checks validated both native configurations, current-driver environment, `bin/inference @ config` launch argv and inherited lifecycle binding, with only process launch/network readiness stubbed. Zero model-weight loads and zero GPU/model queries. These checks do not qualify the new model's tool behavior or current GPU kernels.

READY pins sources, data/host gold, native tokenizer/template files, runtime dependencies, CPU request/response/episode files and each fidelity-string hash. Full model shard hashes were authenticated in the earlier pinned `WEIGHTS.json`; current file size/mtime/inode identities are rechecked. Broad inherited source pins include old research adapters as provenance only: neither service loads one.

From this directory, MAIN first runs:

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py verify
```

MAIN alone supplies its usual existing private key, one visible GPU and shared exclusive lock, then executes the READY `fixed_argv` (`.../bin/python .../owner.py run`) under its 1900-second outer owner. Do not launch directly without MAIN's shared lock. Fixed new output: `outputs/attempt-001`, arms `qwen3` and `qwen35`. Every episode start, native request/response, derived episode, progress checkpoint, service ownership/release and paired result is saved. `OWNER_TERMINAL.json` and `PAIRED.json` preserve partials and the fixed eight-pair denominator.

Admission risks: actual GPU generation for this pair is not yet exercised in the current allocation; model-package parsers differ; two turns may restrict useful inspection; launch/cap failures remain unavailable. Existing sealed owners, data, runtime and model caches are unchanged.
