---
question: rq:adaptive-decomposition
date: 2026-09-12
status: audited_partial_run
evidence_level: exploratory_one_model_partial_fixed_panel
report_sha256: 4691d5f0706eb72d23f340e0e0c397e7091baebc16b4a9c13f76f003a7bb2dac
---

# Asking for less did not make this helper more reliable

We tested full-category answers against a narrower request: return the named
target category or `other`. Both methods were scored on the same category-count
questions. A full map could be reused for all categories; its physical cost was
not multiplied when deriving those different counts.

The fixed time budget expired after 82 of 96 planned requests: 81 returned valid
maps, one hit the request deadline, and 14 were never attempted. Runtime evidence
confirmed the intended batch-invariant service and clean release. This is a
partial experiment, not a completed 80-task comparison. We did not extend its
cap after seeing results or retry selected mistakes.

The independent audit separates comparisons for wholly completed blocks:

| Completed paired subset | Full-category exact counts | Target/other exact counts | Sum of absolute count errors: full → target |
|---|---:|---:|---:|
| TREC: seven blocks, 42 category-count questions | 27 / 42 | 20 / 42 | 16 → 152 |
| AG News: six blocks, 24 category-count questions | 9 / 24 | 9 / 24 | 22 → 38 |

These count questions reuse the same records and are not independent trials.
The unfinished portion cannot be treated as wrong, correct, or zero-cost answers.
Full-panel macro accuracy and the prespecified promotion screen are unavailable
or fail eligibility because the panel is incomplete.

The most striking behavior was the TREC `entity` target: every one of the 112
records in the seven completed blocks received a positive answer, although only
21 had that dataset category. MAIN separately checked those saved maps. The
full-category condition did not have that collapse. This is a semantic category
decision failure despite valid JSON, not an input–answer matching failure.

One hypothesis is that the helper's prior full-category training made a familiar
category label much more likely than the new `other` output under the narrowed
grammar. Other explanations include the wording, the meaning assigned to `entity`,
and how category competition changes under restricted decoding. We have not
identified the mechanism. In particular, a smaller allowed output set is not
automatically a faithful aggregation of the original six-category distribution.

Decision: do not promote literal-target/other as a helpful harness modification.
The negative completed-block evidence is sufficient to move to a diagnostic
comparison rather than spend another run merely completing its tail. The next
approved test uses `yes`/`no` for all six category targets on all 128 TREC records,
with a fresh full-category control. Those outputs are also outside the original
fine-tuning format, so success is not assumed. A secondary comparison with the
old seven-block subset must remain explicitly cross-service and report control
drift. Any positive finding still requires a fresh-panel test.

Artifacts: this directory's write-once `REPORT.json`; raw experiment under
`../../sidecars/helper-targeted-category-counts-v1/outputs/attempt-001`.
The original READY and all failed/unattempted-call accounting remain preserved.

Operations lesson: 96 sequential sixteen-record requests needed more than the
810-second request window inside the 900-second owner cap. Estimate future caps
from measured per-call time plus startup and cleanup, rather than from the much
faster individual-record calls in a mixed-size experiment.
