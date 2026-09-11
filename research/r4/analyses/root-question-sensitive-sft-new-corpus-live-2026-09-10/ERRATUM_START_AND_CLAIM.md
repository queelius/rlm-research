---
title: Erratum — starting policy and replication language
status: additive correction to sealed report
date: 2026-09-11
---

`REPORT_RECOVERY_V2.md` incorrectly calls the comparator a “released starting policy/model.” The shared start is **the already-trained fixed24 adapter**, SHA-256 `94022838a64a530e1abc8daf6cd43502d8aec7d549b6bfec10dd4928b0ca9006`, not untouched released Qwen3-4B. All occurrences of “released starting policy/model” should be read as “shared fixed24 starting adapter.”

The report's phrase “reliably move” is also too strong. Replace it with: **“The same six-update recipe produced bounded replication evidence across two separately captured 72-example training corpora on one shared, research-exposed eight-context evaluation panel.”** This is two corpus realizations, not two independent evaluation replications.

The directly comparable semantic result is:

- shared fixed24 start: 12/72 faithful-and-strict, with 17 NULLs;
- original-corpus QS6: 50/72 faithful-and-strict, with 0 NULLs;
- new-corpus QS6: 55/72 faithful-and-strict observed, with 2 NULLs, hence bounds 55–57/72.

Here, **strict** means the authenticated final integer exactly equals host gold, whether or not the model used the requested computation. **Faithful-and-strict** additionally requires that the requested operator, category, user scope, and threshold executed successfully on the returned child-label map and that the final used that computed scalar. This matches the sealed original-corpus semantic method. The new-corpus all-path review verified final/displayed-scalar use, including index 29's two-line observation; no sampled code was reexecuted.

The strict-only values remain fixed24 17/72 (17 NULL), original QS6 53/72, and new-corpus QS6 57/72 observed with bounds 57–59. They must not be substituted for the faithful-and-strict bars.
