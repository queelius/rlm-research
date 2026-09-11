# Can a child-role instruction prevent costly, irrelevant tool loops?

2026-09-09. Design and source-seam review only; no implementation, model requests, service changes or training. Candidate data, suffix and seeds below are fixed prospectively for the proposed comparison. Parent review/acceptance is still required before implementation or launch. BROAD16 and its continuation remain untouched.

## Question and smallest comparison

Does explicitly telling a child to classify answer types, rather than solve the embedded questions, reduce model/tool work while preserving strict final root answers? Compare the existing coding-agent child prompt with that same prompt plus this exact suffix, separated by two newlines:

> For this child task, classify the answer type requested by each supplied question; do not answer the embedded questions. Work from the supplied text, without Python, package installation or external sources. Return only the requested labels in the requested format.

Tools remain available with identical schemas. This is an instruction, not an enforced text-only child. Do not change root prompts, child user requests, model weights, sampling, answer parsing, recursion availability, retries or error/admission rules. No grammar, examples, forced decomposition, fallback, answer repair, oracle or weight update is introduced. The suffix itself adds input tokens, which count toward cost and the unchanged context limit.

Sixteen full RLM episodes: four context-task groups × two fresh paired seeds × two arms (`control`, `child_role_suffix`). Pairing is at the root task/seed level, not a claim that adaptive child trajectories are paired. Four pair workers execute paired arms sequentially, with first-arm order counterbalanced. No child request is replayed, rewritten or forced to exist in the other arm.

## Why this comparison is informative, and selected

The [amplification report](2026-09-09-child-call-amplification.md) documents 648 child model calls across 150 child invocations, plus 22 root calls, in four deliberately selected costly episodes. Children repeatedly requested Python/package work instead of answer-type classification. These are distinct attributed calls, not evidence that transient retry configuration caused the amplification. All depths were 0/1; maximum depth did not remove the child's coding role or Python tool. These examples motivate the intervention but do not estimate its prevalence.

Those four episodes contain only **three distinct context-task groups**. The fourth group below is the already exposed 32-record comparator proposed in the source report, not a fourth invented failure case. Historical `training`/`validation` names are identifiers: every group is exposed diagnostic data in this no-training study. The old validation context is no longer an untouched validation test for this hypothesis. Selecting costly failures creates regression-to-the-mean risk, even with fresh seeds.

| Group, used verbatim | Records / target | Selection reason | Raw UTF-8 context SHA-256 |
|---|---|---|---|
| `training-016-00:human_being` | 16 / human being | `bc260859…`: repeated nationality-solving/package loops | `1f08b46485f9c1ae78995fff2597d92e4caf3f4cb9fb60fcc25b3234d08a73a7` |
| `training-032-00:numeric_value` | 32 / numeric value | Same-round, exposed moderate-cost comparator; not one of the four selected failures | `022c79dbfb242a9026d29ddec912ea90746b4b3d517d7b73abc9a6068fdd7e99` |
| `training-064-00:entity` | 64 / entity | `06b81671…` and `fe197cde…`: costly child loops and repeated dispatch | `3b62089059aa91fd24fa15cab317c4b284caa1d390c72abee21a60f2a4a21d66` |
| `validation-064-02:entity` | 64 / entity | `4c521e61…`: child web-search/package loops | `609135f44ab213c13f42484add2f5940fd25dc103170a3732c02436896235b3c` |

Read exact texts/questions from [PUBLIC.json](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/root-broad-curriculum-v1/inputs/PUBLIC.json"), SHA `2c466164e9aaffe2571c1f83c18b394345213c82610b7fc3068282600b1eee6b`. Use the existing `example_definitions` root wrapper without changing a byte. Each query is the existing whole-context category-count query ending with the strict `Answer: [X]` instruction. Preserve source IDs/window IDs and the exact source provenance. [HOST_GOLD.json](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/root-broad-curriculum-v1/inputs/HOST_GOLD.json"), SHA `384f15ed3ff64d3a9444bfa47a1534132e8f7de8bfcb96a8b4ded621a35b1ff6`, is host scoring only; no gold enters runtime files or prompts. Existing TREC/public-source overlap and license caveats remain, including leaf-training support for these compositions.

Master seed `981273001`; sampling seeds **893350289** and **62794825**. Derivation: first four SHA-256 bytes, big-endian, of UTF-8 `leaf-child-role-suffix-v1:981273001:i`, modulo `2**31-1`, for `i=0,1`. Both arms share the seed at each coordinate. Freeze order by the table order, first seed across four groups then second; first arm alternates by `(group_index + seed_index) % 2`. A read-only audit found no seed/master collisions in 24 named sidecar `PLAN.json`, `PLAN-*.json`, `SEEDS.json`, `SPEC.json` files below 2 MB outside output/training/service directories. Sorted path-list SHA: `ff7e414eb2779e614617f3fd7a6dd28cde89e4fa1d264141b87602b12d7c94c6`. This is a scoped check, not a global uniqueness claim. Preparation must additionally check new accepted plans created since this design.

## Exact source seam: before conversation construction and rendering

The executed implementation is pinned Prime/nano, **not** this repository's `src/rlm` engine.

In pinned nano `RLMEngine._start`, immediately after `_active_tools` and `_active_tool_schemas` are obtained, line 363 loads `system_prompt = self._load_system_prompt(self._active_tools)`. Lines 365–368 then build `self._messages` from that system string and the supplied user prompt. Append the suffix **between those statements**, iff trusted `self.runtime_config.invocation.depth == 1`. `_start` runs once per invocation; do not append again on subsequent tool/model turns. Do not alter `_active_tools`, schemas, user message, runtime depth, root append string or any subsequent observations.

Proposed additive implementation boundary:

1. A new owned sidecar imports authenticated collector/lifecycle helpers. A small private collector seam sets a host-only `ContextVar` to the frozen row arm around `environment.run_slot(...)`, resetting in `finally`. This is the existing call at `plan-hint-crossover-v1/driver.py:494`. No condition is inserted into the kernel environment or a model-visible root prompt. Concurrent setup propagation must be qualified, not assumed.
2. An owned setup hook awaits the inherited `RLMHarness.setup`, then applies a counted, hash-authenticated source transformation inside that episode's private container before ACP launch. Control receives the existing role-header overlay only. Treatment receives the identical role-header overlay plus the depth-1 `_start` insertion above. Record trusted coordinate/arm, runtime identity, original/role-patched/final engine hashes and patch counts. No shared clone, cached snapshot or frozen overlay is edited.
3. Reuse native `TrainClient` routing/capture; it selects the original root and fixed child aliases and records actual provider token IDs/results. Do **not** edit system/user messages in the HTTP or `get_response` layer. Prime `TrainClient.get_response` uses `turn.prompt` for intercepted turns (`train.py:348`), otherwise parsed body messages, before renderer/bridge construction. HTTP-only mutation could disagree with that graph and silently fail to change the sampled prefix.

Do not use Prime `_runtime_metadata`'s `append_to_system_prompt` as a global treatment: `harness.py:143–144` applies generic system metadata and is not the isolated depth-1 seam. Nano `_load_system_prompt` (`:918–932`) builds a coding role with tool availability; its depth check removes recursion wording but not Python.

The depth-1 suffix must appear in the initial child conversation, the native graph system message and the rendered physical prefix. Native bridge/continuation paths must preserve that same initial system message. Original and treatment depth-0 messages and tool schemas must be byte-identical. Child user requests are equal only on an actually matched prefix of adaptive trajectories; report first-root physical prompt equality and observed matched child user hashes, rather than claiming all children are matched. Same-seed service trajectories can still differ under batching/non-determinism.

## Model, resource and failure contract

Root: exact converted original adapter `857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6`; fixed child: epoch-2 checkpoint-0128 `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`. Both use original Qwen3-4B-Instruct-2507 revision `cdbee75f17c01a7cc42f958dc650907174af0554`. Authenticate actual endpoint alias/path/config/model identities once per owned service, not per request. No trained BROAD16 root is substituted.

Keep native renderer `qwen3`, thinking enabled, temperature 0.5, top-p 1, top-k -1, min-p 0, 2048 maximum generated tokens, context 8192, max depth 1, no compaction. Preserve existing 900-second rollout/1020-second episode and tool timeout settings; the shorter overall cap can censor them. No new per-child turn limit: calls per invocation are an outcome. Retain inherited nano transient retry behavior and native SDK zero retries; count observed physical attempts separately from successful sampled calls and idempotent replay when observable. No added retries or rerolls after failure.

One A100, original-root/fixed-child dual alias. Warm expectation 10–20 minutes, uncertain because failure-enriched controls can loop; **1800 seconds inclusive of service startup and owned cleanup**, at most 1500 seconds collection, reserving 180 startup and 120 cleanup. Inherit an absolute deadline so unused startup time cannot violate the total. Four pair workers mean at most four active root episodes; inherited child fan-out remains unchanged. Do not promise all 16 episodes will complete.

Proposed numerical request guard: at most **2048 actual native provider dispatch attempts across the study**, checked immediately before dispatch, shared by both arms and recorded monotonically. It is a global safety ceiling, not a per-child policy limit. If exhausted, stop collection, retain dispatched-call evidence, mark canceled/incomplete episodes budget-censored and unstarted coordinates unrun. A prevented dispatch is not a provider failure, sampled completion or policy-negative reward. The same applies to the wall cap. Report arm/order-dependent exposure if a cap binds; no unqualified cost-win claim from censored totals. No fallback to a direct classifier, no forced `tool_choice=none`, no reconstructed answer and no evaluation-to-training export. If this guard cannot be added without compromising capture, report that implementation boundary before readiness rather than changing the scientific contract silently.

## Prespecified readout

Primary, per attempted root episode and paired root coordinate: strict final answer; total physical model calls; actual prompt/generated tokens split by root/child; and end-to-end elapsed time. Report sums and within-context paired differences with all four context summaries, not a pooled invocation-level significance claim. Serving/cache/batching effects make elapsed time less clean than call/token counts. Keep unavailable usage/cache fields null; do not infer tokens for rejected unsampled calls from nonexistent completions.

Keep separate columns for strict correct, observable strict wrong/malformed, empty or absent final answer, completed trace with recovered provider errors, episode-level infrastructure failure, admission exclusion, budget-censored, and unrun. A recovered child error does not automatically make a completed observable root answer unknown. Conversely partial captures are not fabricated policy negatives. Preserve the historical child-overflow/equality attribution logic where applicable; this inference-only ablation does not revise RLVR eligibility or claim new root-token credit.

Secondary per **invocation**: child model calls, tool-request turns, observed executed tool outcomes, package/import/error classes, first/last prompt lengths, exact/over-limit rejected calls and sampled empty completions. Per root: actual child dispatches and repeat/restart patterns, using trace edges rather than code strings alone. Report labels/format adherence only when the child's requested contract and returned text make the denominator interpretable; do not invent correspondence for an invalid array. Record root prompt IDs, each child initial user hash, actual arm-specific system hash, schemas, alias, invocation/depth, request ID and physical request/result paths.

Success signal for a larger unselected replication: consistent call/token reductions across the three failure-enriched groups without fewer strict correct answers, empty-child substitution or more null/censored outcomes. If only one context improves, treat it as a localized mechanism example. If costs fall because useful children stop answering, revise the suffix. If treatment is ignored and loops persist despite verified physical insertion, retire role wording as a sufficient remedy for these cases. Eight pairs are too small for a robust general-effect estimate; no automatic promotion or further launch follows.

## Focused qualification required before READY

1. Test first: exact original/role-patched source hash and one insertion site; reject changed source, duplicate insertion and unknown arm. A control transformation must equal the historical role-patched engine exactly. Depth 0 must remain byte-identical; depth 1 must append once and retain tools/user text; an unsupported depth must not acquire a suffix.
2. Concurrent fake episodes with interleaved setup prove host `ContextVar` arm isolation/reset and matching runtime overlay identities. This is a collector/setup test, not generated-code execution.
3. In an owned rootless runtime only, trusted operator-authored fake native root→child→root sequences qualify both arms, including a child tool→second-model-call path. No GPU/provider model calls. Require exact graph-to-rendered native token equality at the initial child and continuation; unchanged root initial IDs; unchanged tool schema/user IDs where applicable; expected child-system suffix delta; correct aliases/depths. Inspect actual captured requests rather than a separately reconstructed ideal template. A source-only string test is insufficient.
4. Exercise an observable wrong answer with a recovered unsampled child 400, an empty sampled completion and a whole-episode interruption; assert distinct readout states. One tiny counter/deadline fake checks that the dispatch budget records only sent requests and never relabels stopped work as a sampled failure. Reuse existing owned-process cleanup checks, not a new scheduler or broad suite.

Preparation publishes source/input/qualification hashes and exact launch argv only after these bounded checks. Parent alone accepts and launches after active work; no interruption of BROAD16 or sentinel is requested.

## One alternative, not a second implementation

A hard text-only child could remove IPython or force `tool_choice=none`. It would directly prevent tool loops, but tests capability restriction plus a changed decoding/action contract, not whether the existing child can follow a better role instruction. It could also remove useful computation for other child requests. Prime's pinned RLM harness does not provide arbitrary disabled-tools support as a drop-in equivalent. Prefer the suffix first because it isolates an existing permissive prompt-policy mismatch. If verified suffix adherence fails, a separately specified hard-tool ablation becomes useful; do not silently combine them now.

## Source identities inspected

Paths below are exact; source inspection is read-only. The linked machine evidence retains the underlying episode/request paths and hashes; this design does not repeat its 674-source audit.

- [Amplification machine evidence](../../../ARTIFACTS.md#unpublished-files "Not published: 2026-09-09-child-call-amplification.json"): `24959d53f484a3a08b90974aef77721fafd3a0769cc2d04595291cf67d604871`; report `9b256f59231dae97806603c8c65af1d48ca794559cfc2e83eb27a31a97548243`.
- `/project/alex_phd/research-cache/2026-09-08-literature/leaf-contract.7HPUr5/nano__engine.py`: `2e04fe4589c75cef1ba3fdbbaead1275c40984588bf782e972c5556e3cc7f7ed`; executed nano commit `4ef3438d55fdd39b18d34035833c73e13b006733`, MIT. Historical role-patched engine: `841ca409ff888fc5b8de894ef46bc7e0089160067e5e6c704f45b15ce363b996`.
- `/project/alex_phd/research-cache/repos/prime-rl/deps/verifiers/verifiers/v1/harnesses/rlm/harness.py`: `7256f1efe1d0b44c8488e62edc93c41fa2da1fae95620bc6de4dea2e7d517bfc`.
- `/project/alex_phd/research-cache/repos/prime-rl/deps/verifiers/verifiers/v1/clients/train.py`: `87356166967c2cd283e6212dc32f955590e6722bc7636f2af13df301f6e53705`.
- [Native capture/routing](../sidecars/root-only-credit-v1/native_routing.py): `5ea35866be87662372ca1b312ddabbbab9ce009915fbfaa31353455ec702e841`; [role overlay](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/leaf-role-routing-v1/source/routing.py"): `8575081694a6ceea8d5f4058d4f625eb81d34f617a680f94bc06968e3a3ca78f`.
- [Pinned collector](../sidecars/plan-hint-crossover-v1/driver.py): `406a64ca59e4d77e6126c3fd97339c57cb5d7aef6808c998d7e18be7e6456832`; local target of any future private seam, not permission to edit this historical file.

No novelty claim: this is a targeted role-specialization/context-cost ablation prompted by actual failure traces. A positive result would support a specific harness–policy interaction, not general reasoning improvement or the adequacy of any RLVR curriculum.
