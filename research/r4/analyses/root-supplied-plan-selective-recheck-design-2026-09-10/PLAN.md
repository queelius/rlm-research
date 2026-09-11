---
status: conditional_plan_not_ready
date: 2026-09-10
implementation: intentionally_absent
planned_new_calls: 24
planned_rechecked_labels_per_arm: 320
---

# Preparation plan after conditional admission

1. Pin the completed ceiling terminal/adopted audit and independently reconcile its 40 exact
   request/response/result triples, 1,280 labels, complete baseline maps, and physical cost.
2. Run the CPU-only exact tokenizer/span alignment check. Stop on any missing label, crossed token
   boundary, nonfinite/missing chosen-token log probability, or renderer mismatch.
3. Compute only label-token mean confidence. Freeze per-episode confidence and hash-uniform selections,
   natural overlap, original episode order, repacks, and the 12 paired fresh seeds. Verify selection
   code has no host-gold dependency and scan seed collisions without reroll.
4. Materialize separate immutable inputs for baseline evidence, confidence rechecks, uniform
   rechecks, public reducer inputs, and private audit gold. Freeze exact request hashes and logical
   arm-to-physical-call accounting.
5. Reuse the qualified c32 service/collector; add only a thin recheck/merge layer. Qualify exact
   structured responses, overwrite-only-selected behavior, whole-batch baseline retention,
   unavailable versus authenticated-invalid branches, and J1 reduction with CPU fake transport.
6. Seal a new sidecar under a new name. Record one A100, 24 calls, four workers maximum, no retry,
   no training/checkpoint, 1,800-second outer cap, cleanup reserve, and a prospective audit method.
7. Submit to MAIN for source review. MAIN decides whether conditional evidence is satisfied and, if
   so, serializes launch. This document does not authorize GPU or service access.

# Frozen episode/call shape

| Size | Episodes | Selected per episode per arm | Repacked calls per episode per arm | New calls, both arms |
|---:|---:|---:|---:|---:|
| 64 | 4 | 16 | 1 x 16 | 8 |
| 256 | 4 | 64 | 2 x 32 | 16 |
| Total | 8 | 320 per arm | 12 per arm | 24 |

The 40 first-pass ceiling calls are shared read-only baseline evidence and are not rerun or counted
twice. Report their cost separately from the 24 incremental calls.

# Required post-terminal audit outputs

- Native validity and availability for every planned recheck call, with no missing cases omitted.
- Frozen selections, overlap, label spans/confidences, repacks, request hashes, seeds, and physical
  call provenance.
- Operational baseline-retention and per-protocol results kept separate.
- Child correction/regression, merged-map accuracy, qualifying-user, and contribution diagnostics.
- J1 exact/absolute-error and paired confidence-versus-uniform results, per episode, cluster, and size.
- Full known/unknown input, output, cache, request, elapsed-time, and release accounting.
- An explicit reminder that eight nested episodes from four exposed clusters are not independent.
