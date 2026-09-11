# Broad equality continuation: independent checkpoint-8 snapshot

2026-09-09. Interim only; fixed final checkpoint 16 remains the primary endpoint.
No checkpoint-12 or later outcomes were read. No source, GPU, model, service,
or live process was changed by this audit.

## Result and important limitation

Validation-8 has **9/16 strict correct answers**, with all 16 terminal answers
observable, graph-verified and schema-valid. The original policy had 5/16;
checkpoint 4 had 4/16. On the same episode coordinates, checkpoint 8 versus
original gives six gains, two losses and eight ties; versus checkpoint 4 it
gives five gains, zero losses and eleven ties. Both-original-and-current
graph-valid pairs number 15, with the same five versus nine successes. The
original infrastructure exclusion is not retroactively repaired.

This is developmental, repeated-context evidence, not a new confirmation or
permission to select checkpoint 8. The eight validation tasks each have two
seeds; sixteen episodes are not sixteen independent contexts.

**High training reward does not mean uniform learning support.** Rounds 7 and
8 each score 22/24, but their 16- and 32-record groups are all-one and provide
no group-relative gradient. Only the eight-row 64-record group contributes
to each of those updates. Earlier in this delta, all-zero ENTY groups also
provide no gradient. Different targets and contexts rotate across rounds,
so the aggregate reward sequence is not a fixed-task learning curve.

## Validation trajectory by length and target

These are unchanged raw strict endpoints, not alternative scoring rules.

| Subset | Original | Checkpoint 4 | Checkpoint 8 |
|---|---:|---:|---:|
| All episodes | 5/16 | 4/16 | 9/16 |
| 32 records | 1/8 | 2/8 | 5/8 |
| 64 records | 4/8 | 2/8 | 4/8 |
| HUM | 2/4 | 1/4 | 2/4 |
| NUM | 1/4 | 0/4 | 1/4 |
| ENTY | 1/4 | 1/4 | 2/4 |
| LOC | 1/4 | 2/4 | 4/4 |

Checkpoint-8 task-level successes, in the frozen 00/01/02/03 target order
HUM/NUM/ENTY/LOC: 32-record contexts score 1/2, 0/2, 2/2, 2/2;
64-record contexts score 1/2, 1/2, 0/2, 2/2. Exact episode IDs, context
hashes, seeds and answers are retained in STEP8_validation-08_RAW.json.

The separate host-gold-only answer-distribution report describes an
evaluation-informed constant of 9 that would hit 6/16 validation episodes.
That descriptive number is not a prospectively deployed model baseline and
does not replace the frozen original comparison. The current 9/16 result
alone does not establish general counting competence or rule out shortcuts.
Reference: ../answer-distribution-controls-2026-09-09/REPORT.md.

## New training attempts, nulls and selected support

Each round planned and recorded 24 attempts. Raw success denominators below
retain every attempt; the round-6 null is not converted into an observed
wrong answer or admitted as a zero-reward training row.

| Round | Correct/planned | Observable; graph-valid | Schema-valid | Selected | Valid homogeneous, unselected |
|---|---:|---:|---:|---:|---|
| 5 | 12/24 | 24; 24 | 21 | 16 | 8 all-zero |
| 6 | 11/24 | 23; 23 | 22 | 15 | 8 all-zero; plus 1 infrastructure null |
| 7 | 22/24 | 24; 24 | 23 | 8 | 16 all-one |
| 8 | 22/24 | 24; 24 | 24 | 8 | 16 all-one |

Observed group rewards and actual selection:

| Round | 16-record group | 32-record group | 64-record group |
|---|---|---|---|
| 5 | HUM 6/8; selected 8 | NUM 6/8; selected 8 | ENTY 0/8; selected 0 |
| 6 | NUM 7/8; selected 8 | ENTY 0/8; selected 0 | LOC 4/7 observable + 1 null; selected 7 |
| 7 | ENTY 8/8; selected 0 | LOC 8/8; selected 0 | HUM 6/8; selected 8 |
| 8 | LOC 8/8; selected 0 | HUM 8/8; selected 0 | NUM 6/8; selected 8 |

Thus 96 new training attempts yield 95 admissible graphs, 47 selected
mixed-group episodes, 48 valid homogeneous unselected episodes (16 all-zero,
32 all-one), and one infrastructure exclusion. Exclusion reasons are distinct;
none of the 48 homogeneous episodes is a trace failure.

The sole new null is round-6 episode
`b1a6c717e3440ede6cd2c7f6ccbac36a6434877e39fc8d92b98bab4361089261`,
training-064-05:location, seed 47398771. It has an empty root reply, incomplete
execution and three physical model requests, all returned. The ACP stderr
localizes a shell-message wait failure: nano `_run_loop` calls
`repl.set_broker_scope`, which calls `_execute_silent`, whose
`get_shell_msg(timeout=30)` raises `_queue.Empty`. The trace terminates with
an internal harness error. No provider/child-request error, budget censoring
or truncated request was recorded. Why the kernel did not respond remains
unknown; this evidence does not attribute it to a model mistake. A targeted
additional read inspected this one raw record's error and stderr, with no
reroll, answer repair or update retry. See STEP8_NULL_DIAGNOSTIC.json for the
raw path, SHA and exact accounting.

## Actual optimizer chain, action masks and native corrections

The auditor loaded the checkpoint-4 anchor adapter once, then only the new
5–8 optimizer/adapter states. All 504 actual Adam parameter-state cursors
equal the respective claimed step; all relevant tensors are finite, and
all 504 adapter tensors change on each consecutive update. Preceding policy
hashes, exact adapter-load equality, optimizer parameter-name order and
COMMIT/state/manifest links agree. This is the same continuous chain, with
no restart at step 4, reroll or reapplied update.

| Actual Adam step | Selected episodes | Root turns | Root action tokens | Consecutive adapter L2 delta |
|---|---:|---:|---:|---:|
| 5 | 16 | 35 | 8,502 | 0.1050882598482365 |
| 6 | 15 | 33 | 7,825 | 0.09786317039182664 |
| 7 | 8 | 21 | 6,028 | 0.09438463940950366 |
| 8 | 8 | 22 | 5,928 | 0.08874940992266787 |

The 47 selected episodes contribute 111 root turns and 28,283 root action
tokens. Child and observation loss tokens remain zero. Exact root-action
suffix masks, native sampled-token logprobs, request/token identities,
capture-to-group bijection, per-turn advantages and correction array lengths
were checked; no behavior likelihood or child credit was manufactured.
The inherited native preflight and physical root/child adapter, request and
sampling provenance checks all pass. The child remains frozen c32de.

All five correction guards were independently recomputed from token-level
log ratios and passed on all four updates:

| Step | Mean absolute log ratio | Sample k3 | Fraction outside [0.5,2] | Removed IS mass | Raw token ESS fraction |
|---|---:|---:|---:|---:|---:|
| 5 | 0.00642914 | 0.00150665 | 0.000705716 | 0.000789702 | 0.993595 |
| 6 | 0.00494657 | 0.000955632 | 0.00102236 | 0.000229250 | 0.997583 |
| 7 | 0.00427389 | 0.000783760 | 0.000497678 | 0.000245737 | 0.997960 |
| 8 | 0.00477282 | 0.000792923 | 0.000843455 | 0.000157846 | 0.998236 |

Bounds are respectively at most 0.1, 0.02, 0.01, 0.01 and at least 0.9.
Passing these guards checks the declared likelihood/correction contract;
it does not certify semantic reasoning or uniform gradient support.

Current checkpoint-8 adapter SHA is
`9f28aa24596c82859001be14d466b710b0100a1287d5ceec20b6a411720a1094`;
optimizer SHA is
`5755c47c57a038b4e9d6459d2b81d0447cc50613b8fee343df03baab1a38062a`.
Full policy closure is in STEP8.json. This BROAD checkpoint 8 is not the
historical eight-update root used in the separate adaptive-pilot design.

## Physical cost of this audited delta

All 1,438 physical native model requests returned: 257 root and 1,181 child.
There are no request-only records, wire errors or unknown usage entries.
The local kernel failure above occurred despite returned model requests.
Native request count is not recursive-session count or independent episodes.

| Stage | Collection seconds | Physical requests (root/child) | Logical prompt | Cached | Uncached | Completion |
|---|---:|---:|---:|---:|---:|---:|
| Round 5 | 234.547 | 264 (52/212) | 258,775 | 243,984 | 14,791 | 25,590 |
| Round 6 | 344.305 | 503 (54/449) | 910,242 | 889,392 | 20,850 | 29,489 |
| Round 7 | 204.164 | 227 (59/168) | 235,833 | 220,480 | 15,353 | 20,291 |
| Round 8 | 184.967 | 238 (57/181) | 238,915 | 226,096 | 12,819 | 17,134 |
| Validation 8 | 120.207 | 206 (35/171) | 192,339 | 178,672 | 13,667 | 11,341 |
| Total | 1,088.189 | 1,438 (257/1,181) | 1,836,104 | 1,758,624 | 77,480 | 103,845 |

Completion tokens split 62,030 root and 41,815 child. Training plus checkpoint
durations for steps 5–8 are 25.586, 24.965, 18.426 and 19.322 seconds, totaling
88.299 seconds. These stage work totals sum to 1,176.489 seconds; they are
not full elapsed campaign/allocation time and omit interstage service and
other orchestration overhead. The existing cumulative budget is unchanged.

## Audit scope, verification and sealed artifacts

The frozen METHOD and STEP1/STEP4 publications remain unchanged. Finalized
STATUS and export manifests were required before each new stage was opened.
The same pinned independent raw scorer reconstructed all 112 new episodes
once; the 40 original episodes were not re-audited. STEP8.json records
83,449 passing assertions and 17.267890 seconds for the main audit, exit 0.

STEP8_SOURCES.json records 3,079 newly cached immutable files, five inherited
hash reuses and five authenticated serving-log prefixes. Each immutable file
was physically read at most once within the main audit. Unlike STEP4's
publication issue, the exact declared prefix bytes were read directly and
cached once; no appended downstream serving-log activity was read or hashed.
Only one already-audited null episode was reopened for the error diagnostic.
Subsequent numerical summaries read the small audit projections, not raw
graphs or checkpoints. Two ad-hoc summary commands initially mishandled a
nested usage dictionary and a nullable schema flag; corrected projection
commands verified the numbers above without rerunning scientific audits.

Seven focused tests pass under the pinned native Python with CUDA hidden:
three root-mask/native-likelihood tests, two inherited log-prefix tests and
two tests of the actual STEP8 bounded-prefix function (cached read and
tamper rejection). Initial discovery under the separate CPU Python passed
the four prefix tests but could not import the three mask tests because
PyTorch is absent there; rerunning in the already-existing native environment
passed all seven. No environment was installed or modified.

Artifacts: STEP8.json, STEP8_SOURCES.json, five STEP8_*_RAW.json projections,
four STEP8_UPDATE_*.json snapshots, STEP8_NULL_DIAGNOSTIC.json,
audit_step8.py, test_step8_prefix.py and STEP8_PUBLISHED.json.
The integrated independently recomputed guards are in STEP8.json; the
per-update helper snapshots retain their earlier, unaugmented fields.

Conclusion: the step-8 validation improvement is real under the frozen raw
endpoint and native/optimizer checks, but small, exposed and uneven by target
and length. Mixed-group gradient support has narrowed to 64-record tasks in
the latest two updates. Continue to the frozen final-16 endpoint; do not
replace it with this intermediate checkpoint.
