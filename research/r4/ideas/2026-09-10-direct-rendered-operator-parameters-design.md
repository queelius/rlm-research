---
id: direct-rendered-operator-parameters-v0
status: draft-design-only
date: 2026-09-10
calls: 48
model: Qwen3-4B-Instruct-2507 + fixed operator-SFT24 LoRA
child: fixed c32
gpu: one A100 40GB
implementation_authorized: false
---

# Draft: direct-rendered operator parameters

## Question

Does placing the exact declarative task parameters in the root user message make the fixed24 policy recover and execute them, relative to the original prompt where the same operation is expressed only in natural language?

This isolates **optional-file reachability/salience**, not algorithm teaching. Interface72 observed zero reads of optional `task.txt`/`task.json` and 0/48 faithful operations. The task question itself was not hidden: audit of the actual first native root body found the complete question directly in the user message and in its token IDs, which exactly matched the frozen prefix.

## Fixed comparison

Use all 24 exposed composition blocks (eight contexts × three operators), two paired arms, one newly frozen paired seed per block:

- `U`: byte-identical original prompt, files, record context, query, and helper.
- `R`: the same prompt and files, with one appended declarative block only: `operator`, `category_a`, `category_b`, `scope`, `threshold`, and `threshold_comparison` using the frozen task-spec values.

The block must contain no procedure, code, examples, answer, labels, batching advice, or tool requirement. For example: `Task parameters (declarative, not instructions): operator=maximum_weight; category_a=entity; category_b=null; scope=all records and all users; threshold=null; threshold_comparison=null.` Exact serialization is common across arms except field values and is frozen before calls. Preserve fixed24 root, c32 child, coding role, tools, 8192 context, 2048 root cap, temperature 0.5, four workers, and strict `Answer: N` scoring. Scan new seeds against named study inventories before freezing; no outcome-based replacement.

## Measures and decision

Primary measures, on all 48 planned endpoints with missing/inauthentic finals as NULL:

1. exact parameter recovery/use in executed final-branch code or observations (field-by-field, with advertised versus read versus operationally used kept separate);
2. faithful requested operator, category, scope, threshold, and stopping behavior, regardless of child-label correctness.

Secondary: strict scalar correctness, native availability/bounds, actual acquisition/map retention, paired `R−U` wins/losses/ties, zero/nonzero strata, eight dependent context clusters, and physical root/child/token cost. Do not execute sampled code, repair labels, or infer use from scalar agreement.

Promotion signal: direct rendering produces parameter use and at least four additional faithful executions spanning three contexts without worse availability. If parameters are recovered but execution remains unfaithful, placement is not the main bottleneck and execution-grounded training becomes the next question. If parameters are not recovered, test a minimal explicit first-action echo/parser interface before another downstream rollout. Card48 remains a separate algorithm-instruction experiment; it preserves the same task questions and records but answers a different research question.
