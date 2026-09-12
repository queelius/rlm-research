---
schema: openai-mrcr-procedural-sft32-onpolicy-screen-question-v1
status: cpu-ready-not-launched
optimizer_steps: 0
gpu_queries: 0
---

# Can procedural-SFT checkpoint 32 support exact-reward grouped root RL?

Collect four fresh on-policy trajectories for each of the first eight records in the frozen
`MODEL_INPUTS_V2` training order.  The fixed policy is the authenticated checkpoint 32 root; the
child remains the zero adapter.  The schedule uses seeds `202609200000..202609200031`, temperature
0.5, top-p 1, top-k -1, at most 2048 tokens per action, and six total root-plus-child actions.

The primary scientific question is whether the fixed policy yields at least two complete G4 groups
with both exact-correct and exact-incorrect outcomes, while preserving native root action token IDs,
per-token log probabilities, prompts, routing, and terminal evidence for a later root-only update.
Official MRCR similarity, first-program shape, stdout transport, and output-return behavior are
diagnostics.  There is no optimization, dynamic resampling, heldout claim, or teacher/gold content in
the model prompt.

## Exact terminal condition

The installed Qwen3 parser normally applies an outer `strip()` to final content, which removes
answer-significant trailing spaces from some frozen MRCR targets. This sidecar uses the separately
qualified, process-local `terminal-strip-disabled` hooks around the full collector/environment
serving scope. The hooks disable exactly the outer Qwen final-content strip and the successful ACP
root-reply outer strip. They do not change reasoning newline handling, tool parsing, or errors.

The collector retains the established trace outcome and also retains exact
native completion IDs, native log probabilities, full tokenizer decodes with and without special
tokens, and equality hashes. This is not a general lossless/whitespace-preserving parser and does
not repair a model response to match gold. Genuine extra linefeeds, punctuation, missing spaces,
and wrong content remain wrong. Shared renderer code and completed artifacts are not edited.
