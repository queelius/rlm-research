# Independent state-representation outcome audit

Run the sealed command once after the representation owner terminal exists. The analyzer performs no
polling and no model calls. It independently regenerates all public roots and three prompts, validates
each native request, tokenizer prefix, response decode, model alias, usage, grade, and qualified
runtime receipt, then reports raw-to-unresolved, unresolved-to-resolved, and raw-to-resolved pairs.

Missing or unqualified terminals produce `PENDING.json` or `HOLD.json`; unknown calls are never scored
as wrong. Token lengths and explanatory wording are intentionally unmatched across representations.
