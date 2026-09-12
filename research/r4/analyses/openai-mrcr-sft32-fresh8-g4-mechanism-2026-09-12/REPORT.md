# Fresh8 G4: two different bottlenecks, not a paired checkpoint regression

Independent proven-core replay reproduces **7/32 raw exact,32/32 available**,66 returned root actions, zero child actions and no native errors. Owner completed/released in404.602s. Fixed cp32, T0.5, terminal-strip-disabled and saved model binding are authenticated; every native action is re-parsed and mapped against the saved initial prefixes. All8 fresh source-row hashes are disjoint from the32-example teacher corpus.

The earlier8 trained contexts had28/32 exact,32 clean target stdout and zero mixed groups. Fresh8 uses different contexts **and** a different seed block: the28→7 difference is descriptive, not a paired model regression or32 independent task observations.

| Fresh context | G4 raw reward vector | First target stdout | Mechanism |
|---|---|---:|---|
| Poem/planning, ordinal2 | 0000 | 4/4 | Correct print; finals add1 or2 terminal newlines. |
| Formal letter/numbers, ordinal2 | 0100 | 4/4 | Three finals add one terminal newline. |
| Email/candy, ordinal1 | 0000 | 0/4 | Guesses “message,” “short email,” or “story”; source says literally “write a email about candy.” Two retries change ordinal bookkeeping without correcting the selector. One then fabricates a story after empty stdout. |
| Email/style, ordinal1 | 0000 | 0/4 | All use “write an email about style”; actual source says “write a email about style.” No matches, not an unavailable requested ordinal. |
| Play scene/manners, ordinal2 | 1111 | 4/4 | Correct retrieval and exact final. |
| Formal letter/stores, ordinal2 | 0001 | 4/4 | Three finals omit two genuine trailing spaces. |
| Song/planes, ordinal1 | 0010 | 4/4 | One final omits two trailing spaces; two add terminal newline(s). |
| Poem/shoulders, ordinal1 | 0000 | 4/4 | All omit two genuine trailing spaces. |

**24/32 first tool observations equal full gold plus the single newline introduced by print.** Those yield7 exact finals and17 copy failures:9 add terminal newline(s),8 delete two trailing spaces. These differences are present in the native parsed finals under the scoped no-terminal-strip condition, not retroactive normalization opportunities. All scores remain frozen. Both email contexts supply the requested first response; selector wording, not ordinal indexing or source absence, causes their8 failures.

Every first program matches the trained AST after masking only `request_text`, `ordinal` and `marker` assignments. Full per-record teacher AST equality is **not applicable** to these fresh rows, rather than a failure. The learned role filter, immediate-assistant-successor rule and ordinal selection remain structurally intact. Email and song each have zero examples in the32-teacher corpus; song nevertheless retrieves4/4. Poem7, letter4 and scene5 examples were present. Only the numbers topic appears among those32 teachers. These measured overlaps do not prove an abstract “familiarity” cause.

There are3 mixed groups, all with identical first native path and clean target stdout across the group: numbers letter, stores letter and planes song. Thus the observed within-group contrast is terminal-copy contrast. Both failed email groups have uniform zero reward, providing no G4 binary contrast for correcting the selector. This is evidence for a bounded final-return objective comparison, not automatic all-root training admission or proof that a last tool action is a text final.

The strongest next harness question is whether one generic instruction induces **actual literal-input inspection before exact matching**, preventing guessed request strings. See NEXT_COMPARISON.md. It does not solve the distinct trailing-whitespace bottleneck and should be judged on that distinction.

[REPORT.json](REPORT.json) SHA256 `e8b0ae49b29415130e990d62cface02ab9d330b0b983d5b9db504c683d913f19`. [EVIDENCE.json](../../../../ARTIFACTS.md) retains all32 programs, actual source request strings, tool observations, finals and exact string-difference operators. The report pins source code, READY, checkpoint binding, gold, contexts, prefixes and all native/episode evidence. Only AST parsing and inert string comparisons were performed; no generated program, GPU call or optimizer was executed.
