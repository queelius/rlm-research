"""AG serialization/strict merge; aggregation is host scoring only."""

import json

LABELS = ["World", "Sports", "Business", "Sci/Tech"]
DEFINITIONS = (
    "Classify the primary topic of each news item using these AG News definitions:\n"
    "World: international affairs, governments, conflict, diplomacy, or global events.\n"
    "Sports: athletic competition, teams, players, games, or tournaments.\n"
    "Business: companies, markets, finance, trade, or the economy.\n"
    "Sci/Tech: science, technology, computing, engineering, space, or research.\n"
    "Choose the primary article topic rather than a merely mentioned subject."
)


def request_for(records):
    public = [{"id": row["id"], "text": row["text"]} for row in records]
    if not public or len({row["id"] for row in public}) != len(public):
        raise ValueError("nonempty unique public record IDs required")
    return (DEFINITIONS + "\nReturn only one JSON object mapping every supplied id exactly once to one label.\n"
            + "No missing or extra ids. Allowed labels: " + json.dumps(LABELS, separators=(",", ":"))
            + "\nItems: " + json.dumps(public, separators=(",", ":"), ensure_ascii=False))


def match_request(prompt, records):
    return isinstance(prompt, str) and len(records) == 16 and prompt == request_for(records)


def schema(ids):
    return {"type": "object", "properties": {key: {"type": "string", "enum": LABELS[:]} for key in ids},
            "required": list(ids), "additionalProperties": False}


def strict_map(raw, ids):
    def pairs(rows):
        result = dict(rows)
        if len(result) != len(rows):
            raise ValueError("duplicate response keys")
        return result
    result = json.loads(raw, object_pairs_hook=pairs)
    if not isinstance(result, dict) or list(result) != list(ids) or len(set(ids)) != len(ids):
        raise ValueError("exact ordered response keys required")
    if any(not isinstance(label, str) or label not in LABELS for label in result.values()):
        raise ValueError("canonical AG category required")
    return result


def merge_maps(maps, ids):
    if len(ids) != 16 or len(maps) != 4:
        raise ValueError("exactly four B4 maps required")
    result = {}
    for index, value in enumerate(maps):
        result.update(strict_map(json.dumps(value), ids[index * 4:index * 4 + 4]))
    return result


def question(spec):
    verb = "Count records" if spec["operator"] == "count" else "Sum the weights of records"
    return (f"Across all 16 records, {verb.lower()} whose category is {spec['target']!r}. "
            "Return only Answer: N, replacing N with the exact nonnegative integer.")


def aggregate(records, labels, spec):
    selected = [row for row in records if labels[row["id"]] == spec["target"]]
    if spec["operator"] == "count":
        return len(selected)
    if spec["operator"] == "weight_sum":
        return sum(row["weight"] for row in selected)
    raise ValueError("unknown frozen aggregation operator")


def public_module_bytes():
    # Do not stage this host module: aggregate/question are deliberately excluded.
    import inspect
    return ("import json\nLABELS=" + repr(LABELS) + "\nDEFINITIONS=" + repr(DEFINITIONS) + "\n\n"
            + inspect.getsource(request_for) + "\n" + inspect.getsource(strict_map)).encode()
