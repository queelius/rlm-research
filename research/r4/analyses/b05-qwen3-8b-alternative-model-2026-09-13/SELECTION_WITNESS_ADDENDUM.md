# B05 Qwen3-8B selection/witness addendum

The official result remains 0/4 direct and 0/4 oracle. All eight responses were well-formed JSON with three stage IDs, but six failed immediately because `covered_features` was not sorted; two used inconsistent numeric witness fields.

Without changing any selected ID, a host-side public-row lookup and deterministic witness recomputation grades the eight selected triples as {'valid_but_wrong': 6, 'invalid_claim': 2}. This is an inert interface diagnostic, not repaired accuracy: it supplies arithmetic the model was required to produce and therefore cannot replace the official grader.
