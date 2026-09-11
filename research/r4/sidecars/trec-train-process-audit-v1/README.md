# Verified train-only TREC mapping and process audit

Feasibility is positive: every one of the 89 OOLONG context8 record questions matches one
unique row **exactly** in both official TREC training data and the official OOLONG validated
TREC subset. All 89 labels agree. Recomputing all 16 original training aggregate questions
from these record labels reproduces every archived answer. No fuzzy matching, inferred
labels, TREC test download or heldout-context6 lookup was used.

## Provenance

[CONTEXT8_LABEL_MAP.json](../../../../ARTIFACTS.md#unpublished-files "Not published: CONTEXT8_LABEL_MAP.json") preserves each 1-based context record,
date/user, exact question and hash, canonical gold label, TREC fine/coarse label, and source
line numbers. Context UTF8 SHA256 is
`e34eb037dd31a441e6d8332bf6de25801574e997df93965d35994edf4ee1d2ba`.
The frozen tasks came from `oolongbench/oolong-synth`, validation revision
`f0d59eaf0febf130664cfceb710436c8e3216b2b`, then were assigned to this research store's
training/development context group. “Train” here is the local experimental split; the
upstream OOLONG split is explicitly validation.

Primary sources are the [CogComp TREC collection](https://cogcomp.seas.upenn.edu/Data/QA/QC/),
its [category definitions](https://cogcomp.seas.upenn.edu/Data/QA/QC/definition.html), and the
[official OOLONG loader at pinned revision](https://github.com/abertsch72/oolong/blob/0bb7eabe839218fee7fe8d007f41cfc2fd3ae24c/src/data_gen/oolong-synth/datasets_loader.py).
The loader names `CogComp/trec` and loads the validated TREC coarse subset. That pinned
code is corroborating provenance, not proof that this exact commit generated the archived
OOLONG dataset revision. Exact question/label agreement and all aggregate checks are the
stronger local verification.

| TREC coarse | Canonical OOLONG label | Context8 count |
| --- | --- | ---: |
| ABBR | abbreviation | 4 |
| ENTY | entity | 14 |
| DESC | description and abstract concept | 26 |
| HUM | human being | 12 |
| LOC | location | 27 |
| NUM | numeric value | 6 |

Raw assets remain external to source Git in
[/project/alex_phd/research-cache/2026-09-08-literature/trec-context8.6NYSkv](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/research-cache/2026-09-08-literature/trec-context8.6NYSkv/PROVENANCE.json").
The manifest records seven source URLs, exact OOLONG revision, retrieval date, sizes and
SHA256s. Unversioned CogComp assets are identified by content hash, not an invented revision.
The [official HF TREC card](https://huggingface.co/datasets/CogComp/trec) declares an unknown
license. OOLONG's MIT repository license does not resolve upstream TREC redistribution
rights; this acquisition is not a claim of a permissive dataset license. No downloaded
third-party code was executed.

## What the existing rewarded programs actually did

[CHILD_PROCESS_AUDIT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: CHILD_PROCESS_AUDIT.json") aligns only exact child user-message
question arrays with equal-length JSON output arrays, grouped by committed root model call.
Malformed and wrong-length arrays remain distinct failures. Primary correctness requires
the exact six-value canonical vocabulary; separately named alias sensitivity merges only
`description` and `abstract concept`, never silently changes the primary result.

The abbreviation-count success at both SFT and RLVR weights demonstrates error cancellation:

| 1-based record | Official fine label | Canonical gold | Both models' prediction | Binary effect |
| --- | --- | --- | --- | --- |
| 29, alternative names for an animal | ENTY:termeq | entity | abbreviation | False positive |
| 75, expansion of a writer's initials | ABBR:exp | abbreviation | abstract concept | False negative |

Gold abbreviation indices are 7,23,69,75. Both programs predict 7,23,29,69 and receive strict
reward for count4. Their full-record accuracy is respectively 32/89 and 34/89 canonical,
or 56/89 and 58/89 under explicit alias sensitivity. Both emit 36 invalid category names.
This is direct evidence that aggregate outcome reward can accept a materially incorrect
classification process. It does not establish that every successful program is incorrect.

RLVR also produces a correct human-versus-location comparison from two batches requesting
50/39 labels but returning 52/33; those 85 outputs cannot be defensibly aligned to 89 records.
The complete mechanisms and calls are linked in the
[SFT](../../../../ARTIFACTS.md#unpublished-files "Not published: ../recursive-call-example-v1/analysis/SELF_SFT_REPORT.md") and
[RLVR](../../../../ARTIFACTS.md#unpublished-files "Not published: ../recursive-call-example-v1/analysis/RLVR_TIS_REPORT.md") reports.

## Ranked smallest follow-ups, not heldout selection

1. The approved next CPU-prepared leaf probe crosses the existing label-list prompt with
   concise generic category definitions and server-enforced JSON enum/exact cardinality:
   18 fixed batches of at most five records, four arms, one seed, 72 calls. It separates
   label semantics from output syntax/coverage without changing a full RLM harness or
   current training admission rules. Gold is scorer-only; no labeled examples enter prompts.
2. After that result, a six-rollout train-only counterfactual can compare original context,
   deletion of false-positive record29, and deletion of false-negative record75, at two fresh
   paired seeds and the same executable-example prompt/weights/budgets. Recompute context
   record-count headers and gold exactly: expected abbreviation counts are 4,4,3. Holding
   the observed erroneous record assignments fixed predicts 4,3,4 instead. A successful
   replan must separate these patterns; simply reusing the old labels cannot pass all three.
   This is a selected mechanism stress test, not new-context transfer. Proposed GPU shape:
   one already-loaded 4B model on one A10040GB, at most four concurrent episodes, 15-minute
   cap, atomic per-episode checkpoints. It is ranked only, not prepared or launched here.

The 89 questions are not 89 independent contexts, and these prompts are selected using
observed development failures. Any later process-supervised or counterfactual RLVR update
needs a new explicit training specification; this audit changes no reward/admission rule.
