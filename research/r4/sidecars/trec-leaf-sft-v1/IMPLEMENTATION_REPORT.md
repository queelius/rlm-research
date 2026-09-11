# CPU implementation report

Prepared 2026-09-08. The narrow experiment is CPU-qualified and ready for the
parent's independent review and GPU scheduling. No GPU was launched or queried
by this preparing agent; parent owns the active A100 experiment. No shared source,
frozen input, home configuration, or existing environment was changed.

## Deliverables

- `source/data.py`: authenticates the frozen split, source inventory, original
  adapter identity/conversion, native contract, and all frozen model files. Resolves
  declared normalized groups to exact source line representatives; materializes
  two group-once epochs and fixed validation/test arrays.
- `source/experiment.py`: native matched greedy HF baseline, two-epoch supervised
  LoRA training, checkpoint recovery, epoch validation, validation-only selection,
  selected-checkpoint test evaluation and paired question outcomes.
- `tests/test_leaf_sft.py`: 16 focused CPU tests.
- `RECIPE.json`, `prepared-v1/data.json`, `prepared-v1/MANIFEST.json`: frozen read-only
  recipe and exact prompt/target/input/label arrays, source hashes and preparation
  identity. Raw third-party source representatives remain external to Git.
- `READY.json`: full launch command, ownership constraint, resume command, resource
  estimate and environment provenance.

## Protocol and audit behavior

The 5,065 training / 300 validation / 489 test group split is adopted exactly from
the pinned proposal. The loader authenticates every inventoried input and checks
every declared source-line set, coarse label and normalized hash. Synthetic tests
reject within-partition duplicates and cross-partition overlap. Every training
group appears once in each epoch. Epoch ordering starts from sorted group hashes
and uses one continuous Python `Random(981260100)` stream for two shuffles; this
routine choice is explicitly frozen in the recipe.

Five source questions form each supervised JSON-array message. Prompts use the
frozen leaf system/tools and exact definitions user condition. All 2,184 rendered
arrays pass native prompt/full prefix equality. Targets are canonical source
labels; there is no teacher model, rollout selection, grammar or old-logprob field.
Only native assistant-suffix tokens, including native end-of-turn and its template
newline, receive labels. Prompt and right-padding labels are -100. No truncation.

The original rank8 all-module LoRA starts from the proven Prime-to-PEFT conversion.
Its original source hash is checked against the frozen zero-update endpoint
descriptor; destination/config hashes are checked against CONVERSION.json. GPU
loading invokes the unchanged authenticated exact-value/dtype adapter audit.
Only LoRA parameters may require gradients and each must be FP32. The base is BF16
and frozen. Training uses AdamW LR 1e-4, weight decay0, norm clip1, constant LR,
SDPA, nonreentrant activation checkpointing, microbatch2 and accumulation8.
Summed causal action-token losses divide by the entire optimizer batch's action
token count, including the final 5-array batch (64 steps per epoch, 128 total).
Finite loss and gradient norm checks precede real optimizer updates.

Checkpoints are saved every16 steps and at both epoch boundaries. Each contains
adapter, optimizer, Python/Torch/CUDA RNG, full cumulative step metrics, cursor,
elapsed training time and frozen data/spec identity. File hashes authenticate
resume state. Atomic staging retains partial checkpoint directories on failure;
complete checkpoint directories are never overwritten. Explicit `--resume` uses
the latest complete checkpoint in the same attempt. It validates cursor/step
consistency and real Adam optimizer step counters, and resumes pending boundary
validation before further training. Failures are separately recorded with traceback;
failed examples are not silently dropped or replaced.

The 60-minute cap counts training steps; baseline, epoch validation and selected
test evaluation occur outside it. A signal bounds an individual training step by
the remaining cap. Checkpoint-save overhead is outside the accumulated step timer.
Parent can impose a larger overall scheduler wall cap if its reservation requires
one; preserving complete checkpoints makes that interruption recoverable.

Evaluation uses the same loaded HF backend, tools-aware native rendering, fixed
five-question grouping, two-array batches, left padding, greedy decoding and
256-token cap before/after. Continuation extraction uses the padded input width
and preserves raw generation tokens; JSON scoring removes only a final native
stop token. Wrong length, malformed/nonstring JSON, noncanonical labels or tool
calls fail the entire array without truncation or synonym relabeling. Canonical
arrays score per position. Outputs retain exact raw generation, content, token
IDs/costs, per-question outcomes, macro/classwise metrics and format failures.

Both baseline validation and baseline test are collected before updates. Epoch1
and epoch2 are selected by validation canonical accuracy, then validation
action-token NLL, then earlier epoch. SELECTION.json is frozen before post-training
test evaluation; changing test results cannot change the selector. Selected adapter
reload is audited exactly, and all489 test groups receive paired before/after
outcomes. This component makes no full-RLM or planner-improvement claim.

## Native preparation results

| Partition | Arrays | Prompt tokens | Supervised tokens | Maximum causal length |
| --- | ---: | ---: | ---: | ---: |
| Epoch1 | 1,013 | 826,037 | 22,429 | 891 |
| Epoch2 | 1,013 | 826,035 | 22,429 | 877 |
| Validation | 60 | 48,850 | 1,315 | 857 |
| Test | 98 | 78,255 | 2,238 | 840 |

Across prepared arrays: 1,779,177 prompt tokens, 48,411 supervised tokens; maximum
causal length891 is below the4096 cap. No examples were truncated or rejected.

Recipe SHA256: `556a69539f4d90df2c6b97341c343fbfb80d135dfcf3f92f17427dbb8bdab702`.
Data SHA256: `2de28bb4384ca1181f4dcf09dc2b121abdbfe4a15162bee830118651c34780d8`.
Preparation identity: `35ad159cd2eb4c2540227a6383037167103fa55f63020e01f57598921dcb59d0`.

## Executed commands and output

All Python checks used the installed training interpreter:
`/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python`.

1. `CUDA_VISIBLE_DEVICES='' <python> -m pytest -q <sidecar>/tests/test_leaf_sft.py`
   before implementation: **15 failed**, each on the missing module assertion.
2. The same focused command after implementation: **15 passed**.
3. Added a real tiny Qwen3+PEFT checkpoint test, including optimizer/RNG roundtrip,
   exact adapter audit, overwrite rejection and corrupted-file rejection.
4. Final same focused command: **16 passed, 1 warning in5.66s**, exit0.
   The warning is PEFT's expected missing pretrained-config warning for the
   synthetic tiny model; this CPU fixture has no downloaded base path.
5. `/project/alex_phd/envs/rlm/bin/ruff check <sidecar>/source <sidecar>/tests`:
   **All checks passed!**, exit0.
6. `/project/alex_phd/envs/rlm/bin/ruff format --check <sidecar>/source <sidecar>/tests`:
   **3 files already formatted**, exit0.
7. `CUDA_VISIBLE_DEVICES='' <python> <sidecar>/source/experiment.py prepare`:
   exit0; emitted the hashes/identity and exact counts above, with
   `all_native_prefix_checks_passed: true`, `gpu_launched: false`.
8. CPU environment inspection: CUDA build13.0 and `torch.cuda.is_available(): false`.

Environment: Python3.12.12, torch2.13.0+cu130, transformers5.15.1, PEFT0.20.0,
safetensors0.8.0, uv0.9.7. Existing training uv.lock SHA256:
`d18054c5eaf69dbc69bc71f14c603df462a6d660001f044915814a9157552158`.
The precise environment and lock path are recorded in READY.json; no install was
needed. Runtime revalidates the package versions frozen in RECIPE.json and records
actual GPU/CUDA identity with the adapter load audit.

## Remaining practical limits

Parent review and actual A100 startup remain. Estimated memory16–28GiB and
training15–45minutes plus evaluation5–20minutes are scheduling estimates, not
measured GPU evidence. A live startup/forward failure must be retained as exploratory
evidence, without relaxing the recipe. Source edits after this freeze will fail
launch authentication; a revised source requires an explicitly versioned new
preparation rather than editing immutable inputs.

TREC data licensing remains unspecified. Unknown pretraining contamination and
uninspected historical source families remain unresolved. Validation contains only
five abbreviation groups. None of these limits is represented as resolved by SFT.
