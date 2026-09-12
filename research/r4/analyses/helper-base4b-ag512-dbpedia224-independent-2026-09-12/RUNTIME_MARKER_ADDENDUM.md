# Released-base reference: optional-warning gate diagnosis

The run returned **184 valid calls and all 736 labels**, then failed only its final log-marker check. The immutable owner and original independent report still say `complete=false`, `runtime_qualified=false`, and primary accuracy unavailable. This addendum does not rewrite or retrospectively pass that predeclared gate.

The marker was not a mandatory kernel-start message. In the earlier compiled LoRA run it was a Torch Dynamo warning about tracing an `lru_cache`-wrapped function at `batch_invariant.py:141`, followed by a `matmul_persistent` stack frame. The released-base log explicitly records eager execution with Torch compilation and CUDA graphs disabled. The installed `matmul_persistent` source has no unconditional logger. Warm Triton caches can also avoid JIT warnings, but a cache-hit hypothesis is unnecessary to explain the absent **Dynamo** warning. Absence of that warning does not establish that batch invariance was off.

The exact launcher pre-exec receipt authenticates `VLLM_BATCH_INVARIANT=1`, PID, command and wrapper hashes. The inspected local multiprocessing path inherits the environment; worker initialization calls `init_batch_invariance`, and unquantized CUDA linear dispatch checks the flag and selects `linear_batch_invariant`. A focused CPU regression executes both actual source bodies with flag-on/off sentinels. This verifies control flow, not historical device execution. The installed vLLM source files are post-run hash-pinned here, **not part of the original READY closure**. No actual in-worker state or first-kernel-dispatch receipt was collected, and the prior compiled LoRA repeatability probe does not prove eager no-LoRA bitwise invariance.

The material conclusion is therefore source-and-environment-supported activation with an unsuitable logging requirement—not independently observed device dispatch. The complete saved response inventory is useful as an **additive exploratory released-base reference with this explicit qualification deviation**, subject to MAIN acceptance. There is no need for another GPU repetition merely to elicit a warning.

| Fixed panel | Released base | c32 | RL seed1 | SFT | RL seed2 |
|---|---:|---:|---:|---:|---:|
| AG News official test | 423/512 | 422/512 | 427/512 | 426/512 | 429/512 |
| DBpedia | 204/224 | 209/224 | 209/224 | 208/224 | 210/224 |

All entries have all planned labels available; there are no malformed, missing or unknown-usage calls in this base run. The raw response/token/schema/body audit was already completed independently of the marker result. No additional model queries were made for this diagnosis.

On AG, base→RL seed1 has 19 gains/15 losses and 37 changed labels; base→RL seed2 has 18 gains/12 losses and 33 changed labels. Six/seven base-correct but c32-wrong labels are recovered, respectively; five/four labels become correct after both references were wrong. This is a mixture of recovery and improvement beyond these two reference outputs, not proof of a new capability. On DBpedia, c32 already exceeds base by five; RL seed1 adds nothing to c32’s headline and seed2 adds one. The released-base reference does not turn the weak official transfer results into a broad gain claim. Both RL seeds and SFT remain visible, with no better-seed selection. Paired uncertainty units are shared B4 requests within each panel, not pooled independent labels across datasets.

The owner took 506.00 seconds. AG calls summed to 321.68 seconds with 127,682 input and 10,949 output tokens; DB calls summed to 137.64 seconds with 60,945 input and 4,687 output tokens. Cache hits and unknown usage counts were zero. Released base used eager/no-LoRA/no-prefix-cache execution, while adapted references used LoRA, prefix caching and compilation. Costs are observed separate phase costs, **not matched-cost or isolated-weight comparisons**.

For future runs, use an explicitly predeclared in-worker activation and first-real-dispatch receipt, preserving exact model/source/environment/clean-release checks. Do not reuse the optional-warning gate or substitute this CPU sentinel test for device telemetry. No sealed owner, result, watcher or raw response was edited.

Reproduce the source/receipt checks with CUDA hidden using `marker_review.execute()` from `marker_review.py`; `RUNTIME_MARKER_ADDENDUM.json` records hashes, actual safe log excerpts, CPU fixture and all per-class/paired/cost details. The source-to-raw result itself remains `RESULT.json`; this is not a new independent scorer or trainer replication.
