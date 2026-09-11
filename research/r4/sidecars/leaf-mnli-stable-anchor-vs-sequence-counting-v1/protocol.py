"""Prospective 16-context stable-anchor versus sequence-counting protocol."""

import copy

import study as s


MASTER = 998317001
SEEDS = tuple(998317101 + index for index in range(16))
LABELS = ("entailment", "neutral", "contradiction")
GENRES = ("government", "slate", "telephone", "travel")
RELATIONS = ("wrong", "alien", "aligned")
ANCHORS = ("labels_only", "sequential_numeric", "permuted_numeric", "opaque")
ARMS = tuple(f"{relation}_{anchor}" for relation in RELATIONS for anchor in ANCHORS)
SYSTEM = (
    "You are a text classification assistant. Classify every supplied input record and return only "
    "the requested final answer in the requested format. Do not write code, use tools, provide "
    "explanations, or reason aloud."
)
SEMANTIC = (
    "For every supplied record, classify the relation of the hypothesis to the premise inside that "
    "same displayed JSON object. entailment means the hypothesis must be true given the premise; "
    "contradiction means it must be false; neutral means neither conclusion follows. requested_tag "
    "is an opaque output address and does not identify or refer to any record.\n"
)


def contexts():
    return s.read(s.ROOT / "DATA.json")["contexts"]


def requested_tags(context):
    ids = [record["id"] for record in context["records"]]
    return ids[17:] + ids[:17]


def context_manifest(context):
    return s.digest([context["index"], [record["id"] for record in context["records"]]])


def anchor_values(context, anchor):
    records = context["records"]
    if anchor == "labels_only":
        return []
    if anchor == "sequential_numeric":
        return list(range(48))
    manifest = context_manifest(context)
    if anchor == "permuted_numeric":
        ordered = sorted(
            range(48),
            key=lambda index: s.digest(
                [MASTER, "permuted_numeric", manifest, records[index]["id"]]
            ),
        )
        assigned = [None] * 48
        for value, index in enumerate(ordered):
            assigned[index] = value
        return assigned
    if anchor == "opaque":
        occupied = {record["id"] for record in records}
        values = []
        for record in records:
            nonce = 0
            while True:
                value = "k" + s.digest(
                    [MASTER, "opaque", manifest, record["id"], nonce]
                )[:12]
                if value not in occupied:
                    break
                nonce += 1
            occupied.add(value)
            values.append(value)
        return values
    raise ValueError(anchor)


def visible_records(context, relation, anchor, alien):
    ids = [record["id"] for record in context["records"]]
    visible = ids if relation == "wrong" else requested_tags(context) if relation == "aligned" else alien
    keys = anchor_values(context, anchor)
    values = []
    for index, (identifier, record, tag) in enumerate(
        zip(visible, context["records"], requested_tags(context), strict=True)
    ):
        value = {
            "id": identifier,
            "premise": record["premise"],
            "hypothesis": record["hypothesis"],
            "requested_tag": tag,
        }
        if anchor != "labels_only":
            value = {"key": keys[index], **value}
        values.append(value)
    return values


def schema(context, anchor):
    if anchor == "labels_only":
        return {
            "json": {
                "type": "array",
                "minItems": 48,
                "maxItems": 48,
                "items": {"type": "string", "enum": list(LABELS)},
            }
        }
    keys = anchor_values(context, anchor)
    items = [
        {
            "type": "object",
            "properties": {
                "key": {"type": "integer" if isinstance(key, int) else "string", "const": key},
                "label": {"type": "string", "enum": list(LABELS)},
            },
            "required": ["key", "label"],
            "additionalProperties": False,
        }
        for key in keys
    ]
    return {
        "json": {
            "type": "array",
            "minItems": 48,
            "maxItems": 48,
            "items": False,
            "prefixItems": items,
        }
    }


def plan():
    rows = []
    dispatch = sorted(range(16), key=lambda index: s.digest([MASTER, "dispatch", index]))
    for rank, context_index in enumerate(dispatch):
        shift = (rank * 5) % len(ARMS)
        for pair_position, arm in enumerate(ARMS[shift:] + ARMS[:shift]):
            relation, anchor = arm.split("_", 1)
            row = {
                "context_index": context_index,
                "repeat": 0,
                "seed": SEEDS[context_index],
                "arm": arm,
                "relation": relation,
                "anchor": anchor,
                "decoder": "exact_anchor_contract",
                "size": 48,
                "block": context_index,
                "pair_position": pair_position,
                "dispatch_order": len(rows),
            }
            row["id"] = s.digest([s.ROOT.name, row])
            rows.append(row)
    return rows


def request(context, row, alien=None):
    relation, anchor = row["relation"], row["anchor"]
    if alien is None:
        alien = s.read(s.ROOT / "ALIEN_DICTIONARIES.json")[str(context["index"])]
    if anchor == "labels_only":
        instruction = (
            "Return exactly 48 strings in one JSON array, in displayed record order. Each string "
            "must be exactly entailment, neutral, or contradiction. Return labels only; ordinary "
            "code will attach each record's requested_tag afterward. No additional text.\n"
        )
    else:
        instruction = (
            "Return exactly 48 JSON objects in one array, in displayed record order. Each object "
            "must have exactly the field key followed by the field label. At every output position, "
            "copy that displayed record's key exactly into key. For label, use exactly entailment, "
            "neutral, or contradiction. No additional text.\n"
        )
    prompt = SEMANTIC + instruction + "Input records:\n" + s.serialize(
        visible_records(context, relation, anchor, alien)
    )
    return {
        "model": s.MODEL["alias"],
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.5,
        "top_p": 1,
        "top_k": -1,
        "min_p": 0,
        "repetition_penalty": 1,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "seed": row["seed"],
        "max_tokens": 3072,
        "return_token_ids": True,
        "chat_template_kwargs": {"enable_thinking": False},
        "cache_salt": s.ROOT.name,
        "structured_outputs": schema(context, anchor),
    }


def null_row(row, reason):
    return {
        "coordinate": copy.deepcopy(row),
        "available": False,
        "strict_correct": None,
        "strict_bounds": [0, 48],
        "reason": reason,
    }
