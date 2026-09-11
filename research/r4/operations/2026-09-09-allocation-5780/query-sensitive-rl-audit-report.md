# Independent audit: query-sensitive root RL

Audit cutoff: 2026-09-09 23:54 UTC. The campaign completed and released its GPU. The owner reports
no error or unreleased service (SHA
`30d2681d138948f7af1844981bd2f96e03a6e5e153a7dc6667922799953e8a49`).

## Answer

Ten genuine root-policy Adam updates did **not** produce persuasive evidence of transferable batch
operator learning. Planned-denominator strict accuracy rose from 2/48 for unchanged low66c to 4/48
for the trained checkpoint, but every trained success had gold answer zero. Among exact-format
responses, the trained policy emitted zero 22/25 times, versus 15/23 for unchanged. The three paired
trained wins were all zero-gold answers; the one nonzero unchanged success was lost because its
trained mate was NULL. Neither final arm called a child. The observed difference is therefore most
consistent with a stronger short/zero-answer tendency, not learned acquisition, scope, or reduction.

Operationally, the trained arm was worse: 36/48 endpoints were available versus 46/48 unchanged.
Eleven of its twelve NULLs were in the ambiguity-affected `all` scope, usually after 16--18 root
calls. This is compatible with a learned looping/termination failure on that wording. The primary
scores and all NULLs remain unchanged.

## Paired readout

| arm | strict / planned | available | exact format | zero-gold successes | NULL bound |
|---|---:|---:|---:|---:|---:|
| unchanged low66c | 2/48 | 46/48 | 23/48 | 1/2 | 2/48--4/48 |
| trained step 10 | 4/48 | 36/48 | 25/48 | 4/4 | 4/48--16/48 |

The 48 same-input pairs contain three trained wins, one trained loss, one both-correct pair, and 43
both-wrong pairs. Thirty-four pairs have both endpoints available; twelve are unchanged-only and two
trained-only. None is NULL in both arms. All 48 pairs have identical task objects, system text, user
text, coordinate, and sampling seed across policies.

Held-out cells account for 36 pairs: unchanged 2/36 with 35 available; trained 3/36 with 27
available. Supported cells account for 12: unchanged 0/12 with 11 available; trained 1/12 with 9
available. All three trained held-out successes and the one trained supported success are zero-gold.
Thus neither split shows a nonzero operator success for the trained policy.

By frozen held-out family:

- `count-union`: unchanged 0/12, trained 1/12; both have 12 available. The trained success is zero.
- `weight-single`: unchanged 1/12 with 11 available, trained 2/12 with 11 available. All three
  successes are zero.
- wording-confounded `distinct-all`: unchanged 1/12 with 12 available, trained 0/12 with only 4
  available. The unchanged success is nonzero (`Answer: 3`).

Across the six unaffected `single`/`union` scope cells together, unchanged is 1/32 with 31
available and trained is 4/32 with 31 available. This availability-matched planned difference still
consists entirely of additional zero-gold successes. The 16-record stratum is 2/32 versus 3/32; the
32-record stratum is 0/16 versus 1/16. The latter combines length with changed operator/scope and is
not a length-only effect. Contexts (12), not endpoints (96), are the highest independent units.

## Training actually executed

All 12 frozen windows were collected: 288/288 rows, 249 authenticated available endpoints, 39
NULLs, 140 exact-format responses, and 26 strict successes. Twelve of the 26 successes had zero
gold. The six realized cell totals were:

| cell | available / 48 | strict | zero-gold strict |
|---|---:|---:|---:|
| count-all | 39 | 1 | 0 |
| count-single | 44 | 4 | 4 |
| distinct-single | 42 | 11 | 8 |
| distinct-union | 45 | 7 | 0 |
| weight-all | 32 | 2 | 0 |
| weight-union | 47 | 1 | 0 |

Windows 1 and 2 had no mixed group and correctly no-op'd at Adam 0. Windows 3--12 each admitted at
least one within-task mixed group and advanced exactly once, ending at checkpoint/Adam step 10.
Across those updates, 102 episodes, 445 root turns, and 66,288 root action tokens entered the loss.
Every checkpoint has a nonzero adapter delta; every recorded TIS/PPO guard passes. Child and
observation loss-token counts are zero for every update. Optimizer-only time is 368.706 s; time
including checkpoint writes is 376.421 s. The final checkpoint was the last committed policy, chosen
without validation or held-out outcomes.

These changing-context windows are not a learning curve. Their reward distribution is also far from
balanced: most strict evidence came from `distinct`; zero-gold count/distinct cases were
disproportionately easy. Final same-input pairing, not the rise in unlike-window successes, is the
effect test.

## Executed behavior and counterevidence

Window 1 shows why endpoint reward alone is mechanistically incomplete. None of 24 episodes called
a child or used `batch_contract.py`. Of 22 available outputs, five stated the correct integer inside
contract-invalid prose but remained reward zero. Other traces used literal word matching, queried a
nonexistent category field, stopped early, or produced malformed code. The declared all-24 source
gate correctly produced a no-op; this is not an authentication defect.

Only one training episode used the child path. In window 5 weight-all repeat 2, coordinate
`6e10a2bf609cf704c230a9c6cc6a138955d54064803e89c890463df75c0114a4`, the root issued 16 serial
child calls. The fixed child returned 13/16 correct labels; its four `human being` predictions were
true positives, but it missed one qualifying weight-3 record, implying 23 versus gold 26. The root
computed a local `total_weight`, but its cell displayed no scalar and it finally answered zero.
This is useful child classification followed by imperfect coverage and failed state-to-final
control—not a displayed correct value being ignored. The episode remains strict zero and its child
tokens were not credited.

The final readouts contain 183 authenticated root calls for unchanged and 195 for trained, but zero
child calls in either arm. The four trained successes all rely on brittle public-text/category-string
tests that return zero; none evidences actual semantic label acquisition. They remain valid task
successes where gold is zero, but they do not establish the intended loop.

## Scope-all ambiguity and operational NULLs

The structured `all` query means all records across users `[u0,u1,u2,u3]`. Its frozen prose says
“Among records belonging to all four users.” Multiple authenticated training traces explicitly read
this as an intersection, reasoning that no record belongs to every user. This affects supported
count-all/weight-all and held-out distinct-all, but not single/union cells. No endpoint was rescored
or removed because of it.

At final readout, unchanged `all` is 1/16 with 15 available; trained `all` is 0/16 with only 5
available. Eight trained distinct-all, two count-all, and one weight-all endpoints are NULL. All
eleven reached 16--18 root calls before failing. The twelfth trained NULL is weight-single after
nine calls. By contrast, both unchanged NULLs ended
after four calls. These are correctly recorded as unavailable endpoints, while their repeated calls
remain observed policy-loop/cost evidence.

## Data, native evidence, and cost

The independent input audit recomputed all 84 host answers from sealed labels plus public records.
It found 12 training and 12 readout contexts, 288 training coordinates, 48 readout coordinates per
arm, and no training/readout source-group overlap. Public model-visible records have exactly `id`,
`user`, `text`, and `weight`; host labels are absent. All source groups are nevertheless exposed to
the fixed child's prior training, as declared; this is group-disjoint root evaluation, not pristine
model data.

Every available exported endpoint matches its raw episode hash and root reply; first prompts and
root/child credit roles verify. There are no audit integrity errors. Completed malformed/wrong
responses are zero; setup, timeout, or provider failures are NULL. No generated code was re-executed
and no answer was repaired.

Training collection used 1,620 physical requests over 2,461.270 rollout seconds, including 1,114
authenticated root calls and 16 child calls. Known training tokens were 4,095,367 input, 197,217
output, with 3,809,120 cached and 286,247 uncached input tokens; 32 calls had unknown token fields.
Unchanged readout used 191 physical requests over 401.896 s; trained used 396 over 351.229 s. The
whole owner took 5,129.039 s. These are local physical/token costs, not provider billing.

## Interpretation and next comparison

This run establishes that the frozen RL machinery can collect sparse mixed groups and make ten
authenticated numerical updates. It does not establish transferable query-sensitive reduction.
The final policy's small planned-accuracy increase is entirely constant-zero-compatible, it never
uses the child at readout, and it has a severe all-scope termination regression.

Ranked follow-ups:

1. Run the already motivated disambiguated scope test, replacing “belonging to all four users” with
   explicit “all records, regardless of user,” paired against the old wording. This distinguishes
   language interpretation from learned control without rescoring this run.
2. Before more RL, test an execution-grounded contract where successful reward requires an
   authenticated child call plus a displayed/current-state reduction, with separately reported task
   reward. This attacks zero-answer shortcutting directly; do not leak host labels or repair child
   outputs.
3. If training continues, balance zero/nonzero answer mass and report a fixed constant baseline at
   freeze time. Promote only if paired fresh contexts show nonzero wins, actual child acquisition,
   and no availability loss. Otherwise retire this terminal-only reward formulation.

## Audit timing

The method was frozen at epoch 1788993389.555 during window 2 collection, after the 22:28:18.701 UTC
launch and before this auditor read any reward, admission, optimizer, or held-out outcome. It is a
source-informed live audit closure, not a prospective preregistration. Inherited `RECIPE.json`
declaration fields describe the older numerical recipe, not this outcome-informed campaign.
