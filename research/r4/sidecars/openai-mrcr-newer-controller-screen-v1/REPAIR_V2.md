---
status: CPU_qualified_additive_repair_MAIN_only_launch
condition: same_screen_hoisted_tokenizer_vocabulary_size
source_READY_sha256: 7c86dbdfa4fe125563cc0e642e7241455fda872469339c5ecb1f63bf46c51b5e
scientific_inputs_changed: false
GPU_calls_in_preparation: 0
---

# Correct the CPU validator, rerun neither model until MAIN admission

The first attempt is **instrumentation-compromised, not a model ranking**. Old Qwen3 supplied all16 requested responses, but all eight run slots timed out. Six second responses were tool calls; two were genuine native final-text responses that did not reach the returned harness final. Every response spent24.7–49.4seconds after raw HTTP receipt in synchronous host processing. This blocks the shared asyncio loop, delays other callbacks and prevents180-second timeouts firing promptly; observed slot durations were286–300seconds. Service zero-request intervals therefore cannot be attributed solely to model capability or tool execution.

The observed cause is in our added token validator: `len(tokenizer)` was evaluated for every prompt/action ID. In this actual pinned tokenizers backend100 size lookups took2.99943seconds; the first recorded882-token validation thus predicts26.45seconds, agreeing with its observed26.81seconds post-wire overhead. This is not a missing model call. MAIN stopped only the authenticated affected collector; the original owner released cleanly and preserved the incomplete945.15-second attempt. The stop receipt is `operations/2026-09-12-newer-controller-validator-stop/STOP_REQUEST.json`.

The sole validation change in `native_capture_v2.py` is to assign `vocab_size = len(tokenizer)` once per response, then run the **same** integer/nonnegative/upper-bound comparisons against that immutable value. EOS, actual model, usage, native-wire, output and prefix limits are unchanged. Full882-token validation is now0.03926seconds. Tokenizers are not mutated during validation; no bounds check is dropped. The original service, lifecycle, native math, templates, parsers, RLM, seeds, fixed sorted8 training inputs,2 ROOT-turn/zero-child caps and1200/1800/1900 science/owner/outer budgets remain unchanged.

All changes are additive: `study_v2.py` selects fresh `outputs/attempt-002` and `READY_V2.json`; `collect_v2.py` substitutes the new validator and READY reference; `owner_v2.py` selects that collector/output and reads the paired result from the new attempt. Old source/results/READY remain intact. Same eight pairs are rerun for **both** released models, never only successful or failed cases. Do not pool V1 timeout outcomes with V2 or infer a rank from the compromised arm.

Four focused tests passed in38.57seconds. They exercise the actual archived native payload; invalid negative/upper-bound/bool IDs; EOS/usage rejection; and the **actual cached CPU harness** receiving two operator-authored tool responses. The latter now ends as the known `model_no_final_within_two_turns` outcome with exactly2 ROOT returns,0children and no hidden third generation/timeout. This covers the failure branch missing from the original tool→final fixtures. No model weights or GPU were used. `CPU_TIMING_V2.json`, `CPU_TESTS_V2.json`, and raw `cpu-v2-001` artifacts are pinned in READY.

MAIN alone may launch native Python `owner_v2.py run` under its existing shared lock and1900-second outer cap after review. Ordinary owner verification is `CUDA_VISIBLE_DEVICES='' .../bin/python owner_v2.py verify`. Preserve the original primary harness score and the three raw/native/harness fidelity diagnostics; this repair does not remove the known text clamps. Actual native end-to-end readiness after repair remains to be measured, and no capability success is implied by these CPU tests.
