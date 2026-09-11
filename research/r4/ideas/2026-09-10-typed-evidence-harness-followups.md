---
schema: typed-evidence-harness-followups-v1
status: conditional_design_only
date: 2026-09-10
gpu_calls: 0
source_sha256:
  scale_failure_report: 1a87ce0fd1a9a5dd2bd833a003be0345862b9b922fae5ddcfdffad1fd165dd54
  zero_support_note: 494298cad416a41b28ef5ada86fcd07e0ade864aa717c0a5d1f3d11826f791e2
  research_engine.py: 2e04fe4589c75cef1ba3fdbbaead1275c40984588bf782e972c5556e3cc7f7ed
  research_supervisor.py: 1b9a1b303b7c2a389d8981d0c7ea9d3e5603b49f8a420f354220c6a28c9cc78e
  research_session.py: a18e282336d9ffed1dfba52a0d9e87d1449d28faf552ef239eed08e130eb40c5
  existing_ledger.py: 49105a0e29db06ba718d8527b1b45daf7639cbbecc6356e28ad46699ec05a1ea
  existing_ledger_overlay.py: febb0e22c1b00fbac83c5203df5b5795adc27ca19f5f223aeb3550c078b292fc
  bounded_view_overlay_v2.py: c59c7567618462984fb97924ff628e5bb84ec3fd9a24c5407639f1109880da9b
  strict_batch_contract.py: d2c7f8df62a4190930dbf3e14f7e68cfb27cc573898bbc343117e8d97190bd88
  lambda_rlm.py: 3f0e0521f92e1e124e76aa4f717a7bf29c95386ff42b3faf6057d4fa320f42e6
lambda_rlm_commit: 3874d393483dc4299101918cf8e9af670194bd88
---

# Two small harness mechanisms after the Scale64 failure

The failure diagnostic does not support a scale-effect claim, but it does locate
three interfaces worth separating. Among 38 authenticated paths, 31 issued a
genuine acquisition, only 20 retained a complete decoded map, and only 12 ran
the requested J1 computation. Six of seven faithful-and-strict paths had zero
gold; two would have raised `TypeError` on nonempty selected support. One further
path received 64 label-shaped child entries but never decoded them because it
passed record dictionaries rather than IDs to `strict_map`. Any follow-up should
therefore use nonzero support as its primary stratum and score acquisition,
retention, reduction, and stopping separately.

## 1. Source-bound typed evidence store (recommended)

Add a supervisor-owned, episode-local key/value store for *observed child
predictions*. The supervisor already sees the direct-child prompt/result before
writing the broker response; the existing experimental overlay hooks precisely
at `finish_subagent`, `write_frame`, and root `log_tool_result`. Admit a result
only when its prompt is an exact source-bound request and its response passes the
existing whole-map validator. Persist `{record_id: predicted_label}` plus
conflicts, provenance, and coverage across turns/compaction. Expose a neutral
IPython API such as `evidence.snapshot()` and `evidence.status()`.

The store must not choose records, launch children, inspect the user question,
read target/target-B/user/weight fields, compute label counts, or provide a
reducer. The root still decides whether and how to acquire evidence and must
author the final computation. This is a typed memory primitive, not a supplied
J1 plan. Unlike the earlier ledger, it exposes the actual source-bound predicted
map rather than only class counts; unlike cumulative decoder return values, it
cannot be overwritten accidentally by the root's last local variable.

Small comparison: fixed sft6 root and c32 child, all four frozen clusters at
sizes 16 and 64, contemporaneous ordinary cumulative-map versus typed-store
arms, one new paired seed per cluster/size: 16 root endpoints, four workers,
300-second endpoint cap and about 2,400 seconds outer. Size64 gives four
precommitted nonzero-gold blocks (`82,54,48,15`); size16 is a reachability
diagnostic and has three zero-gold blocks. Keep all calls and NULLs.

Primary is paired faithful-and-strict improvement on size64, with acquisition,
store admission/coverage, snapshot use, requested-operator execution, nonzero
support, final state use, physical calls, and token cost separate. Promote to new
contexts if at least 3/4 nonzero blocks improve, root-state decoding failures
fall, and availability does not decline. If complete stores are actually read
but faithful reduction does not improve, retire memory work for this policy and
target operator execution. If stores are not read, the result diagnoses
interface uptake rather than memory efficacy.

## 2. Immutable child-result handles (cleaner retention isolation)

Write every full child result to an immutable, supervisor-private artifact and
replace the next root-visible tool message with a bounded receipt containing
handle, requested IDs, byte count, and hash. Provide only a generic
`read_child_result(handle)` function. The root must explicitly retrieve and
validate the raw output; there is no automatic parsing, accumulated map,
relevance decision, or reduction. Preserve the full artifact for audit. This
tests whether repeated inline maps and truncation are the retention bottleneck
without adding solver information.

Compare current bounded-inline output against artifact handles on all four
clusters at sizes64 and128, again fixed sft6/c32 with one new paired seed:
16 endpoints, four workers, 300 seconds each and about 2,400 seconds outer.
All eight blocks have nonzero gold (`64: 82,54,48,15`; `128: 141,95,85,39`).
Primary is authenticated availability plus faithful-and-strict; mechanism
metrics are handle exposure, actual handle reads, complete decoded-map
retention, context tokens, requested reduction, and stopping. Promote only if
at least 3/4 clusters improve at either size with no availability loss and
actual handle use mediates the gain. If handles are exposed but not read, revise
the policy/interface before scaling; if read maps are complete but reductions
remain wrong, retire this retention intervention.

## Provenance and novelty boundary

Read depth was the complete Scale64 report and zero-support note; the existing
ledger/overlay and batch validator in full; the research engine around tool
observation and supervisor around child completion/broker delivery; and official
lambda-RLM `lambda_rlm.py` lines 500–625. Official lambda-RLM injects fixed
split/reduce combinators and a generated executor. These proposals deliberately
stop earlier: they preserve or reference model-produced evidence but do not
select a task plan or reducer. Typed recursive evidence state may be broadly
useful, but these small exposed-cluster studies would be exploratory mechanism
tests, not novelty or generality claims.

Exact local code paths were
`sidecars/root-accumulation-ledger-v1/{ledger.py,overlay.py}`,
`sidecars/root-bounded-observation-view-v1/bv_overlay_v2.py`,
`sidecars/adaptive-filter-pilot-v1/batch_contract.py`, and
`/project/alex_phd/research-cache/repos/lambda-RLM/rlm/lambda_rlm.py`. The pinned
research-runtime files were `src/rlm/{engine.py,supervisor.py,session.py}` below
`/tmp/rlmc.an27-5780.jL5eG5/root/vfs/dir/b50ce4f5b31918d4d2b15d21586825a9320f10fc20818b76f982bcd465d75efc/tmp/vf-rlm-4fa91253816bfa64435b7b727ec01bac2a7a7a2b72ece29ceb2474d26f95418d/checkout/`.
