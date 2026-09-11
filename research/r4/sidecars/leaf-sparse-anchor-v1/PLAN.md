# Sparse anchors implementation plan

> Use superpowers:executing-plans inline. Main approved the bounded design; no subagents or GPU calls during preparation.

**Goal:** Freeze and prepare the exact 144-call mixed-output component screen.

**Architecture:** Add only this sidecar. Private imports reuse qualified native HTTP collection, physical projections and owned service lifecycle; new code owns data/condition construction, mixed-item scoring, sparse summaries and caps. Existing source files and attempts stay unchanged.

**Tech stack:** Pinned Prime Python, httpx, vLLM typed request, native HF tokenizer, XGrammar, pytest; no installs.

**Spec:** DESIGN.md. Constraints and all experiment values are authoritative there.

## Task 1: exact inputs, sparse schema and strict scorer

- Write focused failing `test_study.py` fixtures for144 coordinates/72 paired shapes,64/16/4 anchors, host-gold exclusion, canonical strings/ordered objects, duplicate keys/wrong types, and null-vs-complete-invalid.
- Implement `study.py`: source-checked private qualified helpers,12 exposed source crosswalks, balanced frozen plan, body/schema builder, strict mixed parser, coordinate/cell/paired/distance projections. Do not invoke generated code.
- Run only those tests and inspect red→green evidence. No Git commit for external research artifacts.

## Task 2: qualification and parent-only owned command

- Write focused fake-HTTP tests of the inherited collection callback (valid, malformed,500), and lifecycle cap/source edit-count checks.
- Implement `driver.py` using the exact inspected native run seam with144/900 substitutions; keep endpoint binding and one start clock. `owned.py` privately adapts qualified single-adapter lifecycle and only known process-absence guard.
- `prepare` checks bounded seed namespace, constructs all144 complete bodies, exact CPU typed IDs, distinct mixed XGrammar fixtures and task+cap bounds, freezes DATA/SPEC/WEIGHTS/REQUESTS/PROMPT_IDS/source crosswalk, and records versions/tests.
- Verify frozen sources and exact requests; publish READY last with launch argv, caps, output path and parent-exclusive ownership/release requirements. Main reviews and owns acceptance/launch. No source reformatting, broad test suite, speculative install or service action.
