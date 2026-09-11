# Leaf-data SFT design

Declared 2026-09-08; prepare on CPU while independent GPU experiments run.

Question: can direct supervision of child classifications improve semantic accuracy
beyond clear instructions, and can those improved workers help a frozen RLM planner?
This first component trains/evaluates a child policy. It does not by itself establish
a leaf-only full-RLM intervention; that requires separately verified role routing.

Data: adopt the5065 train /300 validation /489 test normalized question-group
partition in `../trec-leaf-split-provenance-v1/PROPOSED_SPLIT.json` (SHA256
3f5f648488d512d2052b9f3d57c02e030af8e939ca363998c07a556a47d7f457).
Read source representatives through its authenticated inventory/normalization,
not a new unpinned dataset revision. All11 train/test collisions are excluded on
both sides; validation excludes the inspected OOLONG pool. Prior unknown sources
and base-model pretraining remain unverified. Dataset licensing is unspecified;
keep all data external to Git and record the caveat.

Training targets are JSON arrays of the six canonical coarse labels, not model
rollouts, solved aggregate answers, fabricated logprobs or a stronger teacher.
Use the exact native leaf system/tool template and the frozen definitions user
condition from `../trec-leaf-contract-probe-v1`. Shuffle training group IDs with
seed981260100 and batch five questions per supervised message, once per epoch;
two epochs, each containing every training group once. No decoder grammar during
SFT. Do not relabel synonyms or include gold in the prompt. Loss applies only to
assistant target tokens, including the actual native end-of-turn token; all prompt
and padding labels are-100. Exact prompt-prefix equality must hold; no truncation.

Base: existing frozen Qwen3-4B-Instruct-2507; start from the exact original zero-
update LoRA using the verified PEFT key conversion at
`../single-gpu-self-sft-control-v1/inputs/step0-peft-key-conversion-v2`.
Preserve FP32 adapter tensors with `autocast_adapter_dtype=True` on the BF16 base.
Rank8, all original target modules, no base-weight update. AdamW LR1e-4,
weight_decay0, clip_grad_norm1.0, constant LR; microbatch2, accumulation8,
effective16 supervised arrays/step, including the final short batch. Seed981260200.
Use installed pinned training environment and SDPA/checkpointed activations.
Max causal length4096; reject overlong examples rather than truncate them.
Training wall cap60minutes; checkpoint at least every16 optimizer steps and each
epoch, with adapter, optimizer, RNG, data cursor, source/spec hashes and step metrics.
Preserve partial checkpoints on failure; explicit resume only, never overwrite.

Prepare matched greedy inference evaluation arrays (five questions each) for all
validation and test groups. Keep definitions fixed, no decoder constraint, output
cap256. Evaluation can run in the loaded HF model to avoid repeated serving reloads;
use the same backend/rendering/batching for before/after comparisons, record them,
and do not equate this to the prior temperature0.5 vLLM experiment.
Baseline and final test outputs may be collected, but choose between epoch1/epoch2
using validation only: higher canonical validation accuracy, then lower supervised
validation NLL, then earlier checkpoint. Freeze the choice before inspecting post-
training test results. Test outputs do not drive an optimizer step or selection.
Primary per-record canonical accuracy, plus macro/classwise scores, exact array
validity, raw generations, token costs and paired per-question outcomes. Source
questions, not repeated predictions, define grouping. Report failures separately.

Do not claim full-RLM or planning improvement from this component. Queue frozen-root
before/after worker routing only if its heldout semantic result justifies it, with
unchanged prompts/harness and truthful per-call aliases. Do not pass these supervised
examples or future grammar-constrained generations through the old RLVR admission
code by manufacturing old-policy probabilities.
