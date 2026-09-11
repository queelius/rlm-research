---
schema_version: "rlm-question-card-v1"
id: "rq:latent-recursion"
title: "When should a recurrent-depth backbone spend compute internally versus on external decomposition?"
status: "deferred_architecture"
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

# When should compute stay internal or become external decomposition?

## Question

When should a backbone trained for recurrent depth spend compute internally, externally through RLM
decomposition, or through a mixture of both?

## Why it matters

Internal recurrence and external decomposition offer different memory, communication, and control
trade-offs. A matched comparison could identify where each compute path helps rather than attributing
all differences to recursion in general.

## Evidence so far

There is no experiment, claim, or result for this question. It is a deferred architecture line, and
the current catalog contains no qualified recurrence-trained backbone.

## What remains unknown

Backbone architecture, pretraining, and recurrent-depth training would confound a comparison with an
ordinary model. External tools may already provide the relevant benefit. Looping arbitrary vanilla
layers would not establish a valid recurrent-depth condition.

## Smallest discriminating next experiment

Only after pinning a model actually trained for recurrence, compare internal, external, and mixed
compute policies under equal model, data, and total-compute budgets on held-out tasks. Freeze the
recurrence schedule, external call policy, stopping rules, and cost accounting. No experiment is
ready and no bounded GPU duration is available.

## What would justify a stronger claim

Promote only matched architecture and training-budget evidence that identifies a reliable task or
difficulty boundary. Revise if capacity or training history explains the difference, and retire any
proposal based only on repeatedly applying unqualified vanilla layers.

