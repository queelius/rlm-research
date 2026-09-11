# Actual root-RLVR path review — 2026-09-09

Outcome: **no optimizer/loss correctness issue established in the three committed updates. One material failure-classification issue is established in round04:** a completely identified, recovered child HTTP400 is promoted to campaign-fatal integrity failure. It is not an alias mismatch, lost request ID, or corrupted action capture. The frozen V2 STOP remains correct under its original conservative rule; this review changes no source, export, checkpoint, or running job.

## Material finding: P2 — known failed provider attempt is reported as integrity corruption

The [exporter](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-only-credit-v1/root_export.py:97") conflates `audit.status != returned` with an actual alias mismatch. The [campaign wrapper](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-rlvr-campaign-v1/campaign_native.py:264") promotes any such exception to `integrity_failures` whenever the overall episode completed and its sampled nodes remain trainable. Consequently, the otherwise recoverable failed request prevents a group from being constructed and stops the full campaign.

Executable evidence: [round04_failure_cpu.py](../../../../ARTIFACTS.md#unpublished-files "Not published: round04_failure_cpu.py"), [ROUND04_FAILURE.json](../../../../ARTIFACTS.md#unpublished-files "Not published: ROUND04_FAILURE.json"), exit0 in 2.94s using the existing native environment with CUDA hidden. It reproduces the original exception before doing any diagnostic projection.

- Exact episode: `ca1caf2a391bd5d3fa6e8573eae84ad9b941b3f6401c77a4f264f11efa5c1557`.
- Call index57 / request `c470812384eb474e9ea303539801b3a2` is depth1; all actual/trace/wire aliases agree on the fixed selected child, and its stored SHA is exactly `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`.
- Raw HTTP400 explicitly rejects **9,972 input tokens against an 8,192 context limit**. No sampled node, completion IDs, completion probabilities, or success response exists for that call. Its complete failure request/response is retained.
- All73 request IDs are unique and have request-local results; all73 aliases and weight bindings agree. The root completes with `Answer: 12`, strict reward0.
- A diagnostic-only in-memory copy that removes solely this proven unsampled failed call, retaining every graph node, passes the actual exporter's physical-branch reconstruction for all72 sampled calls: **5 root turns / 1,563 root action tokens, 67 successful child turns**. Root causal lengths are `[1580,2042,2506,3553,3574]`. All reconstructed tokens/log probabilities match native responses. The 64 recursive-subcalls metric counts invocations, not model calls; some children take multiple turns.

Smallest justified continuation proposal (design only): a **new, explicitly amended continuation** may classify a fully authenticated no-node/no-completion provider rejection as a recorded exclusion, not identity corruption. Keep this episode's training reward null and its observable strict0 in evaluation accounting; keep the original29 admitted rows, exact prompts/seeds/weights/optimizer state and all identity/capture checks. Rebuild a newly identified export/group, independently recheck it, and never edit/relabel the old STOP or export. Admit no new trace through this amendment. Unknown/missing IDs, model/depth/hash mismatches, sampled-token inconsistencies, or ambiguous partial responses must still stop the run.

This particular overlong prompt is policy-induced, so exclusion can censor difficult behavior. It is not evidence that the request was a random infrastructure outage. Training on its recovered root actions as strict0 could be scientifically reasonable, but would be a **separate, larger admission-policy change**, requiring explicit tests and accounting for successful calls versus unsampled failed attempts. Merely deleting the audit status guard would also fail the current sampled-call cardinality check and is not a valid fix.

## Committed updates: checks beyond the existing Adam1→2 snapshot

The exact import path is `campaign_train.py → campaign_common.pilot_math() → root-only-credit-v1/source/train_root.py → single_gpu_rlvr_tis_v3.py → single_gpu_rlvr.py`. The campaign and lifecycleV2 were read; lifecycleV2 patches service ownership and binding/spec evidence, not the loss. Collection stops the owned inference service before the trainer loads the current generation's root adapter. The child remains a separately fixed service policy and is not loaded into the trainable model.

[audit_cpu.py](../../../../ARTIFACTS.md#unpublished-files "Not published: audit_cpu.py") / [CPU_RESULTS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: CPU_RESULTS.json") passed in 7.70s with CUDA hidden and no model load. The result authenticates304 specific source/input/checkpoint files and checks their hashes again before publication; it does not recursively seal archived trees. The fixed audit slice is rounds1–3 and validation00/02, not a moving target.

| Committed round | Mixed episodes credited | Root turns / action tokens | Mean absolute log-ratio | Raw token ESS fraction |
| --- | ---: | ---: | ---: | ---: |
| 1 | 28 | 63 / 23,130 | 0.009921 | 0.995965 |
| 2 | 20 | 41 / 11,091 | 0.006895 | 0.997866 |
| 3 | 20 | 46 / 14,399 | 0.006870 | 0.997437 |

All96 training outcomes were admitted before within-task mixed-reward selection. Pure groups are excluded as declared, not silently made negative. Recomputed groups, membership, ordering, population-standard-deviation advantages and group identities equal the actual exports exactly. Each episode has equal total weight; each root turn has equal weight within its episode; each current action token has equal weight within its turn. Different-length turns therefore receive different per-token coefficients by design.

### Mask, shift, sign, temperature, and TIS

The actual loss uses logits at `prompt_length−1 ...` to predict only the current action suffix; it validates that all prefix labels/masks are excluded. Six CPU cases spanning positive/negative advantage and importance ratios0.1/1/4 matched the analytic gradient within **1.49e−8**, including the temperature0.5 chain rule, capped detached coefficient, causal shift and zero gradient on unrelated output-logit positions. Observation text can still influence root-action probabilities through the model's causal computation; zero direct observation credit does not mean zero influence on representations.

All150 credited turns' native wire input IDs, sampled output IDs, old probabilities, seed, depth, alias and adapter SHA were independently rechecked. Sampled stop tokens are retained. Requests use temperature0.5, top_p1, top_k−1, min_p0, max_tokens2048 and no schema, penalty or whitelist transform; the optional `routed_experts_prompt_start` field is capture-offset metadata, not a sampling transform. The installed [Prime configuration](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../../../research-cache/repos/prime-rl/packages/prime-rl-configs/src/prime_rl/configs/inference.py:623") defaults to `processed_logprobs`, also authenticated from each capture's service-log prefix. The installed vLLM sampler computes these after temperature/filter processing; its native token endpoint does not silently apply HF generation defaults to the explicitly supplied parameters. Thus the HF `log_softmax(logits.float()/0.5)` uses the intended support/temperature, not raw temperature1 probabilities.

The implemented gradient at this single pre-update pass is `−A × min(exp(log p_HF − log p_rollout),2) × grad(log p_HF)`, averaged as above. `proximal=current.detach()` makes the nominal PPO ratio exactly1; PPO's0.8/1.2 clip is therefore inactive. This is safe for the declared single full-batch increment, where no optimizer step occurs between forwards. It must not be advertised as multi-epoch clipped PPO. No reversed advantage, off-by-one action shift, duplicated context loss, or differentiated IS weight was found.

The conditional correction is **not exact trajectory importance sampling**. Its positive/negative gradient coefficients differ from unit weights by approximately0.663%,0.447%,0.487% in the three rounds. Token guards pass, but round1's per-episode summed log-ratios span −14.11 to2.08. A CPU example with1,000 conditional log-ratios of−0.05 passes every existing guard while its joint log-ratio is−50. This demonstrates the already declared limitation; passing these guards does not establish an unbiased on-policy trajectory gradient. HF FP32 adapters versus inference BF16 casts/backend numerics also mean the rollout and proximal policies are not bit-identical; the captures quantify sampled-action discrepancies, not full-vocabulary or trajectory fidelity.

### Persistent optimizer and policy loading

Beyond cursor counting, the audit reconstructs the actual **round2→round3** AdamW update from the saved first/second moments and all504 adapter tensors /16,515,072 parameters. The inferred gradient norm is0.1438944428 versus recorded0.1438944489; maximum second-moment recurrence residual is1.78e−15; maximum predicted parameter residual is1.86e−9. The actual deltaL2 exactly reproduces0.11790219287642255. Hyperparameters and parameter ordering match, not just step integers.

The trainer binds the generation to the immediately preceding adapter/config/optimizer/RNG hashes; reloading verifies exact saved FP32 tensor values and dtypes before training. Restore checks parameter-name order and unchanged AdamW parameter groups, then restores Python/Torch/CUDA RNG state. Model dropout is disabled and Qwen attention/LoRA dropout values are0. Checkpoint state is written last as the commit marker and binds the input group, correction capture and saved optimizer/adapter/RNG members. No stale policy load, lost Adam moments, unintended child update or repeated optimizer increment was established.

### Root reward fallback hypothesis ruled out in the audited admitted slice

All**112 admitted episodes** across rounds1–3 and validation00/02 have a completed, error-free trace with an explicitly non-None root reply. There are86 nonempty and26 empty root replies. The retained strict correctness score agrees with the admitted reward in every case. Since [Trace.last_reply](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../../../research-cache/repos/prime-rl/deps/verifiers/verifiers/v1/trace.py:630") uses even an empty non-None root reply before its last-assistant fallback, none of these rewards is sourced from an orphan child's fallback answer. The round04 exceptional episode also has an explicit nonempty root reply. This is not a claim about all excluded/incomplete traces.

## Bounded limitations and handoff

This audit does not rerun GPU forward passes, prove all backend log probabilities bit-exact, inspect unrelated Responses runtime behavior, or evaluate learning gains. It checks the actual sampled-action math and committed artifacts, not every possible malformed input. Outcome reward still cannot validate child semantics or faithful aggregation; all-action root credit and conditional correction retain their declared research limitations. No optimizer/loss patch is justified by these checks. Only the documented round04 classification distinction warrants a narrowly scoped, newly identified amendment if continuation is desired.

Reproduction commands (each requires a NEW output path):

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python audit_cpu.py --output NEW_CPU_RESULTS.json
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python round04_failure_cpu.py --output NEW_ROUND04_FAILURE.json
```

The systematic-debugging skill informed the failure diagnosis: reproduce the original failure, trace actual request/response identity, and distinguish the supported cause before proposing any change. No fix was implemented.
