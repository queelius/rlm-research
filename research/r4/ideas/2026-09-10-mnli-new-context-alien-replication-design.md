---
id: mnli-new-context-alien-replication-v1
status: proposed-design-only
written_utc: 2026-09-10T02:51:00Z
evidence_cutoff_utc: 2026-09-10T02:50:51Z
---

# Direct new-context requested-tag mechanism replication

## Question

On additional MNLI contexts, is assigning a record the ID of a *different visible record* more
damaging than assigning it an unrelated one-to-one alias? This directly repeats the three-arm
matching / visible shift17 / alien-ID contrast on new contexts. It is separate from the completed
matching-versus-constant breadth result (639/768 versus 398/768), because a repeated constant cannot
distinguish wrong visible-record binding from output-dictionary diversity.

## Smallest informative comparison

Use 16 additional 48-pair contexts, four each from government, slate, telephone and travel. Each
context has 16 premise groups and all three hypotheses per premise. Cross one paired sampling seed
per context with three exact-tag arms, for **48 calls and 768 displayed labels per arm**:

- `matching`: each requested_tag is that displayed record's public ID.
- `shift17`: requested_tag is the ID 17 displayed positions ahead, wrapping within the context.
- `alien`: a unique deterministic `m` + 12-hex alias at every position, absent from the bounded
  named visible-ID inventory and tokenizer-length matched to that position's shift17 tag.

All arms use identical displayed IDs/text/order, common final-only classification wording, label
enum, exact 48-position grammar, released cdbee Qwen3-4B without adapter, thinking off, no tools,
temperature 0.5 and one new paired seed. Alien length matching controls token count locally where
verified; it does not make strings semantically neutral or equalize FLOPs.

Select premise groups deterministically with master `981622001`, using normalized public text hashes
only. Exclude the old eight contexts and just-completed 16 contexts using their named DATA/PUBLIC and
exposure receipts before selection; do not filter on label, difficulty or outcome. Proposed sampling
seeds are `981622101 + context_index`, subject to a named-catalog collision check before freeze.
Hash-order contexts, then rotate the three arm orders. Since 16 is not divisible by three, first-arm
counts must be 6/5/5 rather than falsely described as equal; offset rotations across genres so no arm
is consistently early within every genre. Four workers run completion order uncontrolled.

## Metrics and causal boundary

Primary is strict displayed semantic correctness after whole-response contract admission: exactly 48
tag-then-label objects in displayed order with the exact requested tag at each position. An
authenticated malformed completion scores zero; missing or native-inconsistent transport is NULL
with [0,48] bounds. Also report native availability, whole-contract validity, tag fidelity,
shape-only positional semantics, finish branches, and 16 paired context contrasts.

For shift17 only, precompute displayed-label versus requested-record-label agreement on positions
where those frozen gold labels differ. Report displayed/named/third counts as a diagnostic. Do not
invent gold for alien aliases, reorder predictions, repair tags, or execute tool output. The key
contrast is alien minus shift17; matching anchors the size of correspondence benefit. One seed and
16 clusters remain exploratory breadth evidence, not confirmation or item-level independent data.

## Feasibility and gate

A read-only scan completed at 2026-09-10 02:50:51 UTC against the named current MNLI DATA/PUBLIC
inventory. After excluding normalized text from the old eight and completed new 16 contexts, complete
three-hypothesis premise groups remaining were government 517, slate 529, telephone 536 and travel
547; no conflicting-label pair groups were found. The deterministic proposal selected 256 premise
groups. It generated 768 unique alien aliases with zero bounded visible-ID collisions and no
token-length matching failures. Approximate verbatim-current-role prefixes were 3,464--4,325 tokens;
maximum plus 3,072 output was 7,397 < 8,192. Implementation must reconstruct and pin the exact final
wires/token IDs rather than treating this design-time estimate as an input receipt.

Reuse the already qualified exact-tag owner/service/native authenticator and 4-worker transport in a
new immutable sidecar. A conservative envelope is 1,200 seconds outer, 1,080 work, 1,170 owned,
including 180 startup, 90 seconds/request, 90 cleanup and 30 margin. Preserve all 48 planned NULL
rows, native requests/responses/token IDs/usage and actual costs; no retry or reroll. Promotion requires
all source/collision/token checks and a clean actual owner-to-collector/service CPU fixture. If the
deterministic frozen selection overflows 8,192 after exact rendering, reject the preparation rather
than outcome-blindly substituting contexts.

This file is design only. No sidecar, service, queue entry or GPU launch is authorized yet.
