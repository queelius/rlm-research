---
title: B05 clarified-contract source-visible native audit
date: 2026-09-12
status: AUDIT_WITH_INTEGRITY_ISSUES
---

# B05 clarified-contract source-visible native audit

All 64/64 coordinates are accounted for; 56 made physical calls and 8 were explicitly dependency-unsupported. The additive audit found 56 source-to-wire or runtime integrity issues.

Child eligible-ID micro precision is 0.9473684210526315 (36/38); micro recall is 0.6206896551724138 (36/58). Among matched IDs, metadata is exact for 4 and wrong for 32. ID-set recovery and row metadata correctness are intentionally reported separately.

The actual engine log does contain the ReportWorker injection marker; the saved config alone is not treated as runtime proof. The dispatch receipt, engine command, launcher hash, and owner receipt link are authenticated separately.

Root correctness is graded against the true source. Consistency with displayed reports is secondary because complete source tables remain visible. Unsupported combinations are retained, and the nondeployable oracle condition is not pooled with model-generated reports.
