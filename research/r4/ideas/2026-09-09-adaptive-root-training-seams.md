# Two small training paths: implementation checklist, not approval

Prepared while uptake96 is active, without reading its outcomes. Complements the
[training-options memo](2026-09-09-adaptive-root-training-options.md). No targets,
data reservation, numeric recipe freeze, new training source or model calls.

## A. Interface SFT: supervise native root actions, not a leaf answer array

**Reusable pieces.** [Leaf data helpers](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/trec-leaf-sft-v1/source/data.py:146")
provide `causal_example` prefix/length checks and `collate` right-padding/masks.
[Leaf experiment](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/trec-leaf-sft-v1/source/experiment.py:79") provides
`loss_sum` shifted token-sum CE, `audit` exact loaded-PEFT identity,
`save_checkpoint`, `checkpoint_state` and `validate_cursor`. The existing
16-example optimizer boundary fits the memo's provisional 32 action examples ×
two exposures = four updates. This is feasibility, not evidence that four steps
are sufficient. Do not call its whole training entry point unchanged: it binds
the original leaf dataset, original adapter, leaf evaluation and selection flow.

- Freeze the **root** system message, actual available tools, public task prompt,
  Qwen3 `enable_thinking=True` and native renderer revision. Use the inherited
  native setup/graph contract; the leaf `data.render` is not suitable. It emits
  plain label-array assistant content through HF chat-template serialization.
- An authored example is an actual root model-call prefix plus one authored root
  continuation. Prefix includes system/tools/user, earlier root actions and real
  observations. It must exactly match the native physical prefix token IDs.
  Use the renderer's append/bridge path for a later turn; do not assume a fresh
  whole-conversation re-render preserves earlier sampled bytes/reasoning.
- Supervise only the **current root continuation**: content, tool-call syntax,
  arguments and the native end-of-turn token. Mask every earlier token, including
  earlier root actions in that example, child text, tool observations, public
  context and padding. Prior root actions get targets only in their own examples.
- Crucial renderer boundary: `Qwen3Renderer._render_assistant` marks
  `<|im_start|>assistant\n` as scaffold, tool-call markers/arguments and
  `<|im_end|>` as sampled, and the trailing template newline as **not sampled**.
  Naively supervising everything after an HF generation prefix through the full
  rendered message also supervises that newline. End the target at the actual
  stop token; compare the renderer masks/native continuation rather than use
  plain full-message suffix length as the whole loss mask. Preserve BPE boundaries.
- `render(..., add_generation_prompt=True)`, `render_ids`, `parse_response` and
  `bridge_to_next_turn` in the pinned renderer are the concrete APIs. Require
  `full[:len(prefix)] == prefix`; do not fix a mismatch by slicing causal tokens,
  disabling thinking, stripping tools or changing their key order. Declared
  formatting is an authored target, not a claim about a model's hidden reasoning.
- Interface-only targets may teach imports, `source_records`, the helper call and
  strict decoding. A task-specific filter/reduction program teaches a **plan**;
  rename and separately declare it rather than claim an interface-only treatment.
  Any prior observation comes from executing an operator-defined fixture in the
  owned CPU runtime. Do not invent a child answer; an example can end at the call.
- Record target authorship, context/source IDs, public query, prefix/target token
  hashes, role and masks, target-token exposure, precision and checkpoint cursor.
  Starting historical step8 must be explicitly pinned; fresh SFT Adam is new
  state, not an accidental restoration of its historical RL optimizer.

**Smallest later qualification.** One owned CPU-native two-root-turn fixture:
an authored public-file load, its real tool observation, then a helper-call action.
Prove first and second physical prefixes, parsed ipython arguments, no helper
gold fields, exact stop boundary and zero observation/child/padding target tokens.
This fixture uses fake provider responses and cannot supply sampled behavioral
likelihood. Add one tiny actual PEFT CE update with those masks and save/reload:
base frozen, LoRA-only finite delta, masked labels affect no CE terms, four-step
cursor convention and optimizer/RNG restoration correct. No broad training suite.

## B. Adaptive terminal RLVR: historical weights, genuinely new Adam generation 0

**Reusable pieces.**
[`campaign_train`](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/root-rlvr-campaign-v1/campaign_train.py:19") has
`optimizer_step`, `make_optimizer`, `restore_optimizer`, `update_generation` and
the authenticated-group path. [Common identity helpers](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/root-rlvr-campaign-v1/campaign_common.py:98")
have `generation_identity`, `check_generation`, `checkpoint_policy` and contiguous
commit validation. [Root export](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/root-only-credit-v1/root_export.py:11")
has causal branch reconstruction/native graph-to-wire proofs;
[`validate_root_turn`](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/root-only-credit-v1/source/train_root.py:100")
enforces depth, weight, exact sampled lengths, sampling and no causal truncation.

- Create an explicit **new starting-policy manifest**: adapter SHA
  `473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd`,
  authenticated historical checkpoint/selection lineage, new-campaign step 0,
  `optimizer_reset=true`, empty Adam and separately seeded new RNG. Historical
  update count 8 remains provenance, not the new optimizer cursor.
- The two actual blocking guards are `original_policy()` and the step-0 branch
  of `authenticate_policy()`: both require original `857a…`. Privately adapt
  these to the accepted starting manifest; do **not** bypass weight checks or
  relabel historical step8 as an original model. `restore_optimizer` already
  returns on new step 0 after checking empty optimizer state. Do not load
  historical `optimizer.pt`/RNG; do authenticate their origin if required by the
  historical checkpoint closure. New steps 1 onward restore **new-campaign**
  Adam/RNG in exact parameter order, with moment steps 1, 2, …, 8.
- Preserve `generation.previous_policy`, campaign/plan/group identity and fixed
  child `c32de…` at every native request and update. Policy 0 generates round 1;
  policy 1 generates round 2. All accepted rollouts for a round are fresh from
  its exact policy, not repeatedly optimized stale examples.
- The proposed two prompts × eight attempts requires a **16-row admission
  adapter**; original `authenticate_group` hardcodes 32, broad uses 24. Do not
  weaken its raw coordinate/episode/manifest/native replay checks. Declare new
  adaptive public task and host-gold builders, query-varying schedule and seed
  namespace; retain exclusions rather than reuse pilot rows as training data.
- Only genuine native **sampled root** tokens go in `episodes[].turns`. Child
  actions remain separate role evidence; tool and child observations in later
  root prefixes are masked. A valid direct root solution can receive credit;
  recursion shape is not admission. Equal-reward groups provide no GRPO-like
  relative gradient; do not reroll/select new targets until mixed.
- Reuse `tis_action_loss` and `distribution_summary` unchanged: recorded native
  old probabilities supply correction, current-forward `detach()` supplies the
  proximal reference only for the single full-batch step, then exactly one Adam
  update after every backward contribution. Keep correction cap/guards,
  nonempty root masks and binary within-prompt advantage checks. A cost reward
  is not compatible with unchanged binary admission and needs a separate decision.
- Save every new step with adapter/config, Adam/RNG, generation, source and input
  binding, cursor, gradient/delta and correction capture. `checkpoint_policy`
  authenticates INPUTS, group/export, correction and state; this is the commit
  point even if RESULT is absent. Reuse both recovery paths to prevent a second
  update after a crash. Fixed final new-step8 is not validation-selected.

**Smallest later qualification.** One native fake root→child→root capture under
the new starting alias; prove exact step8 disk binding and root-only masks, and
reject stale-policy/child-credit edits. Two tiny real PEFT updates from a pinned
test adapter with fresh Adam must show 0→1→2, exact save/reload moments/RNG, no
child/base mutation, and recovery after checkpoint-before-RESULT without a second
step. One 16-row fixture tests mixed/null/all-equal admission and exact coordinate
coverage. These are CPU fixtures, not new scientifically sampled episodes.

## Hard separation and decision gate

Adaptive40 operator arms have zero sampled root actions. Their code can be an
explicitly authored SFT target, but their calls/rewards cannot become a root RL
trajectory with invented old logprobs, advantages or root credit. Fake qualification
logprobs are likewise test values, never trainable research data.

After complete uptake/adaptive evidence: choose SFT for a demonstrated interface
bottleneck; choose terminal RLVR for a competent free policy with mixed valid
rewards and useful planning headroom; evaluate a separately declared cost objective
only when correctness cannot discriminate the plans. Neither path is approved by
this checklist. No pending outputs were inspected to write it.

## Inspected source identities

Most trainer/data source hashes are also pinned by the accompanying feasibility
JSON. Direct inspection for this checklist included these exact revisions:

| Source | SHA256 |
| --- | --- |
| Native `renderers/qwen3.py` | `75c4d4a96c7fe930b0fe80d83df894133e1319b364b033cf97fbea2d84e8e146` |
| Leaf `source/data.py` | `b5aa353e2173c3fd48ecc36ce0596c9c3328767a7d82c8d22c57b4e0a32f0b8f` |
| Leaf `source/experiment.py` | `c4a66731f544c57821b8f0bf81eb6f5785f12f943b61b8bc4e3916a1dcef041c` |
| Campaign `campaign_train.py` | `38fe3087b8deb94ee8e0fa2e0330ca34a822f84192031c389ff32acf00d79d1f` |
| Campaign `campaign_common.py` | `17e888550668638673fa725c6a580b7580b6abd975bd27f69b8be7ad628800ea` |
| Pilot root `source/train_root.py` | `131bf68610ed54b102cb6aae4b0c73635877811d887039ea8ca4a3002c701a26` |

Native renderer path:
`/project/alex_phd/research-cache/repos/prime-rl/deps/renderers/renderers/qwen3.py`.
No inspected source was modified.
