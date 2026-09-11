---
date: 2026-09-10
status: additive_correction
---

# Semantic review authorship correction

`semantic_review.py` incorrectly describes its explicit path judgments as
“human-reviewed.” They were authored by an AI agent after reading the actual sampled programs
and tool observations, not by a human or an independent blinded reviewer.
The artifact remains an agent-authored manual path review requiring MAIN verification before
adoption. No row judgment, count, source evidence, or NULL treatment is changed by this erratum.
