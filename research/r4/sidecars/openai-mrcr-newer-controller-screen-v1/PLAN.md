# Released-model controller screen implementation plan

> Execution: inline, bounded external research sidecar. MAIN reviews READY and alone launches GPU. The approved model note is `ideas/2026-09-12-newer-small-controller-baseline.md`; MAIN's amendment replaces mixed-family/hash-ranked examples with the first8 lexicographically ID-sorted frozen MRCR training records.

Goal: compare released Qwen3-4B-Instruct-2507 and cached released Qwen3.5-4B, no adapters, on8 paired public JSON conversations using the original RLM Python tool.

Architecture: reuse short32's accepted rootless runtime/task and MuSiQue's actual native-wire audit. New local binding/configuration, fixed schedules, finite owner and concise scoring only. Native templates are model-specific: DefaultRenderer(qwen3 tool parser) for old Instruct2507, Qwen35Renderer for3.5, both nonthinking. No custom model/tool framework.

Global constraints:8unique contexts/16episodes; max2 total root turns/episode; nochildren; max32 physical model calls; T.5/top_p1/top_k−1; seed202609190000+case-index;1024 output/call; actual prefix+output≤8192; science≤600seconds/arm,1200total; whole owner1800/external1900seconds including loading/release. Each actual request/response checkpointed. Unknown failures are not wrong answers. No heldout selection, weights/env changes or GPU calls in CPU preparation.

## Task1 — implement and CPU-qualify the thin screen

- [ ] Create `study.py` (source/model bindings, exact sorted training schedule, depth0/maxturns2 environment, tokenizer-native renderer), `prepare.py` (host-only gold/source provenance and first-prefix inventory), `native_capture.py` (counted two-call adaptation of sealed wire audit), `collect.py` (8episode native loop), `metrics.py` (role/ordinal/successor observation and terminal categories).
- [ ] Create `service.py` using the already served3.5 configuration and accepted current-driver environment; `owner.py` uses the existing authenticated lifecycle with unchanged `bin/inference @ config` argv. Save sanitized failure details and confirmed release. Do not change lifecycle math or introduce dispatch instrumentation.
- [ ] First run `test_screen.py` against missing/new interfaces, then implement and run its two focused fixtures. Real CPU runtime fixture: each model-native parser receives one authored `ipython` JSON/XML call inspecting the actual `/context.json`, then one synthetic final. Confirm2returned ROOT actions,0children, exact initial token prefix and raw wire capture. Metrics fixture distinguishes target-assistant observation from a broad dump and provider unknown from model-invalid/final.
- [ ] Freeze `READY.json`, `CPU_EVIDENCE.json`, exact source/data/template/runtime closure and `RUNBOOK.md`. Verify the actual owner entrypoint CPU-only.

## Task2 — MAIN review/admission

- [ ] MAIN reads the new source and actual CPU receipts and chooses whether to launch. Fixed outputs `outputs/attempt-001/{qwen3,qwen35}`. Model order old then new is predeclared; cache/history differences are not a matched-cost causal claim. Two turns allow one inspection then final, not a recovery after a bad first inspection. No spare-call fallback, deeper recursion or post-result adjustment.
