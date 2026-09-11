# Native availability erratum

The initial operational inventory message described the 22 owner-labeled `native_final` rows as
available and the 16 `attempted_native_no_final` rows as NULL. Qualified native authentication then
established that all 16 latter episodes contain authenticated empty terminal finals. Under the frozen
rule, empty authenticated finals are observed incorrect. The authoritative totals are therefore 38
authenticated observed paths (9 strict correct, 29 strict wrong, including 16 empty) and 26 NULL
timeouts. `REPORT.md`, `FAILURE_NATIVE_AUDIT.json`, `SEMANTIC_AUDIT.json`, and `FINAL.json` all use the
corrected totals; the earlier 22/42 operational message is superseded.
