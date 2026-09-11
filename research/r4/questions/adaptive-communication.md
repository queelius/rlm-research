---
schema_version: "rlm-question-card-v1"
id: "rq:adaptive-communication"
title: "Do resumable task-local child handles buy useful information more cheaply than a comprehensive first return?"
status: "deferred"
updated_utc: "2026-09-09T18:19:33Z"
evidence_cutoff: "2026-09-09T17:32:51.282711+00:00"
source_catalog:
  path: "/project/alex_phd/runs/rlm-research-r4/analyses/research-factory-2026-09-09/CATALOG.json"
  sha256: "e0fa23412505eee178d27041816e84f7931d6da01b02e13f664393a6586ff39c"
related_questions:
  - "rq:sufficient-interface"
claim_ids: []
reports: []
publication_readiness: "not_publication_ready"
---

# Are resumable child handles worth their cost?

## Question

Do resumable, task-local child handles provide useful information more cheaply than requiring one
comprehensive first return?

## Why it matters

Adaptive follow-up could let a root request only missing evidence. It could also add more turns,
state reconstruction, and coordination cost than a well-designed one-shot report.

## Evidence so far

There is no experiment, claim, or result for this question. It is explicitly deferred until the
one-shot report-sufficiency question is better understood.

## What remains unknown

No ownership contract, persistence boundary, continuation cost model, or failure semantics are
prepared. Back-and-forth overhead and state reconstruction may erase any information advantage.

## Smallest discriminating next experiment

Under one fixed global budget and no cross-episode persistence, compare a small first report, a
comprehensive first report, and a small report followed by charged resumptions. Freeze handle
ownership, allowed state, stopping rules, correctness metric, and total call/token accounting before
launch. No bounded GPU duration is currently available.

## What would justify a stronger claim

Promote only a matched-budget accuracy-versus-cost benefit on held-out tasks after charging every
continuation and failure. Retire the direction if the comprehensive one-shot return dominates.

