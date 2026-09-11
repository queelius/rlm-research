# Fresh TREC/SST/AG replication: the requested 12-cluster grid is infeasible

September 9, 2026. Data feasibility only; no records selected/reserved, model calls,
study implementation, or pending outcomes inspected.

Four genuinely new TREC clusters cannot be assembled from the authoritative
benchmark pool. The completed leaf training/readouts already used 5,854 of 5,865
normalized train/test groups. Of the remaining 11 cross-split duplicates, one has
conflicting coarse labels and a different one appeared in an old RLM context.
**At most nine eligible groups remain before any further historical exclusions.**
No complete 64-record cluster is possible, much less four. New permutations or
compositions of exposed TREC questions would not solve this source-freshness limit.

## Measured availability

| Public source | Rows / normalized groups | Used or reserved in bounded input scan | Remaining eligible |
|---|---:|---:|---:|
| TREC train + test union | 5,952 / 5,865 | 5,854 completed SFT groups, plus known old exposure | **At most 9** |
| SST-2 validation | 872 / 872 | 864 | **8** |
| SST-2 upstream training | 67,349 / 66,978 | 0 exact matches | **66,973** after five conflicting-label groups |
| AG News test | 7,600 / 7,600 | 256 | **7,344** |

The SST validation count independently reproduces the earlier failed fresh-screen
result: three disjoint 256-group leaf pools plus 96 reserved root-curriculum groups
leave eight, not another four contexts. Reservations remain excluded even if their
optional experiment has not run. The raw upstream pool's presence in an acquisition
manifest is **not** research exposure.

The bounded scan traversed all six `/project/alex_phd/runs` roots for named
DATA/PUBLIC/GROUPS/SPEC/CONTEXTS/RESERVATIONS inputs, with 25 matching catalogs and
no oversized candidate skipped. It avoids outputs, qualifications, source code,
and provenance/dedup inventories that enumerate unselected upstream rows. Exact
file hashes and per-catalog counts are in [FINAL_COUNTS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: FINAL_COUNTS.json")
and [FINAL_SOURCE_HASHES.json](../../../../ARTIFACTS.md#unpublished-files "Not published: FINAL_SOURCE_HASHES.json").

This is not an exhaustive positive nonexposure certificate for arbitrary embedded
prompts, unlisted input filenames, or external repositories. Those remaining
crosswalks must be resolved before calling selected AG/SST records globally new to
the research program. The TREC **negative upper bound** needs no such exhaustive
scan: additional exclusions can only lower it.

## Acquired SST training bytes and source caveats

Only one additional public Parquet was acquired: Stanford's pinned SST-2 training
split, revision `8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb`, 3,110,458 bytes,
SHA256 `c7921283b75a42e685f50edecb96798607ea0fcbfd0739ee8975f22c12d55f09`.
It is external to Git at
`/project/alex_phd/research-cache/datasets/sst2-train-feasibility-20260909/`;
ACQUISITION.json records the immutable URL, retrieval time and checksum. No remote
loader/code was executed; only installed PyArrow read the data.

SST training has 371 excess normalized duplicate rows and five conflicting-label
groups; exclude the latter as whole groups without choosing the preferred label.
There are zero exact normalized training/validation overlaps. **Training rows are
not interchangeable with the old full-sentence validation population:** 11,171
eligible groups have only one or two whitespace-separated words. Treat a direct
sample as a phrase/text-unit sentiment replication, not four guaranteed complete
sentence clusters. Parent-sentence/subphrase overlap and near duplicates are not
resolved by exact normalized hashing. For a full-sentence claim, first acquire and
map the original Stanford sentence IDs/split annotations; do not silently select
longer phrases as a sentence substitute.

Normalization: NFKC + casefold + whitespace collapse for SST/AG; TREC uses the
historical NFKC + casefold + word-token grouping. Both are SHA256 over UTF-8.
TREC's pinned parser replaces its single 0xf0 source byte with a space; no labels
were inferred or repaired. Original source rows/indexes and all 11 TREC remainder
members are retained in machine evidence. News article/event near-duplicates are
not guaranteed absent by exact hashing.

Underlying TREC, SST and AG data licenses remain unknown/unconfirmed in the pinned
source records. HF loader Apache-2.0 and OOLONG software MIT do not grant underlying
dataset redistribution rights. These are old public benchmarks: new to our
research is not unseen in model pretraining/post-training.

Primary source links: [SST pinned card](https://huggingface.co/datasets/stanfordnlp/sst2/blob/8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb/README.md),
[Stanford sentiment source](https://nlp.stanford.edu/sentiment/),
[AG pinned card](https://huggingface.co/datasets/fancyzhx/ag_news/blob/eb185aade064a813bc0b7f42de02595523103ca4/README.md).
Cards and original acquisition manifests were inspected from the authenticated
existing cache; no new license or model-cleanliness claim is inferred.

## Smallest useful choices for main's decision

1. **Recommended: eight new-source clusters, two tasks.** Four AG test clusters
   plus four SST training text-unit clusters, 64 unique groups each. First finish
   the positive exposure crosswalk; use label-independent hash ordering, exclude
   full conflicting groups, and freeze complete text without model-based filtering.
   Two released checkpoints × eight contexts × two seeds × three output forms
   gives **96 calls**. Preserve meaningful-minus-constant primary separately by
   task/model, exact matched source order within a model, and honest template
   differences across models. If full sentences are essential, use Stanford's
   sentence-ID mapping before this option rather than pretending phrases qualify.
2. **Keep 12 contexts, change the freshness claim.** Reuse four explicitly exposed
   TREC clusters as a historical anchor, alongside eight newly checked AG/SST
   clusters: **144 calls**. Report TREC separately; no pooled '12 fresh clusters'
   or independent TREC source-replication claim.
3. **Require three genuinely fresh task sources.** Replace TREC with a separately
   approved classification dataset and explicitly call it task transfer. This
   needs acquisition/contract qualification; it is not the smallest ready option.

No new seeds, prompts, selection, model configuration, budgets or launch command
are frozen here. Those are a later design decision, not an adaptive scheduler.

## Audit correction and reproducibility

An initial diagnostic scan (`FEASIBILITY.json`) counted raw-pool provenance nested
inside DATA files and therefore falsely marked all 872 SST validation groups
excluded. This was caught before publication. The corrected scanner explicitly
skips provenance/dedup/acquisition branches and reproduces **864 excluded, eight
remaining**. The old diagnostic is retained but **superseded by FINAL_COUNTS**;
it is not evidence of actual use. This distinction is the requested raw-source
versus experiment-membership boundary, not a newly spent reservation.

`inspect_pools.py` and `acquire.py` reproduce the data-only work; FINAL_MANIFEST
seals the published report and corrected counts. No old sources or research
outputs were edited.
