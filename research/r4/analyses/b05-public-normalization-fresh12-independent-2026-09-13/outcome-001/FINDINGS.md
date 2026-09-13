# Fresh replication: normalization improves selection, with a width limit

The independent [native/public audit](REPORT.json) passes with zero issues. All 48 calls are available, semantically valid JSON ID sets, and stopped normally. Exact frozen base/no-adapter model, prefixes, seeds, decoding, saved responses and scores match; canonical JSON digests and raw response bytes were checked separately. All 12 new public roots were regenerated from their prospective seeds, no prior root/candidate-ID overlap was found, and all 130 retained candidates/effective fields match the original public tables. No model output was repaired or executed.

Unordered exact improves **1/24 → 9/24**, with **8 wins, 0 losses, 1 both correct and 15 both wrong**. Wins occur in **5 of 12 stage contexts**, not eight independent contexts. All nine normalized exact answers are at width 6. Widths 12 and 20 remain zero exact. Strict sorted exact is **0 → 2**; seven normalized semantic exact answers remain unsorted. The strict gains are both seeds of `root_1bd39907f7890a`.

| Frozen subgroup | Contexts / paired seeds | Exact raw → normalized | Mean BA raw → normalized |
|---|---:|---:|---:|
| History 1, width 6 | 2 / 4 | 1/4 → 4/4 | .771 → 1.000 |
| History 1, width 12 | 2 / 4 | 0/4 → 0/4 | .500 → .885 |
| History 1, width 20 | 2 / 4 | 0/4 → 0/4 | .483 → .708 |
| History 3, width 6 | 3 / 6 | 0/6 → 5/6 | .578 → .972 |
| History 3, width 12 | 3 / 6 | 0/6 → 0/6 | .529 → .810 |

History-1 total is 1→4/12; history-3 is 0→5/12. These groups contain different newly generated instances and different width mixtures. This is **not a causal estimate of increasing history depth**. Only applied-change history varied; check revisions stayed at one. The old exposed held9 result (0→4/18, two successful contexts) remains separate and is not pooled into an IID sample.

## Metrics and cost

All 24 sets in each arm are valid, with no unknowns or invalid-known rows. TP/FP/FN/TN change **130/76/28/26 → 150/35/8/67**. There are 158 repeat-weighted positive and 102 negative candidate labels per arm (260 total; 130 distinct candidate records). Micro precision is 130/206=.6311 → 150/185=.8108; recall is 130/158=.8228 → 150/158=.9494. Mean per-set BA is .56905 → .87793, each denominator 24. This macro mean is not BA computed from pooled confusion counts; a stage with only positive labels uses the predeclared single-present-class rule.

BA improves in 20 paired seeds, ties in two, and falls in two. Both declines are the same width-20 context, whose normalized output selects all 20 candidates.

Natural cost is one model call per answer in both arms; 48 physical calls total. Input tokens fall **101,706 → 48,798** (52.0%); output tokens **3,400 → 3,047**; total **105,106 → 51,845**. No usage fields are unknown. Owner elapsed **117.622 seconds**, complete, runtime-qualified and released. Input length and explanatory wording jointly change with representation; this is not a token-matched intervention.

## All 12 cases, checked inertly

The [mechanism JSON](MECHANISM_REVIEW.json) links every pair's unchanged ID sets, omissions, false positives and public-policy facts. Counts below are false positives / missed eligible IDs; semicolons separate the two seeds.

| Context suffix | History / width | Raw FP/FN → normalized FP/FN | Mechanism |
|---|---:|---|---|
| `70ba82eaf06498` | 1 / 6 | 1/0→0/0; 0/0→0/0 | Removes one ineligible ID at seed 0; preserves the existing exact answer at seed 1. |
| `d0749cf960bc6d` | 1 / 6 | 1/1→0/0; 1/1→0/0 | Replaces an ineligible ID with a previously missed eligible one at both seeds. |
| `92162391bed7c0` | 1 / 12 | 3/1→0/1; 4/1→0/1 | Removes all false positives but misses a different eligible ID. This is still a completeness error. |
| `fb91e16740bd1d` | 1 / 12 | 3/3→1/0; 3/3→3/0 | Restores full recall; one or three explicitly failed-check candidates remain. |
| `bb66f545a632ec` | 1 / 20 | 8/1→10/0; 8/1→10/0 | Returns all 20 candidates despite ten explicit check failures; both BA declines. |
| `6d544619f49da7` | 1 / 20 | 7/5→0/1; 7/2→0/3 | Removes every false positive, but eligible omissions remain; one seed loses recall despite better BA. |
| `1bd39907f7890a` | 3 / 6 | 1/1→0/0; 1/1→0/0 | Correct replacement at both seeds; both outputs also satisfy sorted format. |
| `9a3822636b8c0f` | 3 / 6 | 0/1→0/1; 0/1→0/0 | All six candidates are eligible. Seed 0 misses a different ID; seed 1 restores completeness. |
| `020af699f9bfb4` | 3 / 6 | 1/0→0/0; 1/0→0/0 | Removes the only ineligible candidate at both seeds. |
| `6f1927c98cd1c7` | 3 / 12 | 4/0→2/0; 4/0→2/0 | Full recall, but a failed-schema candidate and a below-minimum-capacity candidate remain. |
| `953fba31fff9de` | 3 / 12 | 4/1→3/0; 4/1→2/1 | Fewer false positives, but two or three failed-schema candidates remain; second seed still misses an eligible ID. |
| `77a2119505f24a` | 3 / 12 | 5/2→1/0; 5/1→1/0 | Restores full recall and removes most false positives; one below-minimum-capacity candidate remains. |

The remaining 35 repeat-weighted false positives comprise 31 failed-check selections and four below-minimum-capacity selections. The single all-candidate width-20 context contributes 20 of the 35. These violations are visible in the effective records: further arithmetic/join offload alone cannot explain them away. Conversely, two wider contexts produce only eligible IDs but omit required ones. Selection filtering and exhaustive list production both remain bottlenecks. These are observable output facts, not inferred hidden reasoning.

## Decision and future questions—no new experiment prepared

The positive normalization effect replicates on fresh same-family instances, including greater change history, while exact completion remains sharply width-limited. This supports harness-side mechanical preprocessing as useful; it does not establish learned delegation, recursion, or a new algorithm.

For a later research session: can per-candidate decision accounting separate failure to apply an explicit false check from failure to enumerate every eligible ID? Can a controlled representation/length comparison determine how much benefit comes from resolved joins versus shorter, clearer input? Neither question is implemented or queued here. Stop after this accepted comparison and preserve the audit.

Provenance: native REPORT SHA `14f5b5835cbbc04f3cc55769c807dc2d18c00aedafc1b0fd14ac1877082243a1`; SUMMARY `eacae8f02e7189116e12fdc21e186c2619eaf253999f88c5c3c34b1592038f7f`; mechanism `7ce7f1d787cc76372de62ac04aee93025021b21cf0e7d062520af531356811ad`. Full native source hashes and the separate post-outcome mechanism wrapper receipt are retained alongside this note.
