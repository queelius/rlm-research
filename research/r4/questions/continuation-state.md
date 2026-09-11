---
schema_version: "rlm-question-card-v1"
id: "rq:continuation"
title: "Can a learned compact task-local state support reliable fresh-root continuation at lower total cost?"
status: "separate_deferred_line"
updated_utc: "2026-09-09T23:06:56Z"
evidence_cutoff: "2026-09-09T17:32:51.282711+00:00"
living_update_cutoff_utc: "2026-09-09T23:06:56Z"
source_catalog:
  path: "/project/alex_phd/runs/rlm-research-r4/analyses/research-factory-2026-09-09/CATALOG.json"
  sha256: "e0fa23412505eee178d27041816e84f7931d6da01b02e13f664393a6586ff39c"
related_questions:
  - "rq:sufficient-interface"
claim_ids:
  - "claim:continuation-state"
reports:
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/artifact-restart-audit-report.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/state-content-factorial-audit-report.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/state-content-factorial-audit-report-erratum.md"
publication_readiness: "not_publication_ready"
---

# Can compact state support fresh-root continuation?

## Question

Can a learned compact, task-local state preserve reliable continuation after a fresh root starts
while reducing total context, reconstruction, and retrieval cost?

## Why it matters

Long root histories are expensive and fragile. A compact continuation state could support staged or
interruptible computation, but this is a state-transfer question distinct from decomposing the
original input.

## Evidence so far

There is no learned compact-state result. `claim:continuation-state` remains a
proposed hypothesis in the sealed catalog. Later deterministic fresh-root probes
provide relevant evidence without establishing that learned claim.

The [restart audit](../operations/2026-09-09-allocation-5780/artifact-restart-audit-report.md)
tests16 real source states under three fresh-root packages. Quoting genuine history
gave10/16 correct answers and12 faithful supplied-state reductions. Naming archived
files gave3/16, no archived-state reads, and42 new child requests; inline metadata
gave6/16 planned with two unavailable finals and one faithful reduction. All arms
had the same authorized files. This diagnoses state retrieval/use, not the effect
of a learned summary or exact native continuation.

The [separating visibility study](../operations/2026-09-09-allocation-5780/state-content-factorial-audit-report.md)
then increased actual old-state use from3/32 to18/32 when observations were visible,
but answer correctness changed only14/32 to15/32. Genuine state reuse is therefore
not itself a task-quality gain. The
[denominator correction](../operations/2026-09-09-allocation-5780/state-content-factorial-audit-report-erratum.md)
must accompany that report. Both probes use four exposed contexts and alter prompt
length/content; neither proves cheaper general continuation.

## What remains unknown

The proposed state may merely shift context into a trace store rather than save cost. It may omit
unresolved dependencies, rely on hidden cross-episode persistence, or overlap prior continuation
mechanisms without adding a distinct learned contract. The completed48-root restart
pilot took460.357s outer; a larger learned-state comparison is not yet specified.

## Smallest discriminating next experiment

At prospectively frozen checkpoints in held-out trajectories, compare continuation with full history
against a fresh root receiving learned state plus an explicitly accessible trace. Charge state
generation, storage, reconstruction, retrieval, and all failed continuations. Freeze checkpoint
selection and prevent cross-episode persistence before execution.

## What would justify a stronger claim

Promote only if correct continuation is retained on new checkpoints at lower measured total cost.
Revise the state contents after a training-only diagnosis if failures expose missing dependencies,
and retire novelty based only on restarting a root without a learned compact-state advantage.
