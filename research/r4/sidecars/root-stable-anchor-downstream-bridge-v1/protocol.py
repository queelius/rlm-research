"""Frozen protocol helpers for the stable-anchor downstream bridge."""

import hashlib
import json

MASTER = 998431001
LABELS = ("entailment", "neutral", "contradiction")
USERS = ("Ada", "Ben", "Cy", "Dee")
GENRES = ("government", "slate", "telephone", "travel")
ENCODINGS = ("sequential_numeric", "opaque")
POLICIES = ("supplied", "free")
SYSTEM = (
    "You are a text classification assistant. Classify every supplied record and return only "
    "the requested JSON array. Do not use tools, write explanations, or reason aloud."
)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def anchor_values(context, encoding):
    if encoding == "sequential_numeric":
        return list(range(48))
    if encoding != "opaque":
        raise ValueError("unknown encoding")
    occupied = {row["id"] for row in context["records"]}
    values = []
    for row in context["records"]:
        nonce = 0
        while True:
            value = "k" + digest([MASTER, "opaque", context["id"], row["id"], nonce])[:12]
            if value not in occupied:
                break
            nonce += 1
        occupied.add(value); values.append(value)
    return values


def leaf_request(context, encoding, model="strict-rlm-qwen3-4b-child-c32"):
    keys = anchor_values(context, encoding)
    visible = [
        {"key": key, "id": row["id"], "premise": row["premise"], "hypothesis": row["hypothesis"]}
        for key, row in zip(keys, context["records"], strict=True)
    ]
    instruction = (
        "Classify the hypothesis against the premise in the same displayed object. Return exactly "
        "48 objects in displayed order, each with exactly key then label. Copy key exactly. label "
        "must be entailment, neutral, or contradiction. Input records:\n"
    )
    items = [{"type": "object", "properties": {
        "key": {"type": "integer" if isinstance(key, int) else "string", "const": key},
        "label": {"type": "string", "enum": list(LABELS)}},
        "required": ["key", "label"], "additionalProperties": False} for key in keys]
    return {"model": model, "messages": [{"role": "system", "content": SYSTEM},
        {"role": "user", "content": instruction + json.dumps(visible, separators=(",", ":"))}],
        "temperature": .5, "top_p": 1, "top_k": -1, "min_p": 0,
        "repetition_penalty": 1, "presence_penalty": 0, "frequency_penalty": 0,
        "seed": 998431101 + context["index"], "max_tokens": 3072,
        "return_token_ids": True, "chat_template_kwargs": {"enable_thinking": False},
        "cache_salt": "root-stable-anchor-downstream-bridge-v1",
        "structured_outputs": {"json": {"type": "array", "minItems": 48, "maxItems": 48,
            "items": False, "prefixItems": items}}}


def broker(content, context, encoding):
    values = json.loads(content)
    if not isinstance(values, list) or len(values) != 48:
        raise ValueError("expected exactly 48 leaf objects")
    keys = anchor_values(context, encoding)
    labels = []
    for index, value in enumerate(values):
        if (not isinstance(value, dict) or list(value) != ["key", "label"]
                or value["key"] != keys[index] or value["label"] not in LABELS):
            raise ValueError("invalid ordered leaf key/label contract")
        labels.append(value["label"])
    return {row["id"]: label for row, label in zip(context["records"], labels, strict=True)}


def reduce_answer(context, labels, question):
    if set(labels) != {row["id"] for row in context["records"]}:
        raise ValueError("incomplete canonical map")
    selected = [row for row in context["records"] if row["user"] in question["users"]
                and labels[row["id"]] == question["relation"]]
    if question["operator"] == "count":
        return len(selected)
    if question["operator"] == "weight":
        return sum(row["weight"] for row in selected)
    raise ValueError("unknown operator")


def question_text(question):
    users = ", ".join(question["users"])
    if question["operator"] == "count":
        return f"Count records whose user is one of [{users}] and whose NLI relation is {question['relation']}."
    return f"Sum weight for records whose user is one of [{users}] and whose NLI relation is {question['relation']}."


def root_plan(contexts):
    rows = []
    for context in contexts:
        for qi, question in enumerate(context.get("questions", [
            {"operator": "count", "relation": "entailment", "users": ["Ada"]},
            {"operator": "weight", "relation": "neutral", "users": ["Ben"]},
        ])):
            seed = 998431301 + 10 * context["index"] + qi
            cells = [(e, policy) for policy in POLICIES for e in ENCODINGS]
            if int(digest([MASTER, context["id"], qi])[-1], 16) % 2:
                cells.reverse()
            block = []
            for encoding, policy in cells:
                row = {"context_id": context["id"], "context_index": context["index"],
                    "query_index": qi, "question": question, "encoding": encoding,
                    "policy": policy, "seed": seed, "temperature": .5,
                    "records": 48, "pair_id": digest([context["id"], qi]),
                    "target": question["relation"], "users": question["users"],
                    "family": question["operator"], "question_text": question_text(question)}
                row["id"] = digest(["downstream-bridge", row]); block.append(row)
            rows.extend(block)
    return rows


def root_prompt(context, row):
    api = "classify_all() returns the complete canonical {public_record_id: nli_label} map."
    plan = (" Execute exactly this procedure: import classify_all from map_api; call it once; "
            "select records by the requested users and relation; compute the requested count or "
            "weight sum; print the scalar; then return only Answer: N." if row["policy"] == "supplied"
            else " You may use the documented map_api while solving the task.")
    public = [{k: record[k] for k in ("id", "user", "weight", "text")}
              for record in context["records"]]
    return api + plan + "\nRecords:\n" + json.dumps(public, separators=(",", ":")) + "\nQuestion: " + question_text(row["question"])
