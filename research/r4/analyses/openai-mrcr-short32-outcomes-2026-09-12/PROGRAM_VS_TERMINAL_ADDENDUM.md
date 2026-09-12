---
schema: mrcr_short32_program_vs_terminal_interpretation_v1
date: 2026-09-12
status: posthoc_mechanism_audit_not_new_model_result
scope: all_four_raw_similarity_at_least_0_90_outputs
new_model_calls: 0
---

# Finding the passage is not the same as writing a correct search program

The earlier audit correctly identified four final answers that contained the
requested passage with newline-copy errors. A closer reading changes what we can
say about the *procedure*: none demonstrates a correct Python extraction routine.

In all four attempts, the model printed the conversation data broadly into its
own observation. Those observations were 18,683–20,000 characters long. Three
carried truncation warnings, but the complete requested passage was still present
in an escaped representation. The final language-model response selected that
passage and reproduced the escaped line breaks. There were no child-model calls.

The attempted Python extraction did something else. Three attempts selected a
user's request rather than the requested assistant answer. The fourth raised an
exception after printing the data, before completing its intended extraction.
Thus the final model response recovered from incorrect code by reading a broad
observation. This is useful behavior, but it is not successful programmatic
decomposition or reliable selection of the answer into a Python variable.

MAIN read the generated tool code and the actual returned observations without
executing that code. The accompanying JSON pins all four original episodes and
checks that a complete representation of the target passage occurs in the tool
output. It assigns no repaired scores and no hypothetical direct-return successes.

## Consequences for the current experiments

The queued shaped-reward RL update remains an informative exploratory test, but
its positive examples can reward broad context printing followed by direct
reading. An improvement in final answers must therefore be accompanied by a
procedure and observation-size audit before claiming improved decomposition.
All frozen training rewards, examples and evaluation choices remain unchanged.

The procedural demonstrations target a different behavior: select the matching
user/assistant pair in Python and print only the requested answer. Compare actual
behavior, not just the final similarity score, when those trained models finish.

A future small comparison could constrain observation size or expose a compact
structural preview, asking whether the model learns to inspect and select instead
of dumping the context. Such a constraint could also hide necessary evidence, so
it needs a paired accuracy-and-cost test, not an assumed benefit.

An exact program-result return channel is another useful control, but it cannot
automatically fix these four programs: their selected values were wrong or never
produced. The repository's core engine already supports `FINAL_TEXT` and
`FINAL_RESPONSE`; the current nano-based experimental harness requires a final
model reply. Adapting an existing return channel is not a novel RLM invention.
We should establish correct program selection before crediting gains to better
answer transport.

Evidence: `PROGRAM_VS_TERMINAL_ADDENDUM.json`, reproduced by
`audit_observation_transport.py`. This is a refinement of `SIGNAL_ADDENDUM.md`,
not a replacement for the original raw-string scoring.
