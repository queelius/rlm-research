---
schema: root-qs-scale-harness-factorial-reader-amendment-v1
amended_utc: 2026-09-10T19:16:23Z
outcome_reads_before_and_during_amendment: 0
reason: add an explicit qualified-native endpoint driver and its synthetic seam test
---

# Immutable v1 receipt and exact reconstruction

The first `READER_READY.json` bytes are preserved beside this receipt. Its SHA-256 is
`d38fde6a0200474d391389226d54be67afdb39b45323d33cef52356df336e89c`; its canonical identity is
`3962275a1535f1b46f4c7f3143d50a7cde18d46f3b56e4c4ae6f644f6623855c`.

The original v1 source hashes were:

- `audit.py`: `94decc2daa224b525eb31ad968eb8f4760dad4ce6300092dc071a05a9c84aca0`
- `test_audit.py`: `f7a1a4d5b9589a57d02eb075f312a263f5a395c0f658ef1f028c906e59cb47ef`
- `METHOD.md`: `dffa8b7d3977f069b18bdf0c477120211d8ab01dac8a01e8cbbb4e7de6b91b13`

V1 is exactly reconstructable from the current v2 sources by removing only these appended blocks:

1. From `audit.py`, delete the complete 40-line block beginning
   `def authenticate_native_rows(` and ending at its `return rows`, including the two surrounding
   blank lines. No other v1 audit byte changed.
2. From `test_audit.py`, truncate immediately after the newline ending
   `assert result["planned_denominator_bounds"] == pytest.approx([-0.25, 0.25])`. This removes only
   `test_native_endpoint_driver_preserves_trace_evidence_and_oracle_separation`.
3. `METHOD.md` is byte-identical in v1 and v2.

Applying those two deletions produces the exact hashes recorded above. V2 was prepared before any
outcome read and changes no running-study source or input. The superseding seal is at the analysis
root; v1 is historical and must not be used as the current reader.
