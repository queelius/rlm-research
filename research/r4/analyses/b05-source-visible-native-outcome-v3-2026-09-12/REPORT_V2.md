---
title: B05 V3 response-hash and child-ID audit correction
date: 2026-09-12
status: COMPLETE_CORRECTED_RAW_AUDIT
---

# B05 V3 response-hash and child-ID audit correction

The initial audit's 56 `response_sha` flags do not indicate response corruption. The
collector first assigned the raw response-file SHA256, then overwrote that field with
`decode_response`'s canonical parsed-JSON digest. All 56/56 saved
physical responses match the recorded canonical content digest. Their raw-byte SHA256
values are now recorded separately; none happened to equal the canonical digest. The
collector did not preserve those raw-byte hashes in its call records, so this addendum
does not pretend they were originally attested.

The strict child grader accepted 22/24 responses and rejected two for invalid metadata.
The original conditional ID summary therefore covered only 22 records. The inert,
all-record diagnostic covers 24/24 child calls and a fixed 64 eligible IDs: it finds
40/42 predicted IDs correct
(precision 0.952381) and
40/64 eligible IDs recovered
(recall 0.625000). Among matched IDs,
4 rows have exact metadata and
36 do not. Invalid metadata remains invalid; ID
overlap is not a repaired child answer or training label.

The original audit and its 56 issues remain preserved. Native prompts, token arrays,
model/sampling fields, grades, actual `ReportWorker` marker, dispatch receipt, and owner
release had no other reported discrepancy.
