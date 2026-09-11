---
id: question-sensitive-sft-semantics-000-053
status: complete_manual_slice
date: 2026-09-10
indices: 0-53
available_reviewed: 37
---

# Manual semantic review, inventory indices 0–53

I manually read every available endpoint in this disjoint inventory slice: the sampled programs, parent/tool-ID-linked observations, requested operator/category/scope/threshold, and authenticated final. I did not execute sampled code or assign fidelity with a keyword rule. Seventeen unavailable slots remain operational NULL and have no semantic classification.

Of 37 available endpoints, 36 made at least one real child acquisition and 35 had a complete observed map available for reduction. Sixteen executed a faithful requested operation; ten of those were strict successes and six were faithful computations whose observed child labels produced the wrong answer. Twenty endpoints were strict successes overall, but ten did not implement the requested operation. These include sum-for-maximum and sum-for-threshold coincidences, malformed conditional logic, and zero-answer coincidences.

The sharpest counterexamples are index36, which acquired all16 records across eight child calls but overwrote each prior two-record map and never displayed a successful scalar before returning the coincidentally correct zero, and index25, whose `context.txt` parse failed before any child dispatch and ultimately returned the sum of all scoped weights. Conversely, several strict errors are mechanistically useful: indices10,11,13,14,17,35 faithfully apply the requested operation to an observed child map, so their wrong finals are attributable to the acquired labels rather than an operator substitution.

This slice mixes unchanged dev/protected and SFT6 dev according to the frozen inventory order. It is not an independent sample or a complete policy comparison; MAIN owns indices54–159. The row-level JSON is authoritative for this slice.
