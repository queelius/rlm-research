---
title: B05 eligible-IDs interface independent native audit
date: 2026-09-12
status: COMPLETE_RAW_AUDIT
---

# B05 eligible-IDs interface independent native audit

Both arms contain 24/24 paired child coordinates over four root contexts. The all-record
inert projection uses the fixed 64 eligible-ID denominator. Full-report precision/recall
is 0.9523809523809523 /
0.625; IDs-only precision/recall is
0.9565217391304348 /
0.6875. The IDs-only arm has
4 exact-set wins and
0 losses relative to the paired full-report arm.

Strict-valid-only metrics are separately labeled and use denominators
22 and
18; invalid outputs are not
silently credited as valid answers. Every saved prompt was independently re-rendered to
the exact native request, and response token IDs, chosen-token logprobs, usage, model,
provider ID, canonical response-content digest, and actual `ReportWorker` runtime marker
were checked. Integrity issues: 0.

The host lookup retains every claimed known ID, including ineligible IDs, and only supplies
deterministic effective metadata. It does not infer eligibility, repair the model's ID set,
or demonstrate model learning. The 32 downstream combinations are CPU host arithmetic,
not additional model calls or independent root problems.
