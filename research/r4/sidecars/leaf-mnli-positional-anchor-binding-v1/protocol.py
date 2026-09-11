"""Three references by input row marker by output positional anchor."""

import copy

import study as s


MASTER = 996217001
SEEDS = tuple(996217101 + index for index in range(8))
LABELS = ("entailment", "neutral", "contradiction")
RELATIONS = ("wrong", "alien", "aligned")
INPUT_ROWS = ("absent", "present")
OUTPUTS = ("labels_only", "row_first")
ARMS = tuple(f"{relation}_{input_row}_{output}" for relation in RELATIONS for input_row in INPUT_ROWS for output in OUTPUTS)
SYSTEM = "You are a text classification assistant. Classify every supplied input record and return only the requested final answer in the requested format. Do not write code, use tools, provide explanations, or reason aloud."
SEMANTIC = "For every supplied record, classify the relation of the hypothesis to the premise inside that same displayed JSON object. entailment means the hypothesis must be true given the premise; contradiction means it must be false; neutral means neither conclusion follows. requested_tag is an opaque output address and does not identify or refer to any record.\n"
LABEL_ONLY = "Return exactly 48 strings in one JSON array, in displayed record order. Each string must be exactly entailment, neutral, or contradiction. Return labels only; ordinary code will attach each record's requested_tag afterward. No additional text.\n"
ROW_FIRST_PRESENT = "Return exactly 48 JSON objects in one array, in displayed record order. Each object must have exactly the integer field row followed by the string field label. At output position i, copy that displayed record's row integer exactly into row. For label, use exactly entailment, neutral, or contradiction. No additional text.\n"
ROW_FIRST_ABSENT = "Return exactly 48 JSON objects in one array, in displayed record order. Each object must have exactly the integer field row followed by the string field label. At output position i, write the zero-based displayed position i into row. For label, use exactly entailment, neutral, or contradiction. No additional text.\n"

prior = s.load(
    "position_anchor_prior_protocol",
    s.PRIOR / "protocol_v2.py",
    "7c5dbd83d5e83fba0a3d2ae5da991878ae9bdbc1a2b2c5391c3d3be4b16ea77a",
    {"study": s.qualified},
)


def contexts():
    return prior.contexts()


def requested_tags(context):
    return prior.requested_tags(context)


def visible_records(context, relation, input_row):
    values = prior.visible_records(context, f"{relation}_labels_only")
    if not input_row:
        return values
    return [dict(row=index, **value) for index, value in enumerate(values)]


def parts(arm):
    relation, input_row, output = arm.split("_", 2)
    if relation not in RELATIONS or input_row not in INPUT_ROWS or output not in OUTPUTS:
        raise ValueError(arm)
    return relation, input_row, output


def schema(arm):
    _, _, output = parts(arm)
    if output == "labels_only":
        return {"json": {"type": "array", "minItems": 48, "maxItems": 48, "items": {"type": "string", "enum": list(LABELS)}}}
    items = []
    for index in range(48):
        items.append({"type": "object", "properties": {"row": {"type": "integer", "const": index}, "label": {"type": "string", "enum": list(LABELS)}}, "required": ["row", "label"], "additionalProperties": False})
    return {"json": {"type": "array", "minItems": 48, "maxItems": 48, "items": False, "prefixItems": items}}


def plan():
    rows = []
    dispatch = sorted(range(8), key=lambda index: s.digest([MASTER, "dispatch", index]))
    for rank, context_index in enumerate(dispatch):
        shift = (rank * 5) % len(ARMS)
        arms = ARMS[shift:] + ARMS[:shift]
        for position, arm in enumerate(arms):
            relation, input_row, output = parts(arm)
            row = {"context_index": context_index, "repeat": 0, "seed": SEEDS[context_index], "arm": arm, "relation": relation, "input_row": input_row, "output": output, "decoder": "exact_positional_contract", "size": 48, "block": context_index, "pair_position": position, "dispatch_order": len(rows)}
            row["id"] = s.digest([s.ROOT.name, row])
            rows.append(row)
    return rows


def request(context, row):
    relation, input_row, output = parts(row["arm"])
    instruction = LABEL_ONLY if output == "labels_only" else (ROW_FIRST_PRESENT if input_row == "present" else ROW_FIRST_ABSENT)
    fields = "row, id, premise, hypothesis, requested_tag" if input_row == "present" else "id, premise, hypothesis, requested_tag"
    prompt = SEMANTIC + instruction + f"Input records ({fields}):\n" + s.serialize(visible_records(context, relation, input_row == "present"))
    prior_row = {"arm": f"{relation}_labels_only", "seed": row["seed"]}
    body = copy.deepcopy(prior.request(context, prior_row))
    body.update(messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], seed=row["seed"], cache_salt=s.ROOT.name, structured_outputs=schema(row["arm"]))
    return body


def null_row(row, reason):
    return {"coordinate": row, "available": False, "strict_correct": None, "strict_bounds": [0, 48], "reason": reason}
