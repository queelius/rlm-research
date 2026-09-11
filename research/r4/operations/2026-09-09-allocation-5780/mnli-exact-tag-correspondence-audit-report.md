# Exact-tag MNLI correspondence audit

Independent native/source rescoring confirms the producer totals with no disagreements: matching
622/768 (81.0%) versus shift17 280/768 (36.5%), with all 32 endpoints authenticated and all 32 whole
contracts valid. On all 522 predeclared unequal-gold shifted positions, predictions followed the
requested-named record 373 times (71.5%), the displayed record 80 (15.3%), and the third label 69
(13.2%). On the 246 equal-gold shifted positions, 200 were correct (81.3%).

The matching advantage appears in all eight exposed context clusters. Because the exact decoder
forced the same diverse tag multiset in both arms, this is evidence for semantic redirection by the
requested ID under a constrained decoder, not merely an output-diversity or malformed-output effect.
It does not establish free ID emission, internal attention, or new-context generalization.

This independent parser was written after outputs existed and after MAIN disclosed aggregate totals;
runtime_port's existing method remains the pre-generation specification. The auditor authored the
generic shifted predecessor and original MNLI data preparation, not this exact-tag implementation.
Full qualifications are in `analyses/leaf-mnli-exact-tag-correspondence-live-2026-09-10/REPORT.md`.
