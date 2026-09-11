# Role routing CPU handoff

Implemented and qualified a narrow inference-only root/child weight intervention.
The twelve reused development episodes are frozen in SPEC.json; binding the SFT
adapter waits for the existing validation-only SELECTION.json. No GPU was launched.
The parent design timestamp was corrected from21:53 to21:49 before specification freeze.

## Trusted boundary and truthful trace

An additive setup hook first installs the pinned nano runtime in each newly owned
rootless container using the existing qualified RLMHarness. It verifies SHA256
`2e04fe4589c75cef1ba3fdbbaead1275c40984588bf782e972c5556e3cc7f7ed`
and adds depth, invocation ID, a duplicate ACP request ID and ordinary/checkpoint/
compaction kind to nano's request headers. Original and changed paths/hashes are
recorded per owned runtime. The verified setup patch targets the installed editable
nano checkout; no image rebuild or shared clone/cache mutation is needed.

Prime strips the original ACP transport header into its semantic metadata but
preserves the four custom role headers through get_response. This was checked with
the actual extract_acp_info function and the real rootless exchange. The per-request
EvalClient wrapper changes body['model'] after Prime's global override. Root depth0
always uses original; depth1 uses the coordinate's original or selected-child alias.
Client configuration supplies an immutable child choice; no shared session model or
sampling is changed across concurrent requests. Missing/malformed role metadata is
an observable error. Checkpoint calls retain depth-based routing and their kind;
unexpected compaction calls fail under the no-compaction design.

Messages, tools and sampling are untouched. No schema, prompt rewrite, forced
recursion, repair, or fallback is introduced. The unchanged body is subsequently
read by actual Verifiers record_call, so the trace alias equals the forwarded alias.
Atomic request/result audit records retain request ID, invocation/depth/kind,
message and payload hashes, role-map hash, adapter hash, aliases, timing and errors.
Reconciliation matches actual trace ACP IDs and aliases, including uncommitted audit
exchanges; no trace is admitted or exported as RLVR data.

## Real CPU evidence

`CUDA_VISIBLE_DEVICES='' /project/alex_phd/envs/prime-rl-5990b1b/bin/python source/qualify.py`
completed with a real newly owned rootless runtime, IPython recursion, interception
server and deterministic local HTTP provider. It made three calls: original-root,
selected-child, original-root. The raw episode/provider requests and setup/source
hash records are in qualification-attempt-001. No model weights or GPU were used.
The fixture supplies synthetic responses and does not mount any gold label map.

Qualification result: both depths0/1 observed, three actual calls reconciled by ACP
request ID, zero missing/uncommitted audits and zero routing errors. Installed source
was `/tmp/vf-rlm-4fa91253816bfa64435b7b727ec01bac2a7a7a2b72ece29ceb2474d26f95418d/checkout/src/rlm/engine.py`;
modified SHA256 `841ca409ff888fc5b8de894ef46bc7e0089160067e5e6c704f45b15ce363b996`.
The container was managed and cleaned up by the original qualified runtime.

Ten focused tests pass, covering routing after global override, actual record_call
alias equality, prompt preservation, malformed role rejection,40 concurrent isolated
requests, pinned-source patch rejection, legitimate checkpoint routing and ACP
reconciliation/error retention. Initial tests failed on missing implementation;
checkpoint and reconciliation tests each failed before their implementations.
Final pytest output: `10 passed in2.15s`. Ruff check passed. Long embedded overlay
lines retain the byte-identical CPU-qualified snippet via narrow Ruff exclusions.

An initial direct docker probe without the existing runtime's host-network option
failed because slirp4netns is unavailable. The qualified DockerRuntime's host-network
path worked; no host packages or configuration were changed.

## Frozen comparison and reuse

SPEC.json SHA256 `079ad6151ea6a7e6ad02c2104f1ff22d2cd54681bb984d670b439de5754ebfde`.
Plan SHA256 `dab60f603ea4d27a3eb42fec8b728a8e35a5b0d4ad4a5b96d8e5a3f017c4bcb1`.
Three development task IDs12000008/09/25, two fresh paired seeds, two child aliases,
alternating pair order, at mostfour pair workers and1800s study cap. Both arms receive
the exact definitions-enabled executable example. Root temperature0.5, full-support
knobs,2048 call-token cap, depth1 and disabled compaction are inherited unchanged.
Per-episode atomic outputs, raw failures and old runtime recovery/error accounting
are reused. Source files are authenticated before dispatch.

The independent48 runner can import driver.py and call:

```python
spec = make_spec(endpoint, None, tasks, plan, study_name)
# Freeze spec now, bind selected adapter only after validation selection exists.
await run_study(spec, tasks, output, binding)
```

`endpoint` contains `url`, `model=driver.ORIGINAL`, `api_key_env`, `renderer_model`.
Tasks are existing strict OOLONG task objects. Arms are original_child/sft_child;
call `with_prompt(task, arm)` to derive matching frozen prompt/task hashes. Plan rows
use the existing qualification coordinates: task_name,arm,id,pair_id,pair_order,
group_id,seed,temperature=.5,client_path='eval',analysis_split and dispatch_order.
Raw UTF8 context SHA256 is used consistently. Role audits are saved beside the main
attempt at `<attempt>-routing` so all errors survive even incomplete episodes.

## Service handoff and limits

READY.json provides exact bind, dual-LoRA service and study commands. serve.py uses
the existing qualified Prime launcher helpers with the same frozen base/config,
changes max_loras/max_cpu_loras to2 and keeps the existing lora_dtype=auto inference
cast to BF16 base dtype. FP32 adapter disk bytes remain exact; this is explicitly
recorded as a standard serving cast, distinct from missing adapter keys.
The installed InferenceConfig accepted this config on CPU. At startup it authenticates
the frozen selection and both adapter files, launches one owned process group, loads
both immutable aliases and verifies both are advertised before recording ready.
It writes full original and selected endpoint descriptors with base/adapter hashes
plus serving dtype metadata; endpoint.json is the original alias for native controls.
It neither overwrites aliases nor updates an active service. Parent must assign the
GPU and supply the existing local API-key environment variable.

Dual-LoRA GPU startup, actual memory use and kernel compatibility remain unmeasured.
The service preserves startup failure evidence; no bitwise FP32 kernel agreement is required.
The driver directly reports strict correctness, recursion and runtime/cost metrics;
record-level canonical coverage, aggregation consistency and final-versus-computed
agreement remain downstream analysis of the retained raw traces with scorer-only
source labels, as assigned to the parent's analysis agents. No full planning or
unseen-source generalization claim follows from this development comparison.
