# Exact requested-tag alien control (MNLI48)

Question: is a wrong visible-record referent more damaging than an unrelated requested alias? Eight
already exposed MNLI48 contexts, two fresh paired seeds, and three arms produce 48 calls. Matching
uses the displayed record ID; shift17 uses another visible record's ID; alien uses a deterministic
one-to-one dictionary absent from the bounded collision inventory. Alien IDs match the shifted ID's
per-position tokenizer length where feasible and retain `m`+12-hex form, but are neither globally
unseen nor semantically neutral, and token-length equality is not FLOP equality.

Every arm shares displayed records/order, classification/requested-tag wording, exact per-position
tag grammar, three free label choices, released Qwen3-4B, final-only role, no tools and paired
sampling seed. Primary is full-contract-gated displayed-label correctness on 768 items/arm. A
completed malformed response scores zero; missing/unverified transport is NULL with bounds. The
displayed/requested-named/third diagnostic applies only to valid shift17 unequal-gold positions; no
alien gold is invented. Preserve request/native IDs, usage, order and all 48 planned NULL rows; no
repair, reroll, tool execution or source acquisition.

The panel is repeated/exposed and adaptive, not fresh-source replication. The isolated sidecar reuses
the qualified exact-tag owner/service/collector through pinned adapters. Envelope: 1200 outer,
1080 work,1170 owned,180 startup,90 cleanup,30 margin; four workers,90 seconds/request,3072 output.
MAIN alone owns GPU/service/queue actions.
