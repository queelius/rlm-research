# Local cue replay: hold output history fixed

MAIN decision, September9,2026 16:38UTC. Outcome-informed exploratory follow-up
to the completed fresh96 and reminder experiments, not a preregistered replication.
No outcome-conditioned choice of individual records or successful trajectories.

Question: can changing only the current forced ID change which source label the
model prefers, when the entire previous output history is held fixed? Complete
sampled output comparisons mix local cue effects with diverging earlier labels.
This diagnostic separates those effects, without claiming to measure attention.

Options considered: another complete sampled batch repeats the existing signal;
synthetic explicit-label copying removes semantic inference but changes the task;
fixed-history conditional replay most directly addresses the current ambiguity.
Choose the third, in new `sidecars/leaf-local-cue-replay-v1`.

Use the exact eight64-record fresh96 AG/SST contexts and released Qwen3-4B-Instruct
2507 checkpoint, with no research adapter. Freeze four displayed target positions
16,32,48,64 (one-based) in every context.32 context-position units, each with
matching current ID, constant p0000 and shifted source(i+17)%64 current ID.
All prior output objects have constant p0000 tags and the correct displayed labels,
identically across the three conditions. This supplied history is explicitly
teacher-forced diagnostic input, not sampled behavior or new model training.
Only the final current tag changes. Use the exact shared fresh96 physical prompt
tokens after proving their matching/constant equality; do not silently change chat
templates. Preserve the serialized prefix and complete physical token IDs.

For each condition, compute unmodified next-token model log probabilities for
every complete canonical label continuation, including an identical closing JSON
boundary. Sum token log probabilities without length normalization. The primary
diagnostic is the displayed-correct label's normalized probability over this
finite candidate set and its matching-minus-constant change. Report argmax
classification and wrong-ID named-label probability separately. On positions
where displayed and shifted named gold differ, report the prospectively defined
disagreement subset without replacing the all32 primary. These are conditional
finite-label scores, not calibrated task probabilities or guided-decoder scores.

Token boundaries must be explicit: encode complete continuation texts and verify
the scoring prefix really is their common prefix. If the tokenizer merges across
the boundary, back off only to a shared token prefix and include the affected
boundary tokens consistently for every candidate; retain that accounting. Check
finite values, every candidate, causal next-token shift and mask, no label-token
leakage into its own predictive position, model.eval/no gradients, and exact input
length. Do not call generated programs, sample repairs, or condition on a model's
correctness. No hidden-state/attention or training update claim follows.

Native environment HuggingFace forward evaluation is a separate implementation
path from vLLM. Pin checkpoint and tokenizer revisions, environment and attention
backend, BF16 weights and FP32 probability reduction. Qualify a tiny CPU model
fixture for score alignment; no real model/GPU during preparation. Never silently
truncate, drop a position, or swap models if the full8192 context check fails.
Master981328001 (check collision scope); deterministic eval has no sampling-seed
replication. Approximately288 candidate forwards across96 conditional prefixes.
Keep all32×3 conditions/candidates and missing values, grouped by source context
and task, along with timing, peak memory and exact inputs. Checkpoint each finished
unit atomically; no resume that changes frozen inputs.

One A100, proposed900s outer,750s work with120s cleanup reserve. MAIN owns launch;
prepare a flat bounded command and verify the remaining allocation before starting.
Prefer a simple single-process batched or sequential forward loop over new service
machinery. A scientifically faithful failure is preferable to a new large framework.
