---
id: leaf-trec-query-conditioned-interface-v1-native-audit
status: complete
date: 2026-09-10
planned_endpoints: 192
available_endpoints: 192
null_endpoints: 0
---

# Query-conditioned TREC interface: native audit

## Result

The compact A/B/other interface did not preserve the c32 advantage seen with
full six-label output. All 192 calls authenticated, so these are observed
scores rather than availability bounds:

| model | interface | correct / 768 | exact 16-record batches / 48 |
|---|---:|---:|---:|
| base | full six | 672 (87.50%) | 4 |
| base | A/B/other | 605 (78.78%) | 1 |
| c32 | full six | 726 (94.53%) | 17 |
| c32 | A/B/other | 605 (78.78%) | 5 |

Thus c32 improved full-six output by 54/768 labels (+7.03 percentage
points), but improved A/B/other by 0/768. The difference-in-differences is
-54/768 (-7.03 points). At the eight correlated batch units it was negative
in six, zero in one, and positive in one; the batch deltas were
`[-13,-10,-8,-7,-24,0,-2,+10]` labels. Full-six c32-minus-base was positive
in all eight batches. A/B/other minus full-six was negative in all eight
batches for both base and c32.

The A/B/other arms still exceeded the constant-`other` reference of 512/768:
both scored 605/768. Their equal totals conceal different errors. Base got
A/B/other respectively 61/128, 44/128, and 500/512; c32 got 79/128,
64/128, and 462/512. The adapter shifted accuracy toward the requested pair
but away from `other`, leaving aggregate accuracy unchanged.

## Interpretation and limits

This does not support query-conditioned label projection as a replacement for
the full six-label child interface in this pilot. It also is not evidence that
query conditioning is generally harmful: the intervention bundles a smaller
output vocabulary, pair-specific instructions, and a changed decision task.
The 48 pair blocks share only eight official-test batches, the test panel is
research-exposed, and this is child classification rather than a root result.
A useful follow-up would first isolate whether projecting a completed six-label
map in ordinary code retains the full-interface gain; that requires no learned
A/B/other output contract.

## Native and operational closure

The independent reader re-rendered and matched all frozen bodies, then checked
model, unique choice, prompt and completion token identities, logprobs, usage,
finish route, and parsed content. All 192 responses were HTTP 200, choice
bearing, native-authenticated `stop` completions with 192 RESULT files and no
NULLs. Usage was fully known: 232,688 input tokens, 51,701 output tokens, and
148,192 cached input tokens. The owner completed and released cleanly in
204.022 seconds; its parent exited 0 without timeout in 204.643 seconds and
reported no GPU processes after exit.

The method and reader were frozen before outcome access. The same author built
the producer and this audit, so the recount is raw/native and reproducible but
not author-independent.
