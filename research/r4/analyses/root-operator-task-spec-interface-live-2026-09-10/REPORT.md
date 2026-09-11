# Independent audit: task-specification interface 72

## Bottom line

Adding a prose task file (`P`) or a structured JSON task file (`J`) did not produce evidence that this SFT24 policy used the supplied operator specification. The preregistered strict scores were `U=2/24`, `P=4/24`, and `J=4/24`, but availability was only 16, 17, and 15 endpoints respectively. More importantly, no executed final-branch program in any retained episode referenced `task.txt` or `task.json`, and manual review found that none of the ten strict scalar successes implemented the requested operator and scope.

This is an exploratory, exposed eight-context panel. It shows that this particular file-plus-prompt package did not instantiate metadata use in the observed trajectories. It does **not** show that correct task metadata would be useless if a policy actually retrieved and used it.

## Timing and independence

The method receipt was frozen at `2026-09-10T08:17:51.571894+00:00`, 43.617605 seconds before the actual command at epoch `1789028315.1894991`. Collection ended at epoch `1789029376.0056067` (outer elapsed 1060.810001 seconds, exit 0, GPU released). MAIN printed the large owner terminal and saw a few endpoint rows at 08:47:36 UTC; the audit method was already frozen and was not changed afterward. I had authored the later warm-RL preparation, not this interface72 implementation.

## Planned-denominator results

| Interface | Correct / planned | Available | Observed wrong | NULL | Bounds if all NULLs are wrong/right |
|---|---:|---:|---:|---:|---:|
| U: unchanged | 2/24 | 16/24 | 14 | 8 | 2–10/24 |
| P: prose file | 4/24 | 17/24 | 13 | 7 | 4–11/24 |
| J: JSON file | 4/24 | 15/24 | 11 | 9 | 4–13/24 |

On jointly available paired blocks, `J−P` had 2 wins, 1 loss, and 7 ties (`n=10`); `P−U` had 1 win, 1 loss, and 9 ties (`n=11`); `J−U` had 1 win, 1 loss, and 7 ties (`n=9`). The pairwise samples are small and availability-dependent. The wide planned-denominator bounds overlap completely.

By requested operator, observed strict successes were:

- U: maximum 0/8, threshold 0/8, conditional 2/8.
- P: maximum 1/8, threshold 1/8, conditional 2/8.
- J: maximum 2/8, threshold 0/8, conditional 2/8.

The eight dependent context clusters were heterogeneous. Correct/available/planned by `U,P,J` were: new-00 `0/3/3, 0/1/3, 0/2/3`; new-01 `1/3/3, 0/1/3, 1/2/3`; new-02 `0/3/3, 0/2/3, 0/1/3`; new-03 `0/1/3, 1/3/3, 1/2/3`; new-04 `0/2/3, 0/3/3, 0/1/3`; new-05 `0/2/3, 0/2/3, 0/2/3`; new-06 `0/1/3, 2/3/3, 2/2/3`; and new-07 `1/1/3, 1/2/3, 0/3/3`. These are descriptive clusters, not 24 independent contexts.

## Was the interface used?

No observed trace used it. I inspected every executed IPython program on the authenticated final branch of all 65 retained episode graphs, including wrong and unavailable-final episodes. Among the 32 available `P`/`J` endpoints:

- `task.txt` references or reads: 0;
- `task.json` references or reads: 0;
- parsed metadata objects: 0;
- metadata fields entering executed selection or reduction logic: 0.

The policy continued to read `records.json`/`context.txt` and infer or imitate an operation from the natural-language question. Therefore `J` versus `P` is a randomized package contrast in principle, but the intended metadata-use mediator was absent in practice.

## What produced the ten strict successes?

All ten were score successes and remain scored as such. None was a faithful execution of the requested operator and scope:

- Six nonzero matches used a simplified wrong computation: both pair-10 maximum tasks summed all predicted numeric weights; both pair-23 conditional tasks summed all predicted human-being weights without testing whether their users had numeric records; and both pair-5 conditional tasks summed location weights over hard-coded user subsets without deriving entity-bearing users.
- Four zero matches were coincidences: one used nonexistent `user_1`-style identities, one ended after malformed map calls and a fabricated text search, one summed location weights instead of counting over-threshold users, and one selected an empty location list without computing a per-user maximum.

Thus the observed faithful requested-operation count is 0/10 strict successes (0/6 nonzero successes and 0/4 zero successes). This semantic diagnostic does not alter the preregistered terminal-reward score and does not reexecute sampled code or repair answers.

## Native, NULL, and cost audit

All 65 retained episode graphs passed the corrected native identity join: the final root branch tokens equal native prompt plus completion IDs; prompt IDs equal the exact wire body; the unique wire choice IDs equal completion IDs; and one physical body/response record matches the final role record. All 48 admitted native finals additionally decode exactly to the recorded reply. Source scores and independently reconstructed scores had no disagreements.

Of 24 NULL slots, seven were retained timeout failures with no episode result. The other 17 had episode results but no authentic usable final: ten length-finished and six stop-finished responses had null content, and one ended with an outstanding tool call. These are NULL, not zeros.

The disk union contains 1,019 physical local-model attempts: 753 root and 266 child. There were 1,012 choice-bearing completions and seven failed/unconfirmed attempts. Known usage was 3,059,757 input, 95,782 output, and 2,903,552 cached tokens, with seven unknowns for each field. This is physical usage, not provider billing. Realized arm call counts differed substantially (`U=322`, `P=231`, `J=466`) because sampled loops differed; they are not fixed interface costs.

## Interpretation and next comparison

The scalar counts alone weakly favor both added-file arms by two planned successes, but pairing, NULL bounds, context dependence, and the complete absence of metadata retrieval make that difference mechanistically unpersuasive. JSON was also more expensive in realized calls without evidence of using JSON.

The next discriminating experiment should test **reachability before downstream task accuracy**: place the exact operator object in a directly rendered, unavoidable message field or require a cheap first action that returns the parsed object, and verify retrieval/parse fidelity on a small balanced panel before paying for full child acquisition. If retrieval is reliable, then compare faithful operator execution with and without the object on new context clusters. Repeating this same optional-file package or starting another terminal-reward run would not address the observed bottleneck.

## Artifacts

- `AUDIT.json`: all 72 slots, native joins, planned scores, pairs, clusters, and physical pins.
- `MECHANISMS.json`: immutable per-success semantic judgments and program hashes.
- `COST_AUDIT.json`: disk-union physical accounting by arm and model role.
- `TRACE_EXTRACT.json`: final-branch programs and observations.
- `OUTCOME_PINS.json`: hashes of the complete output tree at audit time.
- `CPU_TESTS.xml`: four focused checks, all passed.

