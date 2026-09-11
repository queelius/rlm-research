# Pre-output V2 validity correction

V1 READY SHA-256 `d4419c04b00b0613bd8351368ac414349cf4b40a5c035bba411cb294b0c4fd51`
was sealed but never launched. It accidentally omitted the inherited `requested_tag` field, making
wrong, alien, and aligned visible-ID conditions inert renamings. V2 restores the original rotated-by-
17 public `requested_tag` at every displayed position and states that it is an opaque output address;
display order remains the task-authoritative correspondence. No model outputs existed when this
correction was made.

The three conditions now have their intended meaning. In `wrong`, visible `id` is the source ID while
`requested_tag` names another displayed record. In `aligned`, visible `id` equals `requested_tag` and
names the current displayed record. In `alien`, the visible IDs are outside the requested public-ID
set. The diagnostic constructs `visible id -> gold of the record displayed with that id`, then looks
up each `requested_tag`. It is 48/48 for a perfectly intended-position prediction in aligned,
potentially divergent in wrong, and unavailable in alien. It never changes primary scoring.

The exact 16 contexts, A/B tags, master seed, paired sampling seeds, 192 calls, primary contrast,
promotion screen, model, and compute cap are unchanged. Cell dispatch order is rotated by context
index, so each of AA, AB, BA, and BB appears equally often in every within-relation dispatch
position. This only counterbalances service-order exposure; the four calls remain correlated within
context. All V1 bytes remain preserved as an explicitly superseded, unlaunched preparation.
