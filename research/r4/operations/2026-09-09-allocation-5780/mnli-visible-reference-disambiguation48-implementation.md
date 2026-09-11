# MNLI visible-reference disambiguation48 CPU handoff

Status: CPU READY for MAIN review; never GPU-launched by author.

Sidecar: `sidecars/leaf-mnli-visible-reference-disambiguation-v1`. Additive `READY_v2.json`
SHA-256 `afc0acd650166af799c9bc826040af855c995a666378381b6229e4c67ae49904`, identity
`c9c156a0373406e3fcd095075e920542365ec93511dd30079de21355cb2fb10f`.

The draft eight contexts remain byte-identical (`DATA.json` `e4ee7809…`, selection receipt
`202997ba…`). V2 adds aligned/legacy and freezes the full relation3 × wording2 grid:48 calls,
one paired seed/context, deterministic six-arm rotations with first-position counts1/1/1/1/2/2.
Wrong is left17; alien visible IDs are unique, named-inventory collision-free and per-position
token-length matched; aligned visible IDs equal the local requested slots. Text, requested tags,
gold, schema and seed are invariant within block.

Legacy is the exact predecessor wording. Explicit naturally defines `requested_tag` as an opaque
output address and same-object classification. No filler was added. Explicit prefixes are exactly
eight tokens longer per context; the frozen natural prompt token sets are legacy
3494/3623/3748/3818/3824/3855/4072/4088 and explicit
3502/3631/3756/3826/3832/3863/4080/4096. All plus3072 output fit8192. The wording simple effect is
instruction-sensitive, not proof of ambiguity; interaction is descriptive and eight-context
closeness is not equivalence.

Focused qualification:13 tests passed in6.156s (`CPU_TESTS_v2.json` SHA `700f41b3…`). It includes
the actual48 frozen HTTP wires with one corrupt-native-prefix and one HTTP500 NULL, exact grammar
and displayed/named/third scoring, collision/selection checks, owner clock/namespace execution, and
an intercepted full service entry reaching the qualified launcher. Fresh standalone
`owner_v2.py verify` returned the exact identity.

Key pins: protocol `c82b2506…`, scoring `589b4c14…`, collector `078235a8…`, owner `9f513f35…`,
service wrapper `43e50208…`, plan `521ef511…`, requests `f987ae00…`, collision receipt
`e995fede…`, native receipt `faa3afec…`, planned NULL inventory `a87ebede…`.

Envelope: one released Qwen3-4B base, no adapter/tools/thinking; exact requested-tag decoder;
four workers,90s request, outer1440/work1320/owned1410/startup180/cleanup90/margin30. Attempt namespace
is exactly `outputs/attempt-001`; no rerolls. MAIN owns acceptance and launch.
