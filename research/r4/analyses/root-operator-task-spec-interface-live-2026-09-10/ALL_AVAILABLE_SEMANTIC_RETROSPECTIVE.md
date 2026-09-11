# Additive semantic retrospective: all available interface72 finals

This post-outcome audit extends the sealed report's review from the ten strict successes to **all 48 available native finals**. It does not change terminal scores, availability, NULLs, or the original seal.

All 48 available trajectories made at least one actual child call (72 child calls total), so absence of operator faithfulness was not simply absence of acquisition. I manually inspected the executed final-branch programs against the exact requested operation:

- maximum-weight: per-user target-weight sums followed by a maximum;
- threshold-users: per-user target-weight sums, strict `>5`, then count qualifying users;
- conditional-weight: derive users having category A, then sum category-B weights for those users.

Result: **0/48** available finals faithfully executed the requested operator and scope. This comprises 0/17 maximum, 0/15 threshold, and 0/16 conditional endpoints. Consequently there were also 0 faithful-but-wrong-label outcomes; the earlier 0/10 strict-success finding was not hiding correct operator execution among scalar failures.

The failure patterns were consistent. Maximum programs generally summed all predicted target weights; the sole `max(...)` trace used a shadowed variable and assigned the same all-record total to each user. Threshold programs used global sums, one global Boolean, record-level `>5`, or broken aggregation, rather than counting users whose totals passed the threshold. Conditional programs summed one predicted category over fixed, invented, or all users rather than deriving the category-A user set.

This strengthens the mechanism conclusion for observed available trajectories: optional `task.txt`/`task.json` files were never read, and the natural-language question did not elicit the exact operation either. It still does not establish what would happen if structured parameters were actually made reachable and used.

The smallest targeted follow-up is a direct-rendered **parameter control** that keeps the same question/context while surfacing the exact operator, categories, scope, and threshold in an unavoidable message field. The current separate card48 study combines an explicit algorithm instruction with a context/different-question manipulation, so it should not be described as a pure test of mere parameter exposure.

Machine-readable evidence is in `ALL_AVAILABLE_SEMANTIC_RETROSPECTIVE.json`: all 48 endpoint IDs, program hashes, rules, and judgments. Sampled code was not reexecuted and host gold was not inserted.

