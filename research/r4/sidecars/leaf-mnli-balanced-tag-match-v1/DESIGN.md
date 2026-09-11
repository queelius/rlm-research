# Balanced input/output tag-set match: frozen design

This 192-call leaf-only experiment asks whether the late-position benefit of a unique opaque
correspondence key depends on using the same key set in the input and output. It uses the exact 16
previously selected MultiNLI contexts and crosses three public-ID/reference conditions with four
tag cells: A input/A output, A/B, B/A, and B/B. Both opaque sets are fixed independently for each
context from master seed `998477001`; they are mutually disjoint and do not equal any public,
shifted, or alien record ID. All four paired cells use seed `998477101 + context_index`.

Every prompt says that output position *i* labels displayed object *i*. `input_tag` and
`answer_tag` are opaque bookkeeping and neither refers to another record. The grammar requires the
48 answer tags in output order. The primary estimand is late-position accuracy
`mean(AA, BB) - mean(AB, BA)`, pooled over the three reference conditions but retaining all 16
contexts as clustered units. Relation-specific effects, availability, contract validity, total and
late accuracy, and intended-position versus visible-named-record accuracy are reported separately.
The fixed exploratory promotion screen is at least 10 percentage points, positive context-level
effects in at least 12/16 contexts, and at least 15/16 available calls in every cell.

This comparison changes an encoding package, not one isolated mechanism. Structured decoding
forces every `answer_tag`, so tag fidelity cannot show that the model freely copied or retrieved a
key. A match effect could reflect token repetition, prompt regularity, attention, or another use of
the shared string. A null effect would only show that exact input/output tag identity is unnecessary
under this display-order grammar; it would not show that keys never matter. The fixed contexts are
research-exposed and eligibility originally used gold labels to form complete three-label groups.
This is neither new-corpus evidence nor an independent training replication.

The model is released base Qwen3-4B-Instruct-2507 revision
`cdbee75f17c01a7cc42f958dc650907174af0554`, with no adapter or training. MAIN may later allocate one
A100. The immutable cap is 1,800 seconds outer / 1,770 owned / 1,650 work, four workers, 90 seconds
per request, maximum 3,072 output tokens, no retries, no repairs, and all unavailable endpoints
retained as NULL. No sampled model code is executed.
