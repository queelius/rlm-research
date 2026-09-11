"""Optional local receipts; original nano broker and raw result are unchanged."""
import hashlib
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _audit(value):
    # Diagnostic, root-writable evidence: corroborate against native calls/traces.
    with (ROOT / "receipt_audit.jsonl").open("a") as stream:
        stream.write(json.dumps(value, sort_keys=True, allow_nan=False) + "\n")


def source_records():
    return json.loads((ROOT / "receipt_catalog.json").read_text())["records"]


def parse_receipt(raw, expected_ids, allowed_values):
    duplicate_keys = []
    class Object(dict):
        pass
    def pairs(items):
        result = Object()
        result.pairs = items
        for key, value in items:
            if key in result:
                duplicate_keys.append(key)
            result[key] = value
        return result
    def non_json(value):
        raise ValueError("non-JSON constant: " + value)
    parsed, error = None, None
    try:
        parsed = json.loads(raw, object_pairs_hook=pairs, parse_constant=non_json)
    except (ValueError, TypeError) as caught:
        error = {"type": type(caught).__name__, "message": str(caught)}
    seen, duplicates, unknown, invalid, mapping = [], [], [], [], {}
    rows = [{"id":key,"label":value} for key,value in parsed.pairs] if isinstance(parsed,Object) else []
    if error is None and not isinstance(parsed,Object):
        invalid.append({"position": None, "reason": "top_level_not_id_label_object"})
    for position, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"id", "label"}:
            invalid.append({"position": position, "reason": "record_schema"})
            continue
        key, label = row["id"], row["label"]
        if not isinstance(key, str):
            invalid.append({"position": position, "reason": "id_type"})
            continue
        if key in seen:
            duplicates.append(key)
        seen.append(key)
        if key not in expected_ids:
            unknown.append(key)
        if not isinstance(label, str) or label not in allowed_values:
            invalid.append({"position": position, "reason": "invalid_label"})
        else:
            mapping[key] = label
    missing = [key for key in expected_ids if key not in seen]
    valid = not any((error, duplicate_keys, duplicates, unknown, invalid, missing))
    return {"raw_answer": raw, "parsed_records": rows, "returned_order": seen, "parse_error": error,
        "duplicate_keys": duplicate_keys, "duplicate_ids": duplicates, "unknown_ids": unknown,
        "missing_ids": missing, "invalid_records": invalid, "valid": valid,
        "labels_by_id": mapping if valid else None,
        "requested_ids": list(expected_ids), "allowed_values": list(allowed_values),
        "requested_id_coverage": len(set(seen) & set(expected_ids)) / len(expected_ids) if expected_ids else None,
        "semantic_correctness_validated": False}


class RawView:
    def __init__(self, result):
        self.native_result = result
        self.answer = result.answer
        self.session_dir, self.usage, self.turns = result.session_dir, result.usage, result.turns


class ReceiptView(RawView):
    def __init__(self, result, value, call_id):
        super().__init__(result)
        self._value, self._call_id = value, call_id

    def receipt(self):
        _audit({"event": "receipt_access", "call_id": self._call_id})
        # Do not expose mutable internal state across repeated access.
        return json.loads(json.dumps(self._value, allow_nan=False))


def build_request(catalog, selected_ids, query, allowed_values):
    if (not isinstance(selected_ids, (list, tuple)) or not selected_ids
            or any(not isinstance(key, str) for key in selected_ids)
            or len(set(selected_ids)) != len(selected_ids)):
        raise ValueError("selected_ids must be a nonempty unique sequence of public IDs")
    if (not isinstance(query, str) or not query.strip()
            or not isinstance(allowed_values, (list, tuple)) or not allowed_values
            or any(not isinstance(value, str) or not value for value in allowed_values)
            or len(set(allowed_values)) != len(allowed_values)):
        raise ValueError("query and a nonempty unique string vocabulary are required")
    lookup = {row["id"]: row for row in catalog["records"]}
    if not set(selected_ids) <= lookup.keys():
        raise ValueError("selected ID is absent from the public source catalog")
    selected = [lookup[key] for key in selected_ids]
    prompt = ("Answer the query for each supplied source record. Return only a JSON object "
        "mapping each supplied source id to its label string. Copy each supplied id exactly once as a key; "
        "no missing or extra ids. Each value must be one of the allowed values.\nQuery: " + query
        + "\nAllowed values: " + json.dumps(list(allowed_values), ensure_ascii=False)
        + "\nRecords: " + json.dumps([{"id": r["id"], "text": r["text"]} for r in selected],
            ensure_ascii=False, separators=(",", ":")))
    return prompt, {"context_sha256": catalog["context_sha256"], "selected_records": selected,
                    "request_text": prompt, "request_sha256": _sha(prompt)}


async def rlm_records(selected_ids, query, allowed_values):
    from rlm.api import run
    catalog = json.loads((ROOT / "receipt_catalog.json").read_text())
    arm = json.loads((ROOT / "receipt_config.json").read_text())["arm"]
    if arm not in ("indexed_raw", "receipt"):
        raise ValueError("unknown helper arm")
    prompt, provenance = build_request(catalog, selected_ids, query, allowed_values)
    call_id = uuid.uuid4().hex
    _audit({"event": "helper_request", "call_id": call_id, "query": query,
        "allowed_values": list(allowed_values), **provenance})
    try:
        result = await run(prompt)
    except BaseException as caught:
        _audit({"event": "helper_error", "call_id": call_id,
            "type": type(caught).__name__, "message": str(caught)})
        raise
    value = {**parse_receipt(result.answer, selected_ids, allowed_values), **provenance}
    _audit({"event": "helper_result", "call_id": call_id, "receipt": value,
        "session_dir": str(result.session_dir) if result.session_dir is not None else None,
        "usage": {"prompt_tokens": result.usage.prompt_tokens, "completion_tokens": result.usage.completion_tokens},
        "turns": result.turns})
    return ReceiptView(result, value, call_id) if arm == "receipt" else RawView(result)
