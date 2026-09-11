---
status: additive_interpretation_correction
date: 2026-09-10
study: root-question-sensitive-seed-replication-v1
changes_scores: false
---

# Timing and fidelity-comparability correction

This note preserves the sealed report (`b7670575…`) and semantic table
(`0676e3f3…`) without changing any row judgment or score.

First, the report's sentence “The qualified native method predates execution”
is ambiguous and should not be read as saying that the new follow-up wrapper was
preregistered. The underlying qualified QS native/admission kernel came from the
earlier campaign. This follow-up launched at epoch `1789061136.0910366`
(17:25:36 UTC), its parent recorded terminal exit at `1789062779.10067`, and
`METHOD.md`/`readout_audit.py` were written at filesystem epoch `1789062830`
(about 51 seconds after terminal), before the follow-up audit file and before
the analyst read outcomes. Thus the follow-up method was post-execution but
pre-outcome-read, not prospectively frozen before execution. The subsequent
manual semantic review was outcome-available and is disclosed as such.

Second, the fresh audit's broad `faithful` field includes three unchanged-policy
paths (indices 90, 92, and 124) that sampled an appropriate reduction expression
but never successfully executed it on retained state. This is broader than the
original audit's “requested calculation actually performed” metric. Applying
the original performed-and-grounded definition gives:

| Protected panel | Original seed | Fresh seed |
| --- | ---: | ---: |
| Unchanged calculation performed | 18/64 observed | 19/62 observed |
| SFT6 calculation performed | 62/71 observed | 60/70 observed |
| Unchanged performed and strict | 15/64 observed | 15/62 observed |
| SFT6 performed and strict | 52/71 observed | 49/70 observed |

Therefore index 92 does **not** change the criterion's substantive
comparability: the fresh-seed contrast is 19→60 for actual performance and
15→49 for performed-and-strict, compared with the original 18→62 and 15→52.
The broader fresh counts 22→60 remain useful only as sampled-expression
diagnostics. NULLs remain unknown; denominators above are observed endpoints,
and planned-denominator counts are respectively 19→60 and 15→49 out of 72.
