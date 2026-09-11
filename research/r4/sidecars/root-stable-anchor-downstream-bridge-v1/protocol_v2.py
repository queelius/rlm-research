"""Additive labels-only/sequential/opaque protocol; V1 remains frozen."""

import json
import protocol as old

MASTER = old.MASTER
LABELS = old.LABELS
USERS = old.USERS
ENCODINGS = ("labels_only", "sequential_numeric", "opaque")
POLICIES = old.POLICIES
digest = old.digest
anchor_values = old.anchor_values
reduce_answer = old.reduce_answer
question_text = old.question_text
root_prompt = old.root_prompt


def leaf_request(context, encoding, model):
    if encoding != "labels_only": return old.leaf_request(context, encoding, model)
    visible = [{"id": row["id"], "premise": row["premise"], "hypothesis": row["hypothesis"]}
        for row in context["records"]]
    return {"model": model, "messages": [{"role": "system", "content": old.SYSTEM},
        {"role": "user", "content": "Classify each hypothesis against the premise in the same displayed object. Return exactly 48 label strings in displayed order; each must be entailment, neutral, or contradiction. Return labels only. Input records:\n" + json.dumps(visible, separators=(",", ":"))}],
        "temperature": .5, "top_p": 1, "top_k": -1, "min_p": 0, "repetition_penalty": 1,
        "presence_penalty": 0, "frequency_penalty": 0, "seed": 998431101 + context["index"],
        "max_tokens": 3072, "return_token_ids": True, "chat_template_kwargs": {"enable_thinking": False},
        "cache_salt": "root-stable-anchor-downstream-bridge-v2",
        "structured_outputs": {"json": {"type": "array", "minItems": 48, "maxItems": 48,
            "items": {"type": "string", "enum": list(LABELS)}}}}


def broker(content, context, encoding):
    if encoding != "labels_only": return old.broker(content, context, encoding)
    values = json.loads(content)
    if not isinstance(values, list) or len(values) != 48 or any(type(v) is not str or v not in LABELS for v in values):
        raise ValueError("invalid 48-label positional contract")
    return {row["id"]: label for row, label in zip(context["records"], values, strict=True)}


def root_plan(contexts):
    rows = []
    for context in contexts:
        for qi, question in enumerate(context["questions"]):
            seed = 998431301 + 10 * context["index"] + qi
            cells = [(encoding, policy) for policy in POLICIES for encoding in ENCODINGS]
            if int(digest([MASTER, context["id"], qi])[-1], 16) % 2: cells.reverse()
            for encoding, policy in cells:
                row = {"context_id": context["id"], "context_index": context["index"], "query_index": qi,
                    "question": question, "encoding": encoding, "policy": policy, "seed": seed,
                    "temperature": .5, "records": 48, "pair_id": digest([context["id"], qi]),
                    "target": question["relation"], "users": question["users"],
                    "family": question["operator"], "question_text": question_text(question)}
                row["id"] = digest(["downstream-bridge-v2", row]); rows.append(row)
    return rows
