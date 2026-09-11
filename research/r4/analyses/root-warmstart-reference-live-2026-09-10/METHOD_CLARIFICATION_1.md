# Prospective method clarification 1

Frozen `2026-09-10T00:26:16Z`, while MAIN confirmed that neither reference24 science outputs nor the
new training study had started.

The primary-estimand paragraph in `METHOD.md` incorrectly grouped a “tool-routed final” with
completed malformed finals scored zero. The native-authentication paragraph, frozen parser, and
study collector have the intended rule: a completed, authenticated native final that is wrong,
malformed, or empty is an observed zero; an unfinished tool branch or incomplete tool envelope has
no authenticated native final and is NULL. Raw route evidence remains retained. This clarification
changes no code, input, denominator, score, or outcome-dependent choice.
