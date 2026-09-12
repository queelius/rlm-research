---
schema: fresh512-additive-findings-v1
written_utc: '2026-09-12 14:10 UTC'
source_audit_sha256: 57606da1e52a5b694cad6d39dbff9febf5c66a7f6783ce3cf99e440e961f7bbb
status: exploratory_fixed_endpoint_result_replication_candidate
new_model_queries: 0
---

# Fixed512 outcome: RL improves this panel, at substantially higher training cost

All **512 records are available in each arm** (128 valid B4 calls each; no malformed,
failed, or unattempted calls). Correct totals are c32 **422/512 (82.42%)**, RL step8
**437/512 (85.35%)**, and SFT step8 **427/512 (83.40%)**. This clarifies the older
watcher's shorthand “422/512 available”: 422 is correct, not available.

| Comparison | Gains / losses | Net correct | Changed labels | Descriptive paired 128-request-cluster 95% interval |
|---|---:|---:|---:|---:|
| RL minus c32 | 17 / 2 | +15 (+2.93 pp) | 21 | +1.37 to +4.49 pp |
| SFT minus c32 | 7 / 2 | +5 (+0.98 pp) | 9 | 0.00 to +1.95 pp |
| RL minus SFT | 12 / 2 | +10 (+1.95 pp) | 16 | +0.78 to +3.32 pp |

These are the predeclared endpoints/comparisons, not best-checkpoint selection. The
intervals are the existing scorer's descriptive 2,000 cluster bootstraps, not an
independent-512-item p-value or evidence of general replication.

| Host class (128 each) | c32 correct | RL correct | SFT correct |
|---|---:|---:|---:|
| World | 113 | 113 | 113 |
| Sports | 121 | 124 | 122 |
| Business | 117 | 115 | 116 |
| Sci/Tech | 71 | 85 | 76 |

The observed error change is concentrated in Sci/Tech: its Business errors fall
44→34 under RL (39 under SFT), and its World errors 12→7 (13 under SFT).
Business→Sci/Tech mistakes increase 3→5 (4 under SFT). This is consistent with a
shift in that decision boundary; it does not identify a learned mechanism or prove
RL is generally superior. World predictions do not change. RL's 21 changed labels
include two wrong→different-wrong changes; its 128 groups have 17 positive, two
negative and 109 zero net changes. SFT has six positive, one negative and 121 zero
net groups, including one group with cancelling gain/loss. All group tables,
transition counts, class-paired IDs and missingness inventories are in FINDINGS.json.

Measured RL training owner wall time was **2,094.99 s (34.92 min)** versus SFT
**236.25 s (3.94 min)**: about 8.87×. RL included 1,024 native sampled maps,
4,096 label decisions, 1,025,748 reported prompt tokens (934,016 cached), 81,624
completion tokens, and 614.44 s of HF stages. Native call spans sum to 665.40 s;
stage timings are nested, not added to the full owner duration. SFT used 256 gold
maps / 1,024 records / 20,591 supervised tokens and 224.44 s of training.
Both arms share data and eight optimizer updates, but not compute or action exposure.

Each evaluation uses 127,663 prompt tokens, 87,376 cached; completions are
10,152 / 10,184 / 10,164 for c32 / RL / SFT. Serial call time is
322.03 / 323.16 / 322.45 s; full owner time 438.87 / 442.50 / 439.01 s.
All usage is known; baseline is one physical 128-call run reused only after matching
the qualified runtime. Queue waiting is excluded.

All eight RL steps passed source/native-parent binding, host reward/RLOO checks,
importance gates (ESS 110.52–127.54/128), all 128 replay checks per step, and carried
Adam counters 1–8; replay discrepancies were zero. Mixed groups range 3–8/32 and
parent-adapter delta norms 0.0201–0.0402. Training item sets differ each step, so
their 398–459/512 sampled correctness values are **not a learning curve**.

The predeclared positive-versus-both-controls branch is reached: prepare the same
fixed dose on the same data with fresh training seeds, evaluating only final step8
on this **same now-research-exposed512**. This tests training-seed replication,
not a new heldout dataset. Neither trained arm meets the ≤5-changed-label
near-identical screen; a separate likelihood diagnostic must be labelled as such.
No universal helper, root-recursion, or adaptive-planner gain follows from this result.

Evidence: [raw audit](../helper-agnews-eightstep-live-audit-2026-09-12/outcomes/RAW_AUDIT-003.json),
[derived details](FINDINGS.json), [derivation](derive_findings.py),
[prospective decisions](DECISIONS.yaml). This is a source-to-raw audit, not an
independently authored trainer replication. The sealed scorer redecodes all 384
raw native responses and checks exact saved requests, ordered schemas, endpoint
bindings, runtime configuration, batch-invariant kernel evidence and clean release.
