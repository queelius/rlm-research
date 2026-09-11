---
status: complete_manual_semantic_review
study: root-question-sensitive-seed-replication-v1
policy: sft6
segment: 000-071
planned: 72
covered: 72
observed: 70
null: 2
strict: 51
faithful_observed: 60
faithful_and_strict: 49
---

# Fresh-seed SFT6 semantic review, endpoints 0–71

I manually read every endpoint's actual sampled programs, parent-linked tool
observations, and authenticated final. I did not execute generated code and did
not use a keyword classifier. The trusted `qs_problem.answer` oracle was used
only after manual fidelity judgment to check whether faithful wrong finals were
the exact answer implied by their observed child-label maps.

Coverage is 72/72 planned endpoints. Seventy are observed and two are NULL under
the existing audit availability rule (indices 35 and 68). There are 51 strict
answers. Sixty of the 70 observed paths faithfully implement the requested
operator, scope, and threshold; 49 are both faithful and strict.

Index 22 has an authenticated empty final and is therefore an observed zero,
not NULL. Its complete child map is followed by repeated `set` constructions
over record dictionaries, all failing as unhashable, so it is neither faithful
nor strict.

## Classification inventory

- Faithful and strict: 49 endpoints—48 direct paths plus repaired index 59.
- Faithful but wrong from observed child labels: indices 1, 10, 11, 19, 21,
  30, 34, 41, 46, 61, and 71.
- Unfaithful but strictly correct by coincidence: indices 17 and 27.
- Unfaithful and wrong: indices 3, 9, 15, 16, 22, 33, 40, and 60.
- Audit NULL: indices 35 and 68.

All normal acquisitions retained a complete 16-record child-label map. Index 35
attempted acquisition but retained only a partial boolean matches structure and
has no authenticated final. Index 68 retained a complete map and sampled a
faithful reduction, but no authenticated reduction observation/final exists, so
it remains NULL rather than an observed zero.

## Faithful wrong diagnoses

For every faithful wrong path, the trusted oracle applied to the actual observed
map exactly reproduces the final:

| Index | Observed-map answer | Host gold | Misclassified record IDs |
| ---: | ---: | ---: | --- |
| 1 | 2 | 1 | `q40c3eb935019`, `q9d492e69e530` |
| 10 | 3 | 4 | `q40c3eb935019` |
| 11 | 0 | 1 | `q1a7a3ab897cf`, `q25bdece53276` |
| 19 | 2 | 1 | `q11d7ee167298`, `qf917c7a3e46c` |
| 21 | 2 | 4 | `q98602aad4b0c`, `qf07e63c4d669` |
| 30 | 2 | 4 | `q98602aad4b0c`, `qf07e63c4d669` |
| 34 | 0 | 1 | `q1a7a3ab897cf`, `q25bdece53276`, `qe9a57c0d6533` |
| 41 | 19 | 15 | `q459506b7cad8` |
| 46 | 17 | 15 | `q1a7a3ab897cf` |
| 61 | 0 | 1 | `q459506b7cad8`, `qe0d658082aad` |
| 71 | 1 | 2 | `q459506b7cad8` |

This separates child-label errors from reduction errors; it does not make the
individual labels independent observations.

## Unfaithful path details

- Index 3 counts post-threshold records rather than users whose final category
  total is strictly greater than four.
- Index 9 mixes user-summary dictionaries with record-label entries, compares a
  user dictionary to a numeric category code, and sums rather than taking a
  per-user maximum.
- Index 15 repeatedly treats a record-ID label map as a nested user/category
  map; the enormous digit-string final is unsupported by any scalar observation.
- Index 16 repeatedly indexes a one-category dictionary with every observed
  category and fails with `KeyError`; final zero is unsupported.
- Index 17 filters individual records by weight greater than eight before
  aggregation. Its strict zero is coincidental.
- Index 22 repeatedly constructs sets of record dictionaries, fails, and ends
  with the authenticated empty observed-zero final.
- Index 27 computes a sum across scoped users instead of the requested maximum;
  no matching labels make its strict zero coincidental.
- Index 33 swaps user and category variables and repeatedly fails with
  `KeyError`; final zero is unsupported.
- Index 40 repeatedly constructs a set of record dictionaries and fails; no
  scalar observation supports final 93.
- Index 60 selects `numeric value` although the question targets
  `abbreviation`.

Index 34 is faithful because its final executed repair—not its first two failed
drafts—correctly computes per-user totals and strict `>8`. Index 53 similarly
repairs an initial malformed comprehension before observing 11. At index 59,
four dictionary-set attempts fail; the final branch correctly retains qualifying
user IDs, and the actual human-being selection is empty, so its observed/final
zero is faithful for the realized state.

## Source identity

- `METHOD.md`: `208ed6a52606bdad8fd55f2c43b776d944eef0ea80d7b06aed8c7c67070926b7`
- `readout_audit.py`: `812f2b468d5bdbfccb55cd0ffb40e53314cba2711aaa2443be09036676a8de1e`
- `root-question-sensitive-seed-replication-v1-AUDIT.json`:
  `c680125c138079d485eb16a063b86757398c3a5ecf553821c9064e0e6d839374`
- `qs_problem.py`: `054029d750c464a0ae8a928ca08d5906a39f4f9334a04d105f65d5bb05a11a4c`

The JSON companion contains one explicit record for every index, including
acquisition, retained-map, fidelity, observed-state use, strictness,
faithful-plus-strict, classification, and a path-specific note.
