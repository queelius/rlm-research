# Leaf-only contracts and role-specific LoRA routing: bounded inspection

2026-09-08. CPU/source inspection only; no GPU request, installation, active-source edit, or heldout-outcome read. This is a feasibility recommendation, not an implemented or qualified treatment.

## Recommendation

Use an **inference-only EvalClient shim first**, preserving the qualified rootless nano execution path. Add trusted invocation-depth metadata at nano's request boundary, then change only the owned leaf request body after Verifiers applies its global overrides. A standard JSON-schema `response_format` needs less machinery than native TrainClient and is already captured by Verifiers' per-call sampling record. Do not export these constrained leaves into the current full-softmax RLVR estimator.

The motivation is measured, not hypothetical: the fresh native recursive collection captured 132 child calls and returns, but only 6/132 returns were entirely within the canonical label vocabulary. Canonical classification was 274/712 repeated predictions; the sole positive in the mixed-reward group contradicted its executed aggregate. These are development observations, not independent generalization cases. See the sealed [recursive process report](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/recursive-train-capture-v1/analyses/attempt-002/REPORT.md").

## Exact insertion points

1. **Trusted role signal:** pinned nano `RLMEngine._call_model`, engine line 675, knows `self.runtime_config.invocation.depth` and the ACP model-request ID. A new additive nano fork can attach declared depth/invocation metadata to `extra_headers` there. Mark checkpoint/compaction calls separately. The current header carries a request ID, not depth; committed semantic edges arrive too late to route that same request. Do not infer role from prompt wording or from the presence of a JSON array. With the proposed depth-1, compaction-disabled pilot, depth 0 is root and depth 1 is leaf; that rule is not sufficient for arbitrary deeper planners.
2. **Effective request:** `InterceptionServer.handle_request`, line 498, overrides every request with `session.ctx.model` and global sampling. `sample`, line 680, subsequently calls `session.client.get_response(dialect, body, ...)`. A process-local EvalClient shim at this latter seam can validate the trusted role signal and modify the per-request `body['model']` and `body['response_format']` before forwarding. Never mutate shared `session.ctx`, client fields, or global sampling across concurrent root/child calls.
3. **Truthful trace:** `record_call`, line 415, reparses that same body and records its actual `model` and sampling. Therefore update the owned body, not just an unrecorded private copy sent upstream. Preserve ACP linkage and additionally seal a request-ID-keyed role/contract audit: depth, root/leaf role, actual alias, schema/hash, caller-payload hash, derived N, application status, and attempt descriptor hash. Reconcile this audit with committed semantic edges and retain records of failed/uncommitted exchanges.
4. **Wire format:** EvalClient line 73 forwards the body unchanged. ChatDialect line 345 includes `response_format` in its sampling fields, but not top-level `structured_outputs`; a CPU parse check confirmed that the complete standard response-format object survives in trace sampling. Installed vLLM's `structured_outputs_from_response_format`, line 189, converts JSON-schema response format to its structured-output JSON parameter. This is also the documented [vLLM 0.28 structured-output interface](https://docs.vllm.ai/en/v0.28.0/features/structured_outputs/). The local Qwen3 chat template contains neither field; still verify unchanged rendered root/leaf prompts across the paired treatment before calling it prompt-matched.

This requires an additive nano request-header fork plus a sidecar client shim; it is not an existing configuration-only switch. The root's output parser, tool parser, model messages, and effective sampling are not rewritten by the schema shim. Unexpected/missing role metadata is a routing failure, not permission to guess that a root is a leaf.

### Honest cardinality, without an oracle

For the smallest pilot, retain `rlm(prompt)` and put an explicit caller contract envelope in the executable example **identically in both arms**: a fixed contract name and the actual caller-selected `questions` string array. The surrounding child instruction still asks for one canonical label per supplied question. Only depth-1 requests with that exact declared envelope are eligible. Construct the schema as an array whose items are the six public canonical labels, with `minItems = maxItems = len(questions)`. No gold, gold-derived subset of labels, answer, context-wide record count, completed output, or label-map lookup is needed or permitted in the shim.

Validate the envelope with a strict, unambiguous parser and bounded payload size. A missing/nonconforming envelope is recorded as contract-not-applicable and forwarded unconstrained in both arms; it is not counted as successfully enforced. Preserve intention-to-treat episode results and report application coverage. This is explicit partial enforcement, not a hidden fallback. The root remains free to choose batches, omit the envelope, use tools, or answer directly. The new envelope/example is a shared prompt change relative to earlier runs, so only the new matched pair isolates enforcement.

A generic caller-supplied `rlm(prompt, response_schema=...)` would be cleaner for reuse, but the current API and extra-forbidden broker request accept only `prompt`; that option requires an API/broker/supervisor extension. It is unnecessary for the first task-derived pilot.

An enum-array grammar restricts the leaf's action space, including preventing normal tool-call text; it is not merely a passive output validator. Describe the intervention as **constrained leaf classification**, not unconstrained reasoning with harmless formatting. Root planning remains unconstrained, although different leaf results can legitimately change subsequent root behavior.

## Smallest paired full-RLM experiment

- Three explicitly reused development tasks 12000008/09/25, two fresh seeds per task, enforcement off/on: **12 episodes**, no optimizer update.
- Same frozen root and leaf weights in both arms; executable envelope example and label definitions identical. Freeze the chosen definitions condition after the separate leaf72 diagnostic and before this collection. Do not select it on heldout results.
- Same rootless image, context mount, task, seed, temperature 0.5, full-support sampling knobs, 2048-token call cap, depth 1, no compaction, and existing execution budgets. Alternate pair order; at most four paired workers; 1800-second study cap; atomic checkpoint after each episode. Predeclare fresh seed coordinates and output/spec paths at preparation, not in this inspection note.
- Primary diagnostics: contract application coverage, strict enum/cardinality compliance, scorer-only semantic label accuracy, distinct-record coverage, actual committed child calls, terminal strict reward, and agreement between computed aggregation and final answer. Report per-episode cost/latency and infrastructure, routing, truncation, and completed-policy errors separately. Use the train-only map only in the scorer; never mount it in the runtime.
- Before GPU collection, narrowly test root/leaf routing, request-body/trace metadata agreement, malformed-envelope handling, and concurrent request isolation. Then qualify one real root/child exchange under the new fork. No broad framework work is needed.

The same 89 records and three questions are heavily reused development data. This pilot can show that enforcing the leaf contract helps or hurts this harness; it cannot establish transfer to independent documents. Grammar compilation/server errors remain infrastructure failures; a completed wrong or malformed policy answer is an observed policy outcome. Estimator incompatibility is a separate property from either category.

## Root and leaf aliases on one 4B base

**Feasible with the same request-local role shim.** In nano, `_run_child` copies the parent runtime config and changes only invocation context (supervisor line 332); hence model/provider inheritance currently gives one policy. Changing nano's child model alone would still be overwritten by Verifiers' global model override. Route aliases after that override, and freeze an immutable role-to-alias-to-adapter-path/hash map in the attempt descriptor.

vLLM accepts the LoRA name as the request `model` and supports multiple adapters subject to server limits; see [vLLM 0.28 LoRA serving](https://docs.vllm.ai/en/v0.28.0/features/lora/). Installed native token serving also resolves the request model through `_maybe_get_adapters`. For two simultaneous non-base aliases, declare `max_loras=2`, `max_cpu_loras>=2`, and rank capacity at least both adapters' ranks; use the same base weights and tokenizer. This does not require a second base model, but memory/throughput on the allocated MIG remains an empirical readiness check. The current single-adapter service is not already qualified for it.

Use distinct immutable alias names for distinct weights, never overwrite a loaded alias during paired evaluation. Installed KV-cache hashing includes the LoRA **name**; do not rely on identical names distinguishing changed tensors. Record actual effective alias and schema on every branch, descriptor hashes, adapter hashes/dtypes, source hashes, renderer identity, server settings, and ACP role linkage. Keep renderer/tokenizer identity tied to the base model rather than mistaking an alias for a tokenizer repository.

For a clean **leaf-only supervised** comparison, train native-rendered classification targets from authoritative training labels, freeze root weights R, and compare `(R, L0)` versus `(R, L_SFT)` with schema/definitions held constant. Start L_SFT from the same L0 as the control. Root trajectories may change because leaf answers change; that mediated effect is intended. Supervised target likelihood does not need constrained-rollout-policy importance weights. A comparison against historical root/self-SFT runs is descriptive unless prompts, data, starting weights and changed roles are actually matched; a later root-by-leaf 2x2 is the attribution experiment, not a prerequisite for the first pair.

Split by independently grouped documents/context windows **and source question identity**, with exact-question deduplication and declared near-duplicate handling before training. Official TREC train membership does not itself establish a clean local experimental split. The current 89 questions already appeared repeatedly in development rollouts; fitting their source labels tests fit, not generalization. Do not train on context6 evaluation labels or use their outcomes to select this treatment. Public taxonomy definitions are task knowledge; per-question gold remains training targets/scorer-only. Rebatching the same questions does not create independent evaluation data, and historical pretraining overlap remains unknown.

## Why native TrainClient is not the first implementation

TrainClient line 324 reads model/messages/tools from the body but generates using the session SamplingConfig's `wire_args`; adding only body `response_format` does not impose a grammar on its native generation request. It would require an explicitly cloned per-call generation sampling config, truthful body/trace metadata, and constrained-policy accounting.

The existing exporter checks one expected alias, temperature and top-p/top-k/min-p, but does not account for grammar support or replay `node.sampling_mask`. Thus complete token/logprob capture alone would not make these turns compatible with the current full-softmax TIS trainer. Mixed aliases are also currently rejected and a single-adapter trainer cannot recompute both policies unchanged. Do not run the existing exporter on the new inference-only treatment as if its admission checks established compatibility.

Native sampling-mask capture is not a simple fix under today's sampling contract: the inspected Prime configuration describes it as engine-wide and requiring positive temperature and positive top-k, whereas current root sampling uses top-k=-1. Constrained-policy RLVR needs its own support/mask replay design and validation. Keep that separate from the proposed inference-only comparison and from ordinary supervised leaf training.

## Inspected source fingerprints

Paths below are immutable evidence references, not proposed edit targets. Nano is pinned to `4ef3438d55fdd39b18d34035833c73e13b006733`; current local source is authoritative for the inspected behavior.

| Source | SHA-256 |
| --- | --- |
| `/project/alex_phd/research-cache/2026-09-08-literature/leaf-contract.7HPUr5/nano__engine.py` | `2e04fe4589c75cef1ba3fdbbaead1275c40984588bf782e972c5556e3cc7f7ed` |
| `/project/alex_phd/research-cache/2026-09-08-literature/recursive-example.6xBrmx/src__rlm__supervisor.py` | `1b9a1b303b7c2a389d8981d0c7ea9d3e5603b49f8a420f354220c6a28c9cc78e` |
| `/project/alex_phd/research-cache/2026-09-08-literature/recursive-example.6xBrmx/src__rlm__broker.py` | `dd966afe72795fe2beb18b9a691194488c9ea365fa6886833d4be06d5106852e` |
| `/project/alex_phd/research-cache/repos/prime-rl/deps/verifiers/verifiers/v1/interception/server.py` | `d96061ec740017cc10bcbe63ba2d378b67558f22b07b0c1303399d9f4787da08` |
| `/project/alex_phd/research-cache/repos/prime-rl/deps/verifiers/verifiers/v1/clients/eval.py` | `709b9cc9416c6c5d49946f271744e5c36101312a0017460c92581888e4a83698` |
| `/project/alex_phd/research-cache/repos/prime-rl/deps/verifiers/verifiers/v1/clients/train.py` | `87356166967c2cd283e6212dc32f955590e6722bc7636f2af13df301f6e53705` |
| `/project/alex_phd/research-cache/repos/prime-rl/deps/verifiers/verifiers/v1/dialects/chat.py` | `fe932c3696df7e25e22b4ff4b5ba002adba3efeb26527912f47d0b3cae23d665` |
| `/project/alex_phd/envs/prime-rl-5990b1b/lib/python3.12/site-packages/vllm/entrypoints/openai/engine/protocol.py` | `5e6935461da65b9c398db08cebc797db3eeb9a8515d7c743c8ce6c4a6b3e6242` |
| `/project/alex_phd/envs/prime-rl-5990b1b/lib/python3.12/site-packages/vllm/config/lora.py` | `ed6cf6575f5950f079a62f904caeae93d1a4745dd8c21788b74367883bcd4b08` |
| `/project/alex_phd/envs/prime-rl-5990b1b/lib/python3.12/site-packages/vllm/v1/core/kv_cache_utils.py` | `088f2201bee86fade694e78141b6e99a5cd0cdd23c5c7ab3526dd119f76e4aec` |
| `/project/alex_phd/runs/rlm-research-r4/sidecars/trec-leaf-contract-probe-v1/CONTRACT.json` | `cb50c6fddff7ea62a96936a7fcb58da84307248028adb420d7b1ab971a74bea7` |
| `/project/alex_phd/runs/rlm-research-r4/sidecars/strict-rlm-client-qualification-v2/export_causal_turns.py` | `47beb310b1089603a84c0b1ef9f311c2a5f92197f76daac9728af60c3e9145c2` |

The source fingerprints were checked locally after writing this note. No future treatment is frozen by this note.
