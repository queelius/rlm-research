---
schema: mrcr-independent-context-provenance-scope-erratum-v1
created_utc: 2026-09-12
status: additive_clarification_no_data_change
---

# Provenance and claim-scope clarification

`PROVENANCE.json` records Apache-2.0 from the pinned `eval_hub` repository `LICENSE`. That is
direct evidence for the repository code; the cached receipt does not contain separate evidence that
the GCS CSV object is licensed under the same terms. Treat the dataset object's license as
**unconfirmed** until an official dataset-specific statement is pinned. This does not change any
cached byte, row, split, or score.

The five selected contexts are disjoint only under the frozen exact paired User-to-Assistant block
test. They are not claimed semantically independent, independent generation sources, or absent from
pretraining. They were also not cross-checked against the separate 32K--64K pilot context.

Any future 3-train/2-held study must start both compared policies from the same fresh no-adapter
cached 4B checkpoint. It must not warm-start from an adapter trained on the prior single-context
32K--64K pilot, preventing that pilot's exposure from entering the proposed short-context transfer
comparison through weights.
