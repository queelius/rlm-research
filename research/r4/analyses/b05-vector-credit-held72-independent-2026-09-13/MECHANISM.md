---
status: COMPLETE_RAW_AUDIT
planned_calls: 72
available_calls: 72
paired_units: 24
matched_semantic_valid_units: 22
---

# Local versus joint credit: held-panel mechanism

All 72 native calls returned and passed exact saved-request, prompt, model-alias, decoded-token,
provider-ID, physical-inventory, and canonical-response checks. Base, local, and joint use the same 24
context/seed coordinates. The two trained adapters have the same authenticated zero-B initialization.

On all 24 planned units, exact vector accuracy is base 6, candidate-local 8, and response-joint 7.
Local has 3 paired wins and 1 loss against base; joint has 2 wins and 1 loss. The wins span three
distinct contexts for local and two for joint; this is not a single duplicated-context result.

The same two coordinates are semantically invalid in all three arms: each returned a normal-stop JSON
vector with 19 booleans for a 20-candidate task. They are failures in the primary exact /24 denominator;
only the per-candidate confusion diagnostic omits them because no complete 20-decision vector exists.
They are never repaired. Across the common 22 valid units, false positives are 8 for every arm;
false negatives are 15 for base, 10 for local, and 12 for joint.

At the individual decision level, local changes six of 22 valid vectors: seven candidate decisions move
toward gold and two move away. Joint changes four vectors: five decisions move toward gold and two move
away. Sixteen local vectors and eighteen joint vectors are byte-equivalent in their boolean decisions to
base. These small, seed-specific movements support a fresh-seed repeat, not retrospective selection of
local as a winner or a claim that candidate-local credit caused a general capability gain.

The panel is balanced across widths 6/12/20 and check-revision counts 1/3: two contexts in each of the
six cells. No eligibility fallback, ID repair, or partial credit on invalid vectors was used.
