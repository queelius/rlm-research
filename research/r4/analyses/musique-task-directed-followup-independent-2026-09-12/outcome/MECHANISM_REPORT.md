---
schema: musique-task-directed-followup-independent-mechanism-report-v1
scope: completed-attempt003-12-contexts
gpu_queries: 0
generated_code_executed: false
---

# MuSiQue targeted follow-up mechanism note

All 132 saved prompts re-render byte-for-token to the physical native requests with the pinned
Qwen3 tokenizer, `add_generation_prompt=true`, and `enable_thinking=false`: 132/132 exact token-ID
matches and no violations. This closes the prompt-to-wire provenance gap; it does not prove that an
answer used its cited evidence faithfully.

Targeting did not change exact answer outcomes relative to stop or broad: all three were 1/12.
Targeted answer-F1 was somewhat higher (sum 1.505 versus 1.229 broad and 1.227 stop), but support-F1
was not (5.600 versus 5.922 broad and 5.383 stop). Broad extra reports contained the exact gold
string in 7/12 contexts, compared with 3/12 targeted contexts. This lexical check is not a
faithfulness measure. Full-source reached 3/12 exact and supplies a useful boundary: fragmented
report acquisition, not simply insufficient source text, was often limiting.

Five trace-grounded mechanisms stand out:

- One focused branch acquired the player-to-team relation and exact year, but the final returned a
  verbose sentence instead of the concise answer and omitted the player-link support paragraph.
  This is useful evidence followed by answer-format and support-selection failure.
- On a landmark question, both broad and targeted additions contained the exact requested entity;
  the targeted final nevertheless denied it and cited a broad six-paragraph set. Evidence was
  acquired and then contradicted during aggregation.
- On the Narrow Island question, the initial left report contained the island link and the right
  report contained the conference link. The planner sent the conference follow-up to the left half
  and the island follow-up to the right half. Both returned “missing”; the targeted final selected
  the exact support set but answered incorrectly, while full-source was exact. The focused questions
  were relevant but routed to the wrong evidence partitions.
- On the composer-spouse question, all split-report finals selected the exact support set yet said
  the death city was unavailable; full-source was exact. Correct support IDs did not preserve the
  cross-report answer relation.
- On the Nevada question, a broad report explicitly introduced an outside historical guess after
  noting that it was absent from the supplied paragraphs, and the final chose that guess. The stop
  arm had the exact support set but no answer. This is an unsupported-answer failure, distinct from
  support selection.

The screen therefore does not support learned routing or a benefit from targeted follow-ups. A
small next architectural comparison should address report composition and partition-aware routing,
not merely add more calls: retain the two original halves but show the planner which report came
from which half and require it to route each focused question to the opposite half only when the
missing relation is evidenced there. That would need a fresh prespecified panel; it should not be
inferred as successful from these post-hoc examples.

Exact aggregate values, artifact hashes, call IDs, and claim limits are in
`MECHANISM_EVIDENCE.json`; raw public task content is not reproduced here.

