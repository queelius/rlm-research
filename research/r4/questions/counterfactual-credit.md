---
schema_version: "rlm-question-card-v1"
id: "rq:counterfactual-credit"
title: "Can decision-level counterfactuals improve training-data selection beyond ordinary success trajectories?"
status: "deferred"
updated_utc: "2026-09-09T18:19:33Z"
evidence_cutoff: "2026-09-09T17:32:51.282711+00:00"
source_catalog:
  path: "/project/alex_phd/runs/rlm-research-r4/analyses/research-factory-2026-09-09/CATALOG.json"
  sha256: "e0fa23412505eee178d27041816e84f7931d6da01b02e13f664393a6586ff39c"
related_questions:
  - "rq:controller"
claim_ids: []
reports: []
publication_readiness: "not_publication_ready"
---

# Can counterfactuals improve training-data selection?

## Question

Can decision-level counterfactual continuations select better controller training data than ordinary
successful trajectories under the same total budget?

## Why it matters

Terminal success gives weak credit about which intermediate controller decisions mattered.
Counterfactual continuations could improve selection, but extra samples can masquerade as better
credit assignment unless compute and policy semantics are matched.

## Evidence so far

There is no experiment, claim, or result for this question. The named [OpenReview
reference](https://openreview.net/forum?id=k2NrIxm4Do) remains unverified in the source catalog; this
view neither validates it nor claims that it is nonexistent.

## What remains unknown

Deterministic replay of a fixed program is not the same as resampling the root policy. Paired
continuations may add variance, and any gain may come from simply generating more training data.
There is no implementation or bounded GPU duration.

## Smallest discriminating next experiment

Begin with training-only alternative continuations from frozen states. Separate deterministic
program replay from free root resampling, then compare selected data with an ordinary-success set at
matched total generation and training cost. Freeze held-out evaluation, state selection, seeds,
policy version, and counterfactual budget before launch.

## What would justify a stronger claim

Promote only if counterfactual selection improves held-out performance at matched total budget.
Revise the explanation if ordinary extra sampling matches it, and make no novelty claim until the
literature boundary is verified.

