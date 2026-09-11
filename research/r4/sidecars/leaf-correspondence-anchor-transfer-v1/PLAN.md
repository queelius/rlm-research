# Correspondence-anchor implementation plan

> For agentic workers: use superpowers:executing-plans inline. Parent already approved this bounded600-call design; no user questions, GPU launches or frozen-file edits.

Goal: a launchable old-child-only paired transfer control.

Architecture: study.py reuses the authenticated correspondence parser and fixed collector through private callbacks; driver.py freezes/binds/runs one spec. Strict serialized requests preserve ordering; typed vLLM CPU rendering fixes the known qualification seam prospectively, without changing inherited runs.

Tech stack: qualified Prime Python3.12, httpx, transformers/tokenizers, vLLM0.28/xgrammar CPU schema validation, existing cached parquet via pyarrow.

Spec: DESIGN.md. Isolated destination is this new external research sidecar, not a core Git worktree.

- [x] Write focused failing tests for exact600 allocation/coverage, source-group exclusion, stable IDs, no gold in paired payloads, strict duplicate/missing-ID rejection, schema/property ordering and inherited fake-HTTP capture.
- [x] Implement study.load_data(), study.build_design(), study.make_request(), study.score_coordinate(), study.summarize(); keep complete groups and operational/format/semantic distinctions.
- [x] Implement driver.prepare()/verify()/bind()/run() with exact source closure, old-weight disk/live authentication and typed-prompt/request bytes checks. Run the actual collector against a tiny fake HTTP provider on CPU; no generated tool code.
- [ ] Freeze DATA, REQUESTS, SPEC and qualification evidence; run focused tests only. Publish READY last with exact bind/run commands and hard1800s cap.

No commits to the core repository; no new environment, download, broad tests or framework.

The last item is machine-certified only by READY.json, written last after CPU_TESTS.json and a fresh frozen-spec verification. This plan stays unchanged after sealing.
