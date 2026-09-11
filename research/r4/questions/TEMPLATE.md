---
schema_version: "rlm-question-card-v1"
id: "rq:<stable-id>"
title: "<plain-language research question>"
status: "<catalog status>"
updated_utc: "<ISO-8601 UTC timestamp>"
evidence_cutoff: "<sealed catalog cutoff>"
source_catalog:
  path: "/absolute/path/to/CATALOG.json"
  sha256: "<64 lowercase hex characters>"
related_questions: []
claim_ids: []
reports: []
publication_readiness: "not_publication_ready"
---

# <Plain-language research question>

## Question

State the falsifiable question in one complete sentence.

## Why it matters

Explain the scientific decision this question changes.

## Evidence so far

Separate supporting observations from contrary findings. Distinguish the sealed catalog snapshot
from later sealed updates, and say explicitly when there is no experiment or no result.

## What remains unknown

Name the principal alternative explanations, missing baselines, and scope boundaries.

## Smallest discriminating next experiment

Describe the smallest comparison that can distinguish the leading explanations, including the
sampling unit, fixed inputs, primary metric, compute cap, and artifact boundary when known.

## What would justify a stronger claim

State the evidence needed to promote, revise, or retire the claim. Do not declare publication
readiness here.

