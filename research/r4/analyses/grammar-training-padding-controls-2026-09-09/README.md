# Grammar, training and output-padding controls

Status: complete at2026-09-09 approximately05:03UTC. All368 calls are terminal and
raw-audited; no infrastructure or unrun nulls. No extra indexed-SFT benefit is
demonstrated over B. Meaningful tags strongly beat constant placeholders under
exact grammar, while both free-tag formats fail to provide aligned outputs.

- [METHOD.md](METHOD.md): pre-outcome questions, audit and interpretation rules.
- [REPORT.md](REPORT.md): readable findings, exact comparisons, cautions and what
  changes next. [METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json") retains every paired comparison.
- [COUNTS_AND_FORMATS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: COUNTS_AND_FORMATS.json"): per-call label-count agreement
  and lexical/format diagnostics. No pooled-histogram count claims.
- [grammar160/METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: grammar160/METRICS.json"),
  [B80/METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: B80/METRICS.json"),
  [padding128/METRICS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: padding128/METRICS.json"): immutable raw-audited cells and calls. Each
  stage's SOURCES.json contains exact raw wire/call/input/weight hashes.
- [audit.py](../../../../ARTIFACTS.md#unpublished-files "Not published: audit.py"), [synthesize.py](../../../../ARTIFACTS.md#unpublished-files "Not published: synthesize.py"), [test_audit.py](../../../../ARTIFACTS.md#unpublished-files "Not published: test_audit.py"):
  [count_readout.py](../../../../ARTIFACTS.md#unpublished-files "Not published: count_readout.py"): reproducible CPU-only parsing, raw checks and paired synthesis. Two focused tests
  were RED before implementation and now pass; no broad suite or model call.

This analyst authored the B companion; this is a results audit, not a fresh
independent code review. The separate parent reviews are in
`operations/2026-09-09-proceed/B_CONTROL_SOURCE_REVIEW.md` and
`PADDING_SOURCE_REVIEW.md`. [SOURCES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCES.json") and FINAL_MANIFEST.json retain
the artifact hashes. [The partial snapshot](../../../../ARTIFACTS.md#unpublished-files "Not published: PARTIAL-grammar160-B80.json") is preserved.
Audit work never gated the automatic GPU sequence. This bounded audit is finished.
