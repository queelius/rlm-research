# Optional source-bound receipts: bounded end-to-end experiment proposal

2026-09-09. Design only; no implementation, runtime/service invocation, GPU call,
acceptance, or current independent-root outcome inspection. Main chooses whether
to implement. This proposal does not alter any frozen campaign.

## Recommendation and question

Add an experiment-local Python helper module to each **new owned rootless task
runtime**, using the already available `runtime.write` seam. Keep the pinned nano
engine, broker, Prime native inference route, scoring, and model weights unchanged.
Test a common optional indexed-call helper with raw-result access versus the same
helper plus an optional, gold-blind validated receipt. This separates receipt
availability from the already helpful act of requesting indexed labels.

Question: with a capable fixed root and the original recovered child, does making
requested-record correspondence explicitly inspectable improve exact aggregate
answers, at what actual token/call cost? Root chooses whether to use the helper,
its requested records and query, batching, recovery, and final computation.

This is a new local experiment, not a novelty claim. String-returning recursive
calls, programmatic aggregation, typed outer results, and source-indexed outputs
already appear in the original/nano/Lambda comparison. The untested part here is
the incremental end-to-end value of this optional receipt in this pinned runtime.

## Evidence motivating, and limiting, the hypothesis

- Completed 368 helper controls establish no specialized indexed-SFT advantage:
  B versus indexed-trained TREC indexed/free is 740/768 versus 738/768; SST is
  478/512 versus 479/512. Keep old c32de to match the root experiment, not because
  these results establish it as the best child.
- Old-only exact meaningful tags beat equally shaped constant placeholders by
  262/512 TREC and 153/512 SST labels. Output-token differences are small, but the
  changing-counter versus identity mechanism remains unresolved. These are leaf
  label results, not demonstrated end-to-end aggregate improvements.
- Root96 gives historical step8 root 20/24 unchanged versus 14/24 with a text
  return-type reminder; original root 6/24 versus 9/24. The trained root already
  issued structured first-root tools in 24/24 both arms. A general syntax lecture
  or compulsory new plan is therefore an unattractive intervention.
- The concrete `.extend(x.answer)` signature occurred once in original/unchanged,
  not as an established dominant trained-root failure. Receipt usefulness must
  actually be observed; do not assume a widespread string/list bug.

Sources: [root96 report](../../analyses/root-contract-factorial-live-2026-09-09/REPORT.md),
[368-control report](../../analyses/grammar-training-padding-controls-2026-09-09/REPORT.md),
[runtime comparison](../../ideas/2026-09-09-official-runtime-comparison.md).
`CURRENT_SUMMARY.md` was also read, but its earlier summary is not substituted for
these completed controls.

## Actual executed runtime and exact seams

All run-relative paths below are under `/project/alex_phd/runs/rlm-research-r4`.
This is **not** a change to `/project/alex_phd/repos/rlm/src/rlm`.

| Layer | Inspected source and actual API | Consequence |
|---|---|---|
| Prime harness | `/project/alex_phd/research-cache/repos/prime-rl/deps/verifiers/verifiers/v1/harnesses/rlm/harness.py`: `RLMHarness.setup`, `_install_dir`, `_runtime_metadata`, `prepare_acp` | Configured nano version `4ef3438`; setup installs into `/tmp/vf-rlm-<version hash>` inside owned runtime. ACP starts its `bin/rlm --acp`; metadata carries max depth and policy. No host package upgrade needed. |
| Public task files | `sidecars/official-rlm-prime-pilot-v1/src/oolong_prime_v1/taskset.py`: `OolongTask.setup` calls `await runtime.write("context.txt", context_bytes)` | A private task subclass can call inherited setup and write `receipt_api.py` plus a public-only catalog into the same `/app` working directory. Explicit `from receipt_api import rlm_records` avoids modifying unknown REPL bootstrap code. |
| Qualified hooks | `sidecars/root-only-credit-v1/native_routing.py`: `installed_hooks` wraps `RLMHarness.setup`, then runs the established engine overlay; patches `TrainClient.get_response` | Preserve hooks and actual `/inference/v1/generate` capture. Add task-local files after inherited task setup, not a replacement model client. |
| Qualified engine overlay | `sidecars/leaf-role-routing-v1/source/routing.py`: `patch_engine`, `overlay_program`, `route` | Engine source is hash-gated; overlay adds trusted depth/invocation/request headers. Root/child routing changes only the model alias. Do not edit this source or bypass it. |
| nano public recursion | Cached `recursive-example.6xBrmx/src__rlm__api.py`: `async run(prompt: str) -> RLMResult` | A local async helper can call `rlm.api.run` while executing in an active IPython cell. No native schema, label arguments, or receipt API presently exists here. |
| nano return transport | Cached `src__rlm__types.py`: `RLMResult(answer: str, session_dir, usage, turns)`; cached `src__rlm__broker.py`: `run`, `result_to_payload`, `result_from_payload` | Broker explicitly requires exactly those four result fields. Adding a dataclass receipt field would change the wire contract. Instead derive a local wrapper/receipt **after** the original result has crossed the broker. |
| nano ownership | Cached `src__rlm__supervisor.py`: `_run_child` constructs a child engine with inherited runtime config and cwd; `engine.run(prompt)` returns its result | Local helper does not start its own engine/client/service, choose another model, add recursion depth, or implement retries. Existing depth-one child lifecycle remains authoritative. |
| Current independent campaign | `sidecars/root-rlvr-independent-seed-v1/campaign_native.py`: private original collector plus recovered-child amendment; `CAMPAIGN.json` pins inherited sources | Same qualified native collection family; proposed experiment is evaluation-only in a distinct namespace, not a callback or hot patch to the live campaign. |
| Score | `sidecars/prime-rlm-strict-pilot-v1/src/oolong_prime_rlm_strict_v1/taskset.py`: `StrictOolongTask._terminal_result`, `correctness`, `official_correctness` | Preserve strict terminal exact aggregate success and separate official-score diagnostic. Receipt validation must never become reward. |

The cached nano files are under
`/project/alex_phd/research-cache/2026-09-08-literature/recursive-example.6xBrmx/`;
active engine reference is
`/project/alex_phd/research-cache/2026-09-08-literature/leaf-contract.7HPUr5/nano__engine.py`.
Inspected hashes:

| File | SHA256 |
|---|---|
| Prime harness | `7256f1efe1d0b44c8488e62edc93c41fa2da1fae95620bc6de4dea2e7d517bfc` |
| Active engine before qualified role overlay | `2e04fe4589c75cef1ba3fdbbaead1275c40984588bf782e972c5556e3cc7f7ed` |
| Cached API | `1dfb9c24346625a18956ddb830f8c7d66508c5ee40aa8446a5d60d8d88fb8794` |
| Cached types | `e36bbd80af5bb8fd72d51920cbff4b4fcd1081498ccda7b8dd25db9ba8e9784c` |
| Cached broker | `dd966afe72795fe2beb18b9a691194488c9ea365fa6886833d4be06d5106852e` |
| Cached supervisor | `1b9a1b303b7c2a389d8981d0c7ea9d3e5603b49f8a420f354220c6a28c9cc78e` |
| Native routing | `5ea35866be87662372ca1b312ddabbbab9ce009915fbfaa31353455ec702e841` |
| Independent collector adapter | `89398238b535fe302f426301d44c09fbe2f4d7d57cbc67a74dabf3ec5bcecd49` |

Frozen image is
`sha256:53a70288e91a75c9bc8cbc9a75da4c3d156227266fd8ec6c997deb8ef7f921552`
(`localhost/verifiers-rlm-python:3.11-slim-single-id-v1`). The separately acquired
new nano checkout is **not** a substitute for this pinned source. Its local Git
object store does not contain `4ef3438`; no fetch or upgrade was attempted. I did
not claim to inspect the active IPython bootstrap: this design intentionally
avoids patching it. Local-module import and active broker scope remain the small
integration qualification below, not a claimed completed runtime test.

## Three small approaches

1. **Pure optional parser:** `parse_receipt(child.answer, expected_ids, allowed_values)`
   or a local `ResultView.receipt(...)` method. Approximately one stdlib parser;
   no recursive call changes. Cheapest, but caller-supplied IDs alone prove only
   correspondence to that declaration, not that those records reached the child.
   Anonymous historical answers cannot be upgraded to indexed evidence by parsing.
   Useful fallback, weaker test of source-bound consumption.
2. **Recommended: optional source-bound call helper plus local receipt.** One
   module uses a public catalog and deterministic indexed prompt builder, calls
   existing `rlm.api.run`, preserves the original result, and derives a receipt.
   Both arms get the same builder. No grammar/decoder implementation is added:
   the current recursion API accepts only text. Some child results will be invalid;
   that is visible evidence, not something to repair.
3. **First-request code-native control.** A minimal prompt example could ask for
   the existing structured `ipython` call before prose. A genuinely forced prefix
   or new tool/JSON grammar would require a native-renderer/inference intervention,
   not merely an `rlm()` argument. With trained-root first-tool syntax already
   24/24, this is lower priority and not a substitute for receipt evidence. If
   module integration is unexpectedly expensive, choose approach 1, not a new
   decoder or scheduler.

## Minimal receipt contract

Proposed interface, not implemented API:
`await rlm_records(selected_ids, query, allowed_values)`.
An optional `source_records()` exposes the public catalog. Original `rlm(prompt)`
remains available and unchanged. No automatic batch splitting or all-context call.

- Derive catalog IDs from physical record positions (`q0001` etc.), preserving
  Date/User/Instance text, source question-group IDs from `TRANSFER_PUBLIC.json`,
  full context hash, and exact selected record-byte hashes. Public metadata only;
  do not copy `TRANSFER_HOST_GOLD.json` or label maps into the runtime. Reject an
  unknown/duplicate selected ID before making a model call. Do not regenerate IDs
  from output order or silently substitute text supplied by the root.
- Root chooses arbitrary selected IDs, query, and allowed result vocabulary.
  It may ask full classification or target membership (for example `yes`/`no`),
  and may ignore the helper altogether. A target-only aggregate does **not** need
  six-label evidence or a complete six-way label vector. The suggested example
  does not become a compulsory decomposition or coverage reward.
- Freeze one indexed JSON-array-of-objects prompt constructor shared by arms.
  Each object has exactly `id` and `label`; prompt includes requested source IDs
  and text in declared order. Receipt stores exact request text/hash, selected
  IDs, source hashes, unmodified `.answer`, session/usage/turn information, parsed
  records, missing IDs, duplicate IDs/keys, unknown IDs, invalid labels/types,
  parse error, and `valid`. Parse once with strict JSON including duplicate-key
  detection and rejection of non-JSON numeric constants. No fence stripping,
  prefix extraction, case normalization, canonical-label substitution, answer
  fallback, or retry.
- Valid means exactly one well-formed record for each requested ID, no extra ID,
  and all labels in the caller-declared vocabulary. Preserve returned order in
  diagnostics; a valid ID-keyed mapping may support order-independent access.
  Do not silently make a partially repaired mapping usable: invalid receipts have
  `labels_by_id=None`, retain the parsed raw records and visible error details.
  Validation says nothing about semantic correctness.
- Coverage is explicitly **requested-subset ID coverage**, and optionally union
  coverage against this public context for calls actually requesting a compatible
  task predicate. Do not merge incompatible queries/vocabularies into one semantic
  coverage score. No helper use means coverage not applicable, not zero reward.
- Broker/runtime/transport exceptions propagate; log their original class and
  detail separately from malformed model text. A supervisor limit string becomes
  visibly unparseable raw output, not a fabricated label. Unknown failures and
  unanswered episodes remain separately counted, never silently converted to a
  negative learning reward. There is no training in this experiment.

## Paired evaluation: 24 coordinates, 48 end-to-end episodes

Use all six existing 64-record transfer contexts, window IDs 1200–1205, and both
original aggregate questions (human-being count, numeric-value count), with two
fresh rollout seeds per task. This is **24 matched pairs / 48 total episodes**,
not 48 pairs. Copy/freeze all coordinates and prompt bytes before any outcome.
Use seed master `981267100`; per-task/repetition native seed
`981267101 + 2*task_index + repetition` (24 distinct values, each reused only across
its two arms). Audit against prior run manifests before freeze; if a collision is
found, report/redeclare before any run, never silently reseed during execution.

Inputs: `sidecars/root-rlvr-campaign-v1/inputs/TRANSFER_PUBLIC.json`,
`TRANSFER_HOST_GOLD.json`, `PROVENANCE.json`, inherited exact tasks in
`root-return-contract-factorial-v1/SPEC.json`. The public transfer SHA is
`5d2ea9736ff6247656080a5ec234dbfe17141f8da2274c192e26ae52e703b14c`;
gold SHA is `1cb7e891d2d378a0e7d8e82cc89ff907925d89b90d4ed09ee68bcee73f45c9ee`.
These are constructed TREC training-supported contexts, source-group disjoint from
pilot root, earlier composition, leaf validation, and leaf test groups according
to inherited provenance. Their 384 groups are selected from 4,681 eligible groups.
They are already exposed developmental evaluation coordinates, not fresh held-out
confirmation; no new dataset is needed. Do not mislabel them as official OOLONG
held-out tasks merely because the OOLONG-style task wrapper is reused.

Fixed weights, chosen without inspecting the current independent-seed outcome:

- Root historical step8:
  `sidecars/root-recovered-child-continuation-v1/outputs/attempt-001/round-08/training/checkpoint-8`,
  adapter SHA `473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd`.
- Child original recovered:
  `sidecars/trec-leaf-sft-v1/outputs/attempt-001/checkpoint-0128`,
  adapter SHA `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`.
- Base:
  `/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554`.
  Reuse full frozen config/weight/tokenizer closure, not adapter hashes alone.

**Raw arm:** common indexed helper returns a local view preserving `.answer` and
native metadata; root is told raw JSON can be decoded with ordinary Python.
**Receipt arm:** same call signature and prompt constructor; view additionally
offers `.receipt()` with the contract above. Root is told it may inspect this.
Both use the same source catalog and optional example batch. Remove the inherited
anonymous-label example equally in both arms, replacing only that example with the
common indexed helper; preserve public task question and strict scoring. Freeze
the two short consumption examples and their token counts. Do not add the root96
global reminder or an imposed plan.

This estimates an **interface-plus-its-minimal-documentation** effect relative to
an indexed-helper baseline, not receipt internals in isolation and not unchanged
historical harness versus new harness. No padding control is needed for this first
practical test; document any instruction-token imbalance. Identical helper
arguments must produce byte-identical child prompts across arms. Actual root
choices can diverge and must not be described as physically paired child calls.

One A100, same qualified multi-adapter native service, depth 1, same renderer,
temperature 0.5, top_p 1, top_k -1, min_p 0, max_tokens 2048, no new retries.
Preserve inherited timeout configuration, maximum paired concurrency, and native
retry caveat. Interleave arms within the one weight binding with seeded balanced
order, retaining coordinate-paired seeds. Save raw provider requests/results,
traces, task terminal outputs, helper audit and prompt/source hashes per episode.

Expected shape: root96 used 1,108 native calls, 1.18M input and 158,593 output
tokens across 96 episodes, with 17.73 minutes startup/collection/release. Half that
episode count suggests approximately 550 calls, 0.6M input and 80K output tokens,
and about 8–15 minutes on the same A100; these are planning estimates, not quotas
or a throughput guarantee. Set a 1,800-second whole-job cap inclusive of startup
and owned cleanup, with at least 120 seconds reserved for cleanup. Stop collection
at its declared deadline; preserve incomplete pairs/unanswered episodes without
replacement. Release service/GPU ownership before nonessential CPU analysis.

## Necessary small qualification and decision rules

No tests below were run during this read-only design task. Implementation should
need one small module, private task/collector adapters, and focused tests, not an
engine refactor or new scheduler:

1. Stdlib parser table: valid/reordered IDs, missing/duplicate/unknown IDs,
   duplicate keys, wrong labels/types, fences/truncation/extra prose, target-only
   vocabulary, empty selection, and exceptions. Assert raw answer unchanged,
   invalid mapping unavailable, no invented labels, no retry.
2. Fake async API: identical selected IDs/query/vocabulary yield byte-identical
   prompts in both arms, exactly one `run` call, unchanged native metadata and
   propagated exception. Assert source catalog contains no host-gold fields and
   task score/prompt question/context identity is unchanged across arms.
3. One focused integration qualification in a **new owned** pinned rootless
   runtime, after main authorization: task-local module imports from active
   IPython; `rlm.api.run` reaches the original broker; returned RLMResult still
   passes its exact four-field round trip; wrapper is local only. A fake broker
   response suffices for serialization/import qualification, followed by at most
   one declared live smoke episode if needed, with evaluation inputs already
   frozen and the smoke coordinate excluded from the scored comparison.
   Check installed source hashes and actual trusted depth/alias capture. This
   design task did not start a runtime or execute generated code on the host.

Primary report: paired exact-success gains/losses/ties over 24 coordinates, by
context and question, with all 48 scheduled outcomes accounted for. Report
completed observable denominator separately from operational scheduled yield;
unanswered/infra failures are not semantic wrong answers. Secondary: actual
root/child calls, tokens/cache usage, elapsed time, helper uptake, invalid receipts
by reason, requested-ID coverage, visible root syntax failures and recovery,
and whether executed code actually accessed receipt fields and used them in an
aggregate. AST/access logs are observed consumption evidence, not proof of causal
reasoning; root-writable logs need corroboration with native traces and raw calls.

No net success gain, or gain only with large token/call inflation, fails the
practical benefit hypothesis at this setting. Improved shape with unchanged exact
answers is not a task-success benefit. Zero/low uptake is a usability failure of
this offered API, not proof that receipts cannot work if used. Failures dominated
by wrong semantic labels falsify the stronger idea that validation alone fixes
the aggregate problem. A positive pilot merits a new context-disjoint replication
and mechanism ablation; it is not confirmation or evidence of novelty.

## Completion and limits

Only this proposal was written. Source inspections were CPU/read-only. No current
independent-root results were read, and no source/manifest/acceptance/runtime was
changed. Remaining material uncertainty is the small module-import/active-scope
qualification, not an unbuilt scheduler or likelihood model. Main can dispatch
implementation of approach 2 immediately; fall back to approach 1 if that seam
cannot be qualified within a short preparation window.
