# Parser amendment 2 during collection

At `2026-09-10T00:36Z`, after success8 had completed and released-reference was collecting, the
first partial audit exposed an implementation bug in the independent parser: it lexically sorted
request, physical-snapshot and result paths together, allowing the earlier physical `requested`
snapshot to overwrite the terminal `returned` record. This falsely converted authenticated finals
to NULL. The study collector itself was unaffected and reported success8 8/8 available, 3/8 strict.

The amendment makes the already intended lifecycle precedence explicit: request < physical
snapshot < terminal result, retaining all source paths. It changes no endpoint rule, score, study
artifact, or generated output. The failure and initial partial artifact remain preserved; no result
was interpreted from the false parser NULLs. Original corrected-parser SHA-256:
`8f13577748f574f310b76f88b3bd13ec40d296026bcd70a63072cfebc7723724`.
