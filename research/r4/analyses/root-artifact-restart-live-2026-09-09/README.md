# Root artifact restart independent audit

Read-only independent audit of `sidecars/root-artifact-restart-v1/outputs/attempt-001`.

- `METHOD.md` and `METHOD_READY.json`: method and honest post-collection timing disclosure.
- `OUTCOME_PINS.json`: immutable inventory of the untouched outcome tree.
- `audit.py`, `AUDIT.json`, `DETAILS.json`: strict score, native-envelope/token/usage checks,
  and extracted final-branch programs.
- `provenance_audit.py`, `PROVENANCE_AUDIT.json`: source-pin, pre-cut/package byte equality,
  privacy-schema, and 48 runtime setup checks.
- `manual_dataflow.py`, `DATAFLOW_AUDIT.json`: trace-grounded artifact use, scoped reduction,
  reacquisition, merge, and overwrite classifications. No model-generated code was executed by
  the auditor.

The authoritative plain-language report is
`operations/2026-09-09-allocation-5780/artifact-restart-audit-report.md`.
