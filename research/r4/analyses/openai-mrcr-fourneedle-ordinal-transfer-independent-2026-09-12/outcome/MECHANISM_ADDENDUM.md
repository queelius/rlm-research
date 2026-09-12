---
schema: openai-mrcr-fourneedle-mechanism-addendum-v1
created_utc: 2026-09-12T22:08:00Z
generated_programs_executed: false
---

# Checkpoint-32 residual failures

The six non-exact checkpoint-32 endpoints separate cleanly into three delivery
errors and three selection/termination errors. This inspection parses saved code
as inert text; it does not execute it or infer hidden reasoning.

## Clean retrieval, inexact terminal copy (3)

Coordinates `27b3cb6c…`, `5c0fde8d…`, and `965021c8…` each used an AST-parseable
program with the correct literal request and requested ordinal. The tool output
contained the target plus the ordinary `print` newline. In every case the final
reply equaled the host answer except that its final two ASCII spaces were absent
(length delta -2; full common prefix to the shorter reply). The terminal-strip-
disabled condition therefore did not invent or delete these bytes: the saved
native terminal itself omitted them. Raw exact is false, while the marker-gated
SequenceMatcher scores are 0.999073, 0.999320, and 0.999199. These are copy-
fidelity failures, not evidence of selecting the wrong occurrence.

## No clean target (3)

- `b3848ab4…`: the only root generation exhausted the 2,048-token action limit,
  produced no interpretable Python action and left an empty parsed reply. It is
  retained as `model_invalid_terminal`, not a retrieval attempt or native-integrity
  failure.
- `b66e01fd…` and `b781cdc5…`: each generated a complete exact-match loop and the
  requested ordinal, but changed the literal request noun from the public
  context's `email` to `message` in one case and from `email` to a different
  grammatical form in the other. Exact matching consequently found too few
  records; the tool raised the preserved "ordinal unavailable" error and the
  terminal paraphrased that error. These are literal selector/interface errors,
  not global ordinal-index arithmetic errors.

Thus checkpoint 32 has ten raw-exact endpoints, three correct selections followed
by two-byte delivery errors, two literal-query failures, and one pre-action length
exhaustion. The result extends the trained procedure to third/fourth requests in
this same task family, but it is not evidence of recursion or broad decomposition
generalization.
