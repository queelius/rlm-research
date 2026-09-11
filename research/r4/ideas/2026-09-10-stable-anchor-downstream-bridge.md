---
date: 2026-09-10
status: design_only_contingent_not_implemented
gpu_authority: none
proposed_calls: 80 model episodes minimum; 16 fixed leaf acquisitions plus 64 root episodes
proposed_gpu: one A100
proposed_outer_cap_seconds: 1800
---

# Can a better correspondence encoding survive one downstream join?

## Plain-language question

Suppose two leaf prompts classify the same 48 sentence pairs. One uses ordinary row numbers; the
other uses the stable encoding that wins the pending correspondence gate. Before the root sees
anything, a strict broker converts either answer into the **same** public
`record_id -> NLI label` map. Does the more accurate leaf map then improve a varied count or weighted
sum, or does the root lose the benefit while loading and reducing the map?

This is conditional. Implement it only if the opaque or permuted-numeric arm satisfies its own
already-frozen downstream-promotion gate against sequential numbering. If opaque passes, admit
opaque; otherwise admit permuted numeric if it passes. This opaque-first priority is fixed before
outcomes and never chooses whichever observed effect is larger. If neither stable arm passes, retire
this design rather than substituting the best-looking arm after outcomes.

## Worked example

The root sees records such as:

```text
record r17: user=Ada, weight=7, premise="A dog is running.", hypothesis="An animal moves."
record r42: user=Ben, weight=3, premise="The room is empty.", hypothesis="A person is inside."
```

and asks:

> Among Ada's records, sum the weights of records whose NLI relation is entailment.

The sequential leaf might internally receive rows `0, 1, ... 47`; the stable leaf might internally
receive opaque keys such as `k91ab...`. Neither internal key is visible to the root. The broker
validates the complete leaf answer and returns, in both arms, the same-shaped object:

```json
{"r17": "entailment", "r42": "contradiction"}
```

If the stable leaf fixes a late-row label, the host reducer and supplied-plan root should change by
exactly that record's contribution. The free root may still fail by never requesting the map,
discarding it, filtering the wrong users, summing the wrong field, or returning malformed prose.
Those are different stages and must be scored separately.

## What has already been established

This experiment must not be described as the first root/map bridge.

- The completed fresh-context MNLI leaf replication found matching record tags at 639/768 labels
  versus 398/768 for a constant-tag control, positive in all 16 paired contexts. That establishes a
  leaf-level correspondence package on the same source family, not that a root can use the improved
  map. Its complete three-label premise groups also make some global aggregates insensitive to
  record swaps, which is why this proposal selects one row per group and freezes varied answers.
- The completed Bridge32 comparison already projected array and object child outputs into canonical
  maps. On four exposed TREC contexts, count label agreement improved from 567/628 to 593/628 but
  exact count stayed 1/8 in both arms; checksum stayed 0/8 in both. Most eligible calls were width
  four and checksum had both-arm uptake in only 3/8 pairs. Stronger RL4 and high-rate-SFT roots still
  gave 0/8 checksum in both formats; the high-rate root gave 3/8 count in both. Thus map shape alone
  did not establish downstream benefit.
- Clarity96 showed that accurate public field descriptions helped, but only 16/96 episodes actually
  executed a supplied-map count. A final agreeing with a map did not imply that the root used it.
- Semantic-map48 made file retrieval much more common (7 to 19 map reads) but changed strict success
  only 5/24 to 7/24, with semantic map errors and root execution failures both visible.
- In the supplied-plan ceiling, the child got 1129/1280 labels right but exact J1 answers were 0/8;
  oracle labels under the same reducer were 8/8. Rechecking and direct sufficient statistics did not
  reliably close that gap.

The new information is therefore narrow: whether a **prospectively winning long-batch leaf
correspondence encoding**, hidden behind an identical canonical root API, changes an exact
downstream result on new varied-gold metadata compositions. It also locates any loss between leaf
accuracy, map delivery/consumption, executed computation, and strict finalization.

## Frozen factorial and units

Use eight new 48-record contexts, two per MultiNLI validation-matched genre (`government`, `slate`,
`telephone`, `travel`). Each context has two questions:

1. `count`: count records with a fixed NLI relation whose `user` belongs to a visible user subset;
2. `weight`: sum visible positive integer `weight` for the analogous selected records.

Cross these with two internal leaf encodings and two root policies:

- leaf: sequential numeric keys versus the single stable arm admitted by the upstream gate;
- root: exact supplied one-layer plan versus freely chosen root actions.

This gives `8 contexts x 2 questions x 2 leaf encodings x 2 root policies = 64` root episodes. Use
one frozen root seed per context-question, identical across the four paired cells. Context, not the
64 episodes or 48 records, is the independent clustered unit.

Acquire each context's complete 48-label map once per leaf encoding before root execution: 16 fixed
leaf model calls. Reuse that exact authenticated map for both questions and both root-policy cells.
Thus the leaf comparison has equal, fixed physical acquisition cost and cannot be changed by root
uptake. The root panel has 64 fixed episodes with identical caps and balanced order; adaptive root
turn counts are measured costs, not falsely called equal FLOPs.

## New context construction and the anti-constant-answer rule

Take a fresh snapshot of every named executed or prepared MultiNLI source-group inventory before
selection. Exclude all of them, including the 256 premise groups in the pending stable-anchor study.
Use the pinned `nyu-mll/multi_nli` validation-matched parquet at revision
`da70db2af9d09693783c3320c4249840212ee221`, SHA-256
`350c26950b55f460b50d36c76aef87d64b49c78812d7abf7bf97e5fede10f186`.

Eligibility may use gold labels only to identify conflict-free complete three-label premise groups;
disclose this. Rank eligible groups within genre by `SHA256(master || normalized premise-group)`.
For each selected group, choose exactly one of its three rows by a second hash over public text, not
by label, length, model outcome, or desired answer. Take the first 96 eligible groups per genre and
split them into two ordered 48-record contexts. If any genre has fewer than 96 after the fresh
exclusion snapshot, preserve the insufficiency receipt and stop—no relaxed exclusion or replacement.

Assign four public users and weights 1..9 by separate hashes of the public record ID. Choose each
question's relation and user subset by hash before reading panel gold. This breaks the old artifact
where every complete premise group contributed exactly one of every NLI label. Gold is then used
only for a prespecified **panel eligibility check**: each operator's eight answers must contain at
least four distinct values, no value may occur more than three times, and at most two answers may be
zero. If this fixed panel fails, report insufficiency and do not rerank contexts, alter metadata, or
search queries. Gold never enters a prompt, API response, model selection, or repair.

Proposed master seed: `998431001`. Leaf seeds are `998431101 + context_index`. Root seeds are
`998431301 + 10*context_index + query_index`, reused across encoding and plan cells. Freeze exact
records, metadata, queries, request bodies, body/token hashes, root prompts, dispatch order, and
planned NULL inventory before service startup.

## The interface intervention

The two leaf calls differ only in the already-qualified encoding package:

- sequential: matched input/output row numbers in display order;
- stable: the one admitted opaque or permuted-numeric key assignment, fixed independently of gold.

Output order remains displayed-record order. Structured decoding may force key-bearing syntax and
key tokens, so this tests an encoding package, not freely learned key copying or an attention
mechanism.

For each valid complete leaf answer, a strict host broker maps its internal keys back to the frozen
public record IDs and emits one canonical JSON object in public record order. Sequential and stable
root-visible maps must obey the same serialization, schema, key order, label vocabulary,
filename/API name, and documentation; differing predicted labels may of course make their values
differ. Preserve raw leaf completions and log-probabilities; never rewrite a label. Duplicate,
missing, extra, or invalid keys make that leaf acquisition observed-invalid. Unavailable leaf calls
remain NULL. There is no retry or fallback to the other encoding.

The root-facing API is exactly `classify_all() -> {public_record_id: nli_label}` in every cell. It
returns the already-acquired map; it cannot make a new model request or reveal internal leaf keys.
The root otherwise receives the same 48 public records, user/weight metadata, query, tool inventory,
sampling, and answer contract.

The supplied-plan prompt gives the exact one-layer procedure: call `classify_all()` once, select by
the requested relation and users, apply `len` or `sum(record.weight)`, observe the scalar, and return
only `Answer: N`. It supplies no labels or answer. The free prompt documents the identical API and
task but gives no decomposition or reducer. This is a supplied-plan instruction versus free-policy
comparison, not a claim that the plan was learned or that prompt bytes are identical.

Use the fixed QS6 root checkpoint and the same released 4B leaf checkpoint in all cells. Do not add
training, repair, verifier calls, direct-statistics prompts, or a second root model.

## Prospective measurements

Score every planned cell and preserve observed invalid versus unavailable NULL.

1. **Leaf:** complete schema validity; overall and late-16 label accuracy; per-context stable-minus-
   sequential accuracy; false-positive/false-negative counts by relation. Dataset labels are a
   frozen oracle, not human semantic review.
2. **Map delivery and consumption:** API invoked; complete canonical map delivered; map retained in
   actual root state; query-relevant IDs read from that map. A broker log or file open alone is not
   consumption.
3. **Computation:** actual executed count/sum from the delivered predicted map; scalar agrees with an
   independent host reducer over that same predicted map. Do not execute generated code during
   audit. Also report the host predicted-map scalar separately as the leaf-to-task ceiling.
4. **Final:** strict whole reply `Answer: N`; agrees with the last actual executed scalar; dataset
   correct; and `correct AND faithfully performed`. Coincidental zero or correct answers without
   the requested computation do not pass the faithful measure.
5. **Availability and cost:** all 16 leaf acquisitions, all 64 roots, every physical root turn,
   input/output/cached/uncached known and unknown usage, elapsed service phases, failures, and shared
   map provenance. Reused maps are charged once physically and disclosed as shared evidence for four
   correlated root episodes, not four independent leaf calls.

Primary descriptive contrasts are stable-minus-sequential in the supplied-plan cells for (a) the
host predicted-map scalar and (b) root correct-and-performed. Report the same contrast in free cells,
the supplied-minus-free contrast within each encoding, and the plan-by-encoding interaction. Keep
count and weight separate before any pooled summary. Report paired context tables and conservative
NULL bounds; do not replace the primary with complete cases or uptake subsets.

## Gates fixed before implementation

Admission requires the upstream stable arm's own frozen gate. After admission:

- **Leaf mediation gate:** stable improves all-record label accuracy by at least 10 percentage
  points, is positive in at least 6/8 contexts, and has no validity/availability disadvantage.
- **Task-sensitivity gate:** the stable host predicted-map scalar gains at least 3/16 exact
  context-question answers over sequential, with gains represented in both count and weight and no
  more than one loss.
- **Supplied-root gate:** stable gains at least 3/16 correct-and-performed supplied-plan endpoints,
  with positive net effect in at least 5/8 context clusters and no availability disadvantage.
- **Free-root promotion:** stable gains at least 3/16 correct-and-performed free endpoints and the
  lower NULL bound remains positive. This promotes the normalized interface for later root training.

Interpret combinations rather than forcing one success label:

- leaf passes, host scalar fails: the new queries are insensitive to corrected labels; retire this
  panel as downstream evidence;
- host scalar passes, supplied root fails: aggregation/finalization still destroys a real leaf gain;
- supplied root passes, free root fails: prioritize plan/consumption training, not another leaf
  encoding study;
- free root also passes: promote to a new-context or second-model replication before a publication
  claim;
- leaf mediation fails: do not use downstream noise to rescue the stable-key claim.

These are candidate-promotion rules for an exploratory eight-context panel, not significance tests.

## Compute and stopping

One A100; one qualified base with the fixed QS6 root adapter and released leaf route. Four workers,
90 seconds per model request, 2,048 root output-token cap, 3,072 leaf output-token cap, and 8,192
context cap. Proposed envelope: 1,800 seconds outer, 1,770 owned, 1,650 work, with service startup
and release inside the common budget. There are 16 fixed leaf calls and 64 fixed root episodes; root
turns are bounded by the existing runtime and reported exactly. No retry, refill, outcome-selected
rerun, best checkpoint, or automatic answer fallback.

Do not implement or launch until the stable-anchor terminal audit identifies an admitted arm and
MAIN approves the frozen inventory and same-API transport fixture.

## Evidence inspected

- `analyses/root-child-representation-bridge-live-2026-09-09/REPORT.md`, SHA-256
  `b07584134aeac387328f557c2dd976b25a1e3d9e345363dee8397ca2df64f206`.
- `analyses/leaf-mnli-new-context-correspondence-live-2026-09-10/REPORT.md`, SHA-256
  `187601eaf6a44f45a4b8b4ed35de35ad0c20aaeff039a2a6f8b3025e5742bf31`.
- `analyses/root-child-representation-bridge-panel-live-2026-09-09/PANEL_METRICS.json`, SHA-256
  `d79203d72b2c02322aa14dbffaddf628dc4ea78ae791f6d6fef78a25b2d05ca9`.
- `analyses/root-map-contract-clarity-live-2026-09-09/REPORT.md`, SHA-256
  `ad8f2d939a2e76e921988e6cc7a4ba70ebce27a613497aec5c6cdd93e9391c2e`.
- `analyses/root-semantic-map-externalization-live-2026-09-10/REPORT.md`, SHA-256
  `9b019e728a397be0ad799fa12f4355871410861e90c28a80bca708b187fd2334`.
- `analyses/root-lambda-supplied-plan-ceiling-live-2026-09-10/REPORT.md`, SHA-256
  `4ccb7a60082d0bc76e8de88f5500514efca7ba61cf4afd42931a6c7ec04f892e`.
- `analyses/root-j1-sufficient-statistics-live-2026-09-10/REPORT.md`, SHA-256
  `2f4066b9d1e8e3c753c206b8e42b0c0cb3aa4216c2b24af84aa44e47ea2801b2`.
- Pending stable-anchor design and inventory snapshot, SHA-256 `d255ae7f...fcbbfde7` and
  `399ff6e8...e2c3de`. No pending outcomes were read.
- `ideas/2026-09-09-correspondence-to-rlm-next-options.md`, SHA-256
  `4d4e6f3e89b5c0d438b3bcf9657efd0aa7a6a6db5cd7fb3dcc33dcf7f6e502a9`.

No new human semantic review was performed. This document proposes no GPU or service action.
