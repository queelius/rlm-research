"""Complete 3x2x2 positional-anchor protocol on 16 fresh contexts."""

import copy

import study as s


MASTER = 997217001
SEEDS = tuple(997217101 + index for index in range(16))
LABELS = ("entailment", "neutral", "contradiction")
GENRES = ("government", "slate", "telephone", "travel")
RELATIONS = ("wrong", "alien", "aligned")
INPUT_ROWS = ("absent", "present")
OUTPUTS = ("labels_only", "row_first")
ARMS = tuple(f"{relation}_{input_row}_{output}" for relation in RELATIONS for input_row in INPUT_ROWS for output in OUTPUTS)
SYSTEM = "You are a text classification assistant. Classify every supplied input record and return only the requested final answer in the requested format. Do not write code, use tools, provide explanations, or reason aloud."
SEMANTIC = "For every supplied record, classify the relation of the hypothesis to the premise inside that same displayed JSON object. entailment means the hypothesis must be true given the premise; contradiction means it must be false; neutral means neither conclusion follows. requested_tag is an opaque output address and does not identify or refer to any record.\n"
LABEL_ONLY = "Return exactly 48 strings in one JSON array, in displayed record order. Each string must be exactly entailment, neutral, or contradiction. Return labels only; ordinary code will attach each record's requested_tag afterward. No additional text.\n"
ROW_FIRST_PRESENT = "Return exactly 48 JSON objects in one array, in displayed record order. Each object must have exactly the integer field row followed by the string field label. At output position i, copy that displayed record's row integer exactly into row. For label, use exactly entailment, neutral, or contradiction. No additional text.\n"
ROW_FIRST_ABSENT = "Return exactly 48 JSON objects in one array, in displayed record order. Each object must have exactly the integer field row followed by the string field label. At output position i, write the zero-based displayed position i into row. For label, use exactly entailment, neutral, or contradiction. No additional text.\n"


def contexts():
    return s.read(s.ROOT / "DATA.json")["contexts"]


def requested_tags(context):
    ids = [record["id"] for record in context["records"]]
    return ids[17:] + ids[:17]


def parts(arm):
    relation, input_row, output = arm.split("_", 2)
    if relation not in RELATIONS or input_row not in INPUT_ROWS or output not in OUTPUTS:
        raise ValueError(arm)
    return relation, input_row, output


def visible_records(context, relation, input_row):
    ids = [record["id"] for record in context["records"]]
    visible = ids if relation == "wrong" else requested_tags(context) if relation == "aligned" else s.read(s.ROOT / "ALIEN_DICTIONARIES.json")[str(context["index"])]
    values = [dict(id=identifier, premise=record["premise"], hypothesis=record["hypothesis"], requested_tag=tag) for identifier, record, tag in zip(visible, context["records"], requested_tags(context), strict=True)]
    return [dict(row=index, **value) for index, value in enumerate(values)] if input_row == "present" else values


def schema(arm):
    _, _, output = parts(arm)
    if output == "labels_only":
        return {"json": {"type": "array", "minItems": 48, "maxItems": 48, "items": {"type": "string", "enum": list(LABELS)}}}
    items = [{"type": "object", "properties": {"row": {"type": "integer", "const": index}, "label": {"type": "string", "enum": list(LABELS)}}, "required": ["row", "label"], "additionalProperties": False} for index in range(48)]
    return {"json": {"type": "array", "minItems": 48, "maxItems": 48, "items": False, "prefixItems": items}}


def plan():
    rows = []
    dispatch = sorted(range(16), key=lambda index: s.digest([MASTER, "dispatch", index]))
    for rank, context_index in enumerate(dispatch):
        shift = (rank * 5) % len(ARMS)
        for position, arm in enumerate(ARMS[shift:] + ARMS[:shift]):
            relation, input_row, output = parts(arm)
            row = {"context_index": context_index, "repeat": 0, "seed": SEEDS[context_index], "arm": arm, "relation": relation, "input_row": input_row, "output": output, "decoder": "exact_positional_contract", "size": 48, "block": context_index, "pair_position": position, "dispatch_order": len(rows)}
            row["id"] = s.digest([s.ROOT.name, row])
            rows.append(row)
    return rows


def request(context, row):
    relation, input_row, output = parts(row["arm"])
    instruction = LABEL_ONLY if output == "labels_only" else ROW_FIRST_PRESENT if input_row == "present" else ROW_FIRST_ABSENT
    fields = "row, id, premise, hypothesis, requested_tag" if input_row == "present" else "id, premise, hypothesis, requested_tag"
    prompt = SEMANTIC + instruction + f"Input records ({fields}):\n" + s.serialize(visible_records(context, relation, input_row))
    return {"model": s.MODEL["alias"], "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], "temperature": 0.5, "top_p": 1, "top_k": -1, "min_p": 0, "repetition_penalty": 1, "presence_penalty": 0, "frequency_penalty": 0, "seed": row["seed"], "max_tokens": 3072, "return_token_ids": True, "chat_template_kwargs": {"enable_thinking": False}, "cache_salt": s.ROOT.name, "structured_outputs": schema(row["arm"])}


def null_row(row, reason):
    return {"coordinate": row, "available": False, "strict_correct": None, "strict_bounds": [0, 48], "reason": reason}
