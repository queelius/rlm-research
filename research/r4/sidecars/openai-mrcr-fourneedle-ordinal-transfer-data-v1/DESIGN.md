---
schema: openai-mrcr-fourneedle-ordinal-transfer-data-design-v1
status: data_only
---

# Four-needle ordinal-transfer cohort

Within the original short criterion (sum of o200k message-content and answer tokens at most 8,192),
hash-rank official four-needle records separately by requested target occurrence. Exclude any exact
core pair or bidirectional target-answer/core overlap with the original short48, long16, or fresh8
cohorts. Greedily retain eight third-occurrence and eight fourth-occurrence rows while enforcing the
same constraints within the new cohort.

Selection uses no model output or prior outcome. It tests later whether the learned first/second
request procedure transfers to third/fourth occurrence requests; it is not a new benchmark or proof
against pretraining exposure.
