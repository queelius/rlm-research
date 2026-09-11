---
status: prospective_frozen_before_outcomes
date: 2026-09-10
study: leaf-mnli-stable-anchor-qwen8b-v1
run: outputs/attempt-001
planned_endpoints: 144
contexts: 16
relations: 3
arms: 3
---

# Prospective independent Qwen3-8B stable-anchor audit

Do not inspect the output tree until MAIN supplies the exact `OWNER_TERMINAL.json` and exact parent
`EXIT.json`. Before scientific reads, require the owner hash, complete/released state, no owner
error or unreleased service, parent exit zero, no timeout, empty post-exit GPU inventory, and an
EXIT completion marker exactly equal to the owner-terminal hash. A clean process exit alone is not
evidence that all 144 endpoints were observed.

The fixed inventory is exactly 16 contexts × three reference relations (`wrong`, `alien`,
`aligned`) × three arms (`labels_only`, `sequential_numeric`, `opaque`) = 144 endpoints. The reader
must reject inherited four-arm or 192-row assumptions: there is no `permuted_numeric` arm in this
study. For every coordinate, authenticate its plan ID, source 4B coordinate, context, relation,
anchor, seed, dispatch order, serialized request body, structured-output grammar, expected native
prompt-token IDs, model alias, and unique provider request ID.

Authenticate the released unadapted Qwen3-8B binding at revision
`b968826d9c46dd6066d109eabc6255188de91218`, local manifest SHA-256
`2d7abf2289f2067ee55f3629430e619de4718e0a8decd454af7f26448ffaa2f4`, and alias
`qwen3-8b-stable-anchor`. Require no adapter and `enable_thinking=false`. Recount native request and
completion token IDs, HTTP status, decoded message identity, finish branch, and usage. Missing
usage remains unknown; billing is not inferred. There are no shared calls or shared costs within
the new 8B run.

Independently parse the complete 48-record response contract and score labels in displayed-record
order against frozen host gold. An authenticated returned empty, malformed, incomplete, wrong-key,
wrong-route, or otherwise contract-invalid answer is observed and known wrong with early, late,
and strict scores zero. An undispatched, unreturned, non-200, or unauthenticated endpoint is NULL,
never silently converted to zero. Report planned, attempted, returned, native-authenticated,
available, contract-valid, observed-invalid, and NULL counts, plus known/unknown input, output, and
cached-token usage.

Report all nine relation-by-anchor cells, the three anchor summaries pooled across relations, and
all 16 context clusters. Within 8B, primary contrasts are `opaque - labels_only` and
`sequential_numeric - labels_only`; also report `opaque - sequential_numeric`. For each contrast,
give paired-known wins/losses/ties and label accuracy, plus planned-denominator worst/best
missing-outcome bounds. These are identification bounds, not confidence intervals. Context is the
paired unit; calls and 48 labels within a context are dependent.

Apply the prospective decision rule only to within-8B contrasts: promote a fresh-context 8B
replication if both stable-key forms beat labels-only on the context-paired estimate without an
availability loss and each direction is positive in at least 12 of 16 contexts. Report every gate
component rather than only the Boolean decision. The panel is research-exposed and is not a fresh
context replication; promotion means that such a replication is warranted, not that it has
already occurred.

After the within-8B analysis is sealed, join the authenticated 4B endpoints on the exact source
coordinate to show the same three arms descriptively. Report model-by-anchor differences and the
change in each paired anchor effect, with availability and missingness retained separately. This is
not a pure capacity claim: weights, tokenizer, rendered tokenization, and the 8B model binding all
change. The earlier 4B calls and costs are reused, never rerun or attributed to this 8B study.

The audit reader may reuse the previously frozen stable-anchor parser/authentication implementation,
but must define `ARMS = ("labels_only", "sequential_numeric", "opaque")`, set the planned late-label
denominator to `16 * 3 * 32`, remove permuted-arm gates and pooled-permuted summaries, load the 8B
model/tokenizer from this study's sealed manifest, and require exactly 144 unique coordinates and
provider identities.

## Prospective source pins

- `DESIGN.md`: `e257565351873500f8be02158776da9bc74598f246878487edadbb7adf07c17b`
- `PLAN.json`: `fd8285236d80c66870900c84482ffce16704f4765dcaa3e4be4aa9ffbc9fa1a1`
- `REQUESTS.json`: `22ad4289f1262ea7985f558913d562bef49bbf6149d9d2d23a62e783f6401a9d`
- `PROMPT_IDS.json`: `5c85b9ec4e026b3190f8454cc40839341fbe4aa5d6792d657938078f6702c9d7`
- `DATA.json`: `59e27ccc4a1f58b280e3cad1481df6c0a58547bd61cee0c2fcf7d53ea8eed03e`
- `MODEL_PROVENANCE.json`: `826a350a731a6b7d71ab2bc20a9650c9118292f5e42d0f4a93699236bfb600bb`
- `WEIGHTS.json`: `8825b8bec00e9a0e7ca6e74de6e80db9013e4993c1342eca9eada7e4691a252f`

These are pre-READY preparation pins. The terminal auditor must additionally bind the final
producer `READY.json`, its complete source/input closure, and the final prospective reader seal
before accepting outcomes.
