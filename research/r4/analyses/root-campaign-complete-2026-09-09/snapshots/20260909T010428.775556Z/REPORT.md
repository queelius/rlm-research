# Root campaign completion snapshot

State: stopped_or_interrupted; committed updates: 3.

Validation learning curve (strict successes / fixed8): step 0: 2/8, step 2: 3/8.

Selected policy: pending; do not substitute last checkpoint.
Final step8 policy: not yet terminally reported in FINAL.

| Stage | Successes / planned | Admitted | Root / child calls | Root / child action tokens | Invalid terminals |
|---|---:|---:|---:|---:|---:|
| validation-00 | 2/8 | 8 | 14/43 | 3627/3140 | 2 |
| round-01/collection | 12/32 | 32 | 70/372 | 25261/51582 | 13 |
| round-02/collection | 13/32 | 32 | 64/176 | 19867/18922 | 10 |
| validation-02 | 3/8 | 8 | 16/86 | 4005/3909 | 1 |
| round-03/collection | 12/32 | 32 | 68/251 | 20460/28221 | 6 |
| round-04/collection | 12/32 | 29 | 78/317 | 26032/37419 | 6 |

Transfer paired summary: {"excluded_or_unpaired": 0, "newly_correct": 0, "newly_wrong": 0, "retained_correct": 0, "retained_wrong": 0, "same_inputs_are_not_deterministic_replay": true}.

Fresh training seeds are unpaired; fixed seeds are not deterministic replay. Validation selects earliest maximum; selected root differs conceptually from final step8. Transfer is root-held-out/child-SFT-train-supported. Recursion is not coverage.

Pending/censored: validation-04, round-05/collection, round-06/collection, validation-06, round-07/collection, round-08/collection, validation-08, transfer-original, transfer-selected.

Native candidates are not authoritative until export admission. Recovered provider errors remain distinct from excluded episodes. All cached completed stages/updates were authenticated once; original first-two audit is reused by exact hash. No GPU/network calls or experiment mutations.
