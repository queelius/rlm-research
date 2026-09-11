---
id: bounded-native-observation-view-feasibility-2026-09-10
status: design-only
created_utc: 2026-09-10T09:34:24Z
question: Can deterministic stdout clipping prevent cumulative-map context pressure without changing execution state or adding solver information?
decision: conditionally-run-small-factorial
gpu_calls: 0
---

# Bounded native observation view: feasibility and smallest test

## Finding

This is a genuine harness-only intervention, but **not** a setting in the frozen scale
harness. The actual native engine logs the full tool result and only then creates the
model-visible view:

```python
result = tool_result.content
self.session.log_tool_result(turn, tool_name, result, duration)
content = truncate_tool_output(result)
messages.append({..., "content": content})
```

That is the right seam. The frozen engine is
`research-cache/2026-09-08-literature/leaf-contract.7HPUr5/nano__engine.py`, SHA-256
`2e04fe...f7ed`, lines 535–539, acquired from PrimeIntellect `nano-rlm` revision
`4ef3438d55fdd39b18d34035833c73e13b006733`. Its current call uses the built-in
budget; it does not pass a per-run value. The cached successor implementation's
`src/rlm/compaction.py` (SHA `ed9e1f...061b`) defines that default as 20,000 bytes and
already implements content-blind head/tail clipping with an explicit warning, original
estimated token count, line count, and omitted-byte count. `src/rlm/session.py` (SHA
`a18e28...40c5`) confirms that `log_tool_result` writes the unshortened `content` to
`messages.jsonl`. That successor also defines `ExecutionPolicy.max_tool_output_bytes`
in `src/rlm/config.py` (SHA `b64669...78e`), but the frozen scale engine calls the
truncator without the configurable argument; an actual composed-runtime test, not the
presence of the newer field, must establish any config-only route.

Two nearby implementations are informative but are not the active experiment seam.
The official cached RLM at commit `beb0603f...` calls
`format_iteration(iteration)` in `rlm/core/rlm.py` (SHA `9f7294...4559`); its
`rlm/utils/parsing.py` (SHA `8b4697...0e54`) independently defaults to 20,000
characters and appends an omission count. This repository's Responses runtime exposes
`RunLimits.max_observation_chars=6000` in `src/rlm/config.py` (SHA
`70aff7...ce9`) and builds a typed clipped observation in `src/rlm/observation.py`
(SHA `9ebe48...74b`). Neither knob controls the native Chat/IPython path used by the
completed scale/accumulation studies.

## Smallest defensible intervention

Use an experiment-local, source-hash-gated overlay that changes only the native
engine call to `truncate_tool_output(result, 4096)`. Keep the existing deterministic
head/tail policy and visible warning. Do not modify IPython execution, variables,
`strict_map`, child requests, final parsing, context limit, or compaction. Before the
temporary runtime is removed, copy and hash each session's raw `messages.jsonl`; also
write a clipping ledger containing turn, raw SHA/byte count, visible SHA/byte count,
and omitted bytes. The EPISODE/tool message remains the clipped policy input, while the
raw log is analysis-only. Config-only reuse is insufficient unless an actual runtime
fixture proves the pinned engine honors it and the collector preserves the raw log.

This does not summarize. A “summary oracle” that selects IDs, canonicalizes maps,
deduplicates values, preserves query-relevant facts, or describes the next reduction
would inject task information and confound capacity with assistance. Fixed-byte
head/tail clipping is content-blind and can produce invalid partial JSON; that is an
intentional cost, not repaired. Runtime variables and full maps remain live in the
persistent kernel, so later code can reduce them without recovering text from the
visible transcript.

Prior cached prefixes remain identical only through the first tool result. After that,
the clipped observation changes the root's policy context. Therefore this is a new
harness-package evaluation, not an exact replay of prior native trajectories. Existing
SFT/RL weights may be served unchanged, but cached logprobs, rewards, or continuation
groups must not be spliced across the changed observation. Code execution and child
responses are unchanged; only what the root sees afterward differs.

## Conditional 32-call test

Do not run from the preliminary B/C accuracy counts alone. Promote only if the sealed
mechanism audit finds (a) cumulative/full-map stdout materially dominates later prompt
length and (b) unavailable or stopped paths occur after such output, with context
pressure or length evidence. Otherwise clipping answers the wrong failure mode.

If promoted, use a 2×2 on eight mechanically selected exposed large blocks:
`BATCH` versus `CUMULATIVE`, crossed with the unchanged 20 KB view versus the 4 KB
view, one new seed shared by all four cells per block = 32 roots. Select one operator
for each of four parent contexts × {128,256} by a frozen hash rule, balancing count and
weighted-sum four/four; no outcome filtering. Rotate dispatch order. Preserve the exact
records, query, gold, c32 child, fixed24 weights, 2048 action cap, 8192 context, and
ordinary failure/NULL rules. This subset is an exposed mechanistic panel, not a fresh
replication.

Primary: native-final availability and strict dataset score on all planned slots.
Mechanisms: per-turn raw/visible bytes and prompt tokens; actual child acquisition;
two-batch coexistence in live state; requested operator/scope-faithful reduction and
stop; clipping encountered before each later root action. Analyze the within-block
clipping contrast separately in BATCH and CUMULATIVE, plus their interaction; do not
use historical seeds as the control. A positive result requires reduced context
pressure and more faithful CUMULATIVE reductions without a material BATCH regression.
If clipping only raises availability, call it interface robustness. If partial JSON
causes abandonment, test a separately declared structural non-oracular view—not a
post-hoc summary. Expand to all 16 blocks only after this diagnostic is informative.

The reported preliminary accumulation counts (B 1/16 with 5 available; C 0/16 with 4
available) are motivation only. Their mechanism audit is pending, so this note makes
no efficacy or context-failure claim.
