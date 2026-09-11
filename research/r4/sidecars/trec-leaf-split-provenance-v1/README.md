# Source-question-disjoint leaf semantics follow-up

Yes: use TREC source train for leaf SFT and construct custom aggregation documents
from **489 cleaned source-test question groups**. Raw train/test are not disjoint.
This is independence from the inspected local fine-tuning/selection inputs—not a
claim about base-model pretraining or benchmark-wide novelty.

| Source | Rows | Normalized question groups | Duplicate groups |
| --- | ---: | ---: | ---: |
| Official TREC train | 5,452 | 5,376 | 68 |
| Official TREC test | 500 | 500 | 0 |
| Pinned OOLONG validated TREC pool | 4,151 | 4,147 | 4 |

TREC train/test overlap on 10 exact strings and 11 normalized groups. One shared
group even has conflicting coarse labels (DESC versus LOC). All 11 are excluded
from both proposed partitions. Normalization uses the official loader's documented
single-byte repair, Unicode NFKC, case-folding, and punctuation/whitespace-insensitive
word tokens. This is not fuzzy/paraphrase matching. No within-source coarse-label
conflicts were found.

The inspected OOLONG `TREC_Coarse(split=...)` ignores `split` and always loads one
validated pool. All 4,151 questions exactly match official TREC train after its
documented `0xf0`-to-space repair. Local training context8 and evaluation context6
are both upstream **validation**, each with 89 source records. They share one
normalized question; context6 also contains one official TREC test question.
Both were audited. The two archived RLVR-e2e task files and the current 8B task
inventory were also checked: their synthetic questions have zero normalized
TREC overlap. No model outcomes were consulted for this partition.

## Smallest defensible protocol

1. Deduplicate by normalized question group, selecting one source representative;
   exclude all 11 train/test collisions bilaterally.
2. Reserve 300 source-train groups outside the **entire** OOLONG validated pool and
   all explicitly inspected prior inputs: five ABBR and 59 from each other class,
   selected by frozen hash order. The remaining 5,065 groups are the training pool.
   Start cheaply with a predeclared 512 or 1,024 training groups and one leaf-data
   SFT epoch; freeze a separate recipe before updating.
3. Keep 489 source-test groups untouched by tuning. A first aggregation set can use
   ten disjoint 48-record documents, leaving nine records reserved. Vary visible
   label-code permutations and deterministic task targets without exposing per-record
   gold. Multiple queries/permutations on one document remain one statistical group.
4. Compare the same frozen step-0 model before/after SFT. Use validation only for
   checkpoint selection. Report canonical leaf-label accuracy/macro metrics and paired
   aggregate correctness, so aggregate error cancellation is visible. “Leaf-only
   intervention” requires frozen controller routing; otherwise call it leaf-data SFT.

The [machine inventory](../../../../ARTIFACTS.md#unpublished-files "Not published: INVENTORY.json") and [proposed partitions](../../../../ARTIFACTS.md#unpublished-files "Not published: PROPOSED_SPLIT.json")
contain exact source hashes, line-number mappings, group hashes and exclusion checks.
Partition ID: `36e7d2e1ad83210f6420a0312ec46e8a8c70d764e9df0e6d631c67f6fd16c764`.

## Provenance and limits

Official [CogComp TREC files](https://cogcomp.seas.upenn.edu/Data/QA/QC/) are
unversioned; train SHA256 is `9e4c8bdcaffb96ed61041bd64b564183d52793a8e91d84fc3a8646885f466ec3`,
test SHA256 is `033f22c028c2bbba9ca682f68ffe204dc1aa6e1cf35dd6207f2d4ca67f0d0e8e`.
The [CogComp HF card/loader](https://huggingface.co/datasets/CogComp/trec/tree/eb1e45c1ba990fecca7cf84b67ce845edbcf49bf)
is pinned at `eb1e45c1ba990fecca7cf84b67ce845edbcf49bf`. Its dataset license is unknown;
the loader's Apache-2.0 code license does not resolve data rights.

OOLONG dataset revision is `f0d59eaf0febf130664cfceb710436c8e3216b2b`
([source](https://huggingface.co/datasets/oolongbench/oolong-synth/tree/f0d59eaf0febf130664cfceb710436c8e3216b2b));
metadata lists validation 1,300 and test 5,200 aggregate tasks, not source-question
partitions. The MIT [repository](https://github.com/abertsch72/oolong/tree/0bb7eabe839218fee7fe8d007f41cfc2fd3ae24c)
and validated pool are pinned at `0bb7eabe839218fee7fe8d007f41cfc2fd3ae24c`;
that is corroborating code, not proven generating-commit provenance. The pinned HF
dataset metadata has no license field; upstream TREC rights remain unspecified.

Only pointed-to prior inputs were checked; other historical source families/revisions
remain unverified. Excluding all official train and the whole inspected OOLONG pool
protects against contexts drawn from those pools, not arbitrary unknown old sources.
TREC is old/public, so pretraining contamination remains unknown. Validation has just
five abbreviation questions under the conservative exclusion, limiting classwise
precision. This audit made no GPU calls and changed no frozen input.
