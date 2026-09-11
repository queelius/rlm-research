# Research evidence snapshot

Nine sealed reports connect to eight questions, thirteen claims, six decisions and three publication candidates. Evidence cutoff: 2026-09-09T17:32:51.282711+00:00. This is a bounded report-level synthesis, not a new raw audit or complete campaign catalog.

Read [three claim cards](CLAIM_CARDS.md), [decisions](DECISIONS.md), then [CATALOG.json](CATALOG.json). Exact source hashes are in [SOURCE_MANIFEST.json](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCE_MANIFEST.json"); checks are in [VALIDATION.json](../../../../ARTIFACTS.md#unpublished-files "Not published: VALIDATION.json"). The [earlier 01:35 dossier](../cross-experiment-synthesis-2026-09-09/README.md) remains unchanged with its own identifiers.

The main distinction is component versus whole-task evidence. Source-linked labels are robustly useful in component controls, but root reduction, scope and syntax can prevent end-to-end gains. Three candidates remain exploratory/promising, never confirmatory-ready. Repeated seeds are within-context checks, not new independent tasks. New selected records do not mean unknown to helper training or pretraining; released models are instruction-posttrained, not untouched bases.

Example searches from this directory:

```sh
jq '.claims[] | select(.kind=="inference") | {id,statement,not_justified}' CATALOG.json
jq '.experiments[] | select(.id=="exp:fresh96") | {exposure,metrics,native_cost}' CATALOG.json
jq '.decisions[] | select(.additive_correction) | {id,previous_interpretation,decision_changed}' CATALOG.json
jq '.publication_candidates[] | {id,status,missing_decisive_experiments}' CATALOG.json
jq '.questions[] | select(.status | startswith("deferred")) | {id,readiness}' CATALOG.json
```

All nine reports were read completely. No new raw audit was performed; the curator authored some common harness code and the shifted/coverage audits, so this synthesis adds no independent replication. Local source hashes bind what was summarized. Literature verification is explicitly attributed to MAIN; OpenReview k2NrIxm4Do remains unverified, not asserted nonexistent.

Costs distinguish optimizer, training, collection and outer wall time. Unmeasured idle time is null, not inferred from elapsed time. Different historical availability rules remain explicit, with later broker-null corrections linked rather than old scores erased.

Only these six snapshot files were created. No user ideas, global docs, queue, database, raw output, accepted source or old seal was changed. No GPU operation occurred. MAIN owns cross-node handoff. Pending new bridge-policy and complete-demonstration outcomes are outside the cutoff. Missing future work: full campaign coverage, new outcome ingestion, independently replicated claims and finalized composition pilot. None blocks this completed first curation slice.

