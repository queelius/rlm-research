"""IDs-only public contract and deterministic metadata lookup; no eligibility repair."""
import sys
import study

MARKER = "Return the complete eligible relation as exactly one JSON object"
SUFFIX = (
    "Return exactly one JSON object with exactly one key, eligible_ids. Its value must be "
    "a lexicographically sorted array of unique implementation ID strings from this local shard. "
    "Report every eligible implementation exactly once, including eligible implementations "
    "that are not your preferred choice; do not include ineligible implementations. "
    "If none are eligible, return an empty array. Return no additional keys or explanation.\n"
)


def render(original_prompt):
    assert original_prompt.count(MARKER) == 1
    return original_prompt.split(MARKER, 1)[0] + SUFFIX


def reference():
    study.source.b05()
    return sys.modules["b05_native_runner_etl_catalog.solver_reference"]


def grade(text, child):
    study.source.b05()
    parser = sys.modules["b05_native_runner_etl_catalog.grading"]._parse_json_object
    try:
        parsed = parser(text)
        assert set(parsed) == {"eligible_ids"}, "expected only eligible_ids"
        ids = parsed["eligible_ids"]
        assert isinstance(ids, list) and all(isinstance(item, str) for item in ids), "expected string array"
        assert ids == sorted(ids) and len(ids) == len(set(ids)), "IDs must be sorted and unique"
        known = {row["implementation_id"] for row in child["stage"]["tables"]["implementations"]}
        assert set(ids) <= known, "ID outside local shard"
        return {"status": "valid_claim", "parsed": parsed, "reason": None}
    except Exception as error:
        return {"status": "invalid_claim", "parsed": None, "reason": f"{type(error).__name__}: {error}"}


grade_child_response = grade


def lookup(ids, child):
    # Deliberately use every original implementation's effective fields; never read
    # eligibility/rejection fields and never add/remove an ID based on them.
    by_id = {row["implementation_id"]: row["effective_row"]
             for row in reference().child_reference_receipt(child)["derivations"]}
    assert len(ids) == len(set(ids)) and set(ids) <= set(by_id)
    rows = [by_id[identifier] for identifier in sorted(ids)]
    assert {row["implementation_id"] for row in rows} == set(ids)
    return {"row_count": len(rows), "rows": rows}
