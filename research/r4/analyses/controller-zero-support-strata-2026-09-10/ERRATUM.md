---
title: Erratum to controller zero-support strata audit
date: 2026-09-10
status: additive clarification
applies_to: REPORT.md
---

# Evidentiary relationship

The phrase “three independent comparisons” in `REPORT.md` is incorrect. It should read
“three related readouts of one trained checkpoint on the same source contexts.” The original,
fresh-seed, and metadata evaluations are not independent training replications or independent
context replications. Their separate strata are retained, but they must not be pooled or interpreted
as three independent confirmations.

# Existing-note caveat retrieval

The 13 zero-gold caveats listed in `RESULTS.json` are a non-exhaustive marker-based retrieval from
the already-frozen source annotations. They are examples of existing notes that explicitly mention
coincidence, unsupported finals, or empty-set behavior. They are not the result of a systematic new
semantic review and must not be treated as a complete inventory of all possible empty-support
failure modes.

This erratum changes no row, metric, count, NULL treatment, or source annotation. The previously
sealed artifacts remain unchanged.
