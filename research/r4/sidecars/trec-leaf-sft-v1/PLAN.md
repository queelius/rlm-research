# Leaf-data SFT implementation plan

> For agentic workers: execute this one cohesive research-driver task with focused
> test-first development and a separate review. The user authorizes autonomous
> decisions, independent GPU work, and external research-sidecar isolation; do not
> block on questions, broad repository tests, worktree setup or production polish.

**Goal:** produce a ready, resumable supervised child-classification experiment.

**Architecture:** a dataset preparation module authenticates existing question
partitions and native renderings; a small experiment driver trains the existing
rank8 adapter and evaluates matched greedy predictions. All new source and outputs
live in this additive sidecar; shared repositories and frozen experiments stay intact.

**Tech stack:** existing Python3.12 training environment, PyTorch, Transformers,
PEFT and safetensors. No new heavy dependency or environment install is required.

**Spec:** `DESIGN.md` is authoritative for exact experimental values and selection.

## Global constraints

No GPU launch by the preparing agent. No source-test-driven selection. No prompt or
padding loss. Preserve exact FP32 starting adapter values. No fabricated rollout
provenance. Raw third-party data remains outside Git. User-requested exploratory
pace overrides the generic production/worktree/merge ceremony; source hashes,
immutable attempt artifacts and a focused review provide this sidecar's recovery map.

## Task 1: Prepare the complete narrow experiment

Create `source/data.py`, `source/experiment.py`, `tests/test_leaf_sft.py`, a frozen
`RECIPE.json`, and a `READY.json`/`IMPLEMENTATION_REPORT.md` after CPU qualification.
Read the named source-provenance and leaf-contract files before adapting helpers.
The two source modules may be combined if that keeps the implementation simpler;
do not create a generic training framework.

- [ ] Test the normalization/group partition invariants with synthetic duplicate
  questions; assert that train/validation/test group intersections are empty and
  every declared group is used once per epoch. Verify actual pinned source counts.
- [ ] Test action masking and padding before implementing: an example with prompt
  tokens `[1,2]` and target `[3,4]` must yield labels `[-100,-100,3,4]`; right padding
  is also-100. Test native tokenizer prompt/full prefix equality on real prepared
  examples, without GPU loading. There are no old-logprob fields to validate/fake.
- [ ] Implement minimal preparation with frozen source/partition/recipe hashes,
  question-group/source-line references, canonical targets, epoch order and exact
  causal input/label arrays. Preserve prompt and target separately for later audit.
- [ ] Test strict positional scoring: correct-length canonical arrays are scored
  per record; wrong-length/nonstring/non-JSON/tool-call answers are format failures,
  never truncated into alignment. Validate greedy-generation padding/continuation
  extraction on deterministic CPU tensors and token examples.
- [ ] Implement training with exact FP32 adapter audit (reuse the proven converter
  audit), BF16 frozen base, action-token-normalized accumulated loss, checkpointed
  activations, finite gradients and explicit real optimizer-step accounting. Save
  every16steps/epoch, and validate saved cursor, optimizer/RNG and data identity on
  resume. Reuse checkpoint mechanisms, not the old self-SFT's rollout selection.
- [ ] Implement the design's matched greedy baseline, epoch validation, declared
  checkpoint selection, and selected-checkpoint test evaluation. Keep per-example
  raw generations/metrics and a machine-readable selection decision. Tests must
  prove that changing test outcomes cannot change checkpoint selection.
- [ ] Run focused CPU tests/Ruff and an actual CPU-only native-rendering preflight.
  Save commands/output, exact prepared token counts/max length and environment
  versions. Report the launch command and expected GPU ownership/memory/duration.
  A live GPU startup or forward failure remains an exploratory result, not a reason
  to run broad tests or silently relax the declared recipe.

The parent handles the single GPU and independently reviews source/spec alignment.
Record any unresolved concern with its likely impact; do not ask the AFK user.
