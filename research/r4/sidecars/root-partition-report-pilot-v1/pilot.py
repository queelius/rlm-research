"""Frozen synthetic purchase-join diagnostic; no model imports or execution."""

import json
import random

GENERATOR_SEEDS = [981409091, 981409092, 981409093, 981409094]
SAMPLING_SEEDS = [981409101, 981409111]
QUERY = "Find every customer who purchased both product A and product B anywhere in the records."
ANSWER = "Return only a JSON array of distinct customer IDs in ascending order; use [] if none."
SYSTEM = "You solve purchase-record questions carefully. Each record states one purchase; record order has no temporal significance."


def solve(rows):
    products = {}
    for _, customer, product in rows:
        products.setdefault(customer, set()).add(product)
    return sorted(c for c, ps in products.items() if {"A", "B"} <= ps)


def worlds():
    result = []
    for wi, seed in enumerate(GENERATOR_SEEDS):
        rng = random.Random(seed)
        customers = [f"c{i:02d}" for i in range(1, 13)]
        rng.shuffle(customers)
        record_ids = [f"r{i:02d}" for i in range(1, 49)]
        rng.shuffle(record_ids)
        records, colocated, cross = [], [[], [], []], [[], [], []]
        for ci, customer in enumerate(customers):
            products = (
                ["A", "B", "C", "D"]
                if ci < 3 + 2 * wi
                else (["A", "C", "C", "D"] if ci % 2 else ["C", "B", "C", "D"])
            )
            for pi, product in enumerate(products):
                row = [record_ids[4 * ci + pi], customer, product]
                records.append(row)
                colocated[ci // 4].append(row)
                cross[(ci + pi) % 3].append(row)
        rng.shuffle(records)
        for chunks in (colocated, cross):
            for chunk in chunks:
                rng.shuffle(chunk)
        result.append(
            {
                "id": f"world-{wi}",
                "generator_seed": seed,
                "sample_seed": SAMPLING_SEEDS[wi % 2],
                "records": records,
                "gold": solve(records),
                "customers": sorted(customers),
                "partitions": {"colocated": colocated, "cross": cross},
            }
        )
    return result


def plan():
    coordinates = []
    for wi, world in enumerate(worlds()):
        # Alternate partition order across worlds before observing outcomes.
        partitions = ["colocated", "cross"] if wi % 2 == 0 else ["cross", "colocated"]
        for partition in partitions:
            coordinates.append(
                {
                    "id": world["id"] + "-" + partition,
                    "world_id": world["id"],
                    "partition": partition,
                    "records": world["records"],
                    "chunks": world["partitions"][partition],
                    "gold": world["gold"],
                    "customers": world["customers"],
                    "seed": world["sample_seed"],
                    "world_index": wi,
                    "parent_order": ["ordinary", "lossy", "full"][wi % 3 :]
                    + ["ordinary", "lossy", "full"][: wi % 3],
                }
            )
    return coordinates


def render_record(row):
    return f"{row[0]}: customer {row[1]} purchased product {row[2]}."


def request(identifier, text, seed, max_tokens, role):
    return {
        "id": identifier,
        "role": role,
        "seed": seed,
        "max_new_tokens": max_tokens,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
        "generation": {
            "do_sample": True,
            "temperature": 0.6,
            "top_p": 0.95,
            "top_k": 0,
            "repetition_penalty": 1.0,
            "use_cache": True,
        },
    }


def original(coordinate):
    return (
        QUERY
        + "\nCustomers: "
        + ", ".join(coordinate["customers"])
        + "\nRecords:\n"
        + "\n".join(render_record(row) for row in coordinate["records"])
    )


def static_requests(coordinate):
    children = []
    for ci, chunk in enumerate(coordinate["chunks"]):
        chunk_text = "\n".join(render_record(row) for row in chunk)
        ordinary = (
            QUERY + "\nYou see only one of three chunks. Report the information a parent needs "
            "to answer this global question using all chunks. Partial facts may matter across chunks. "
            "Choose your own report format.\nThis chunk:\n" + chunk_text
        )
        incidence = (
            QUERY + "\nYou see only one of three chunks. Extract every purchase in this chunk "
            "as a JSON array of triples [record_id, customer_id, product]. Preserve all records and "
            "their IDs, including partial evidence and products C/D. Return only that JSON array.\nThis chunk:\n"
            + chunk_text
        )
        variants = [("extract", incidence), ("ordinary", ordinary)]
        if coordinate["world_index"] % 2:
            variants.reverse()
        for role, text in variants:
            children.append(
                request(
                    coordinate["id"] + f"-{role}-{ci}", text, coordinate["seed"] + ci, 768, role
                )
            )
    for arm, cap in (("direct_short", 256), ("direct_expanded", 2560)):
        children.append(
            request(
                coordinate["id"] + "-" + arm,
                original(coordinate) + "\n" + ANSWER,
                coordinate["seed"],
                cap,
                arm,
            )
        )
    return children


def extract(content, chunk):
    try:
        rows = json.loads(content)
        valid = isinstance(rows, list) and all(
            isinstance(row, list) and len(row) == 3 and all(isinstance(value, str) for value in row)
            for row in rows
        )
        if not valid:
            raise ValueError("expected JSON triple array")
    except (ValueError, TypeError):
        return {
            "rows": None,
            "valid": False,
            "correct_triples": None,
            "precision": None,
            "recall": None,
        }
    truth = {tuple(row) for row in chunk}
    unique = {tuple(row) for row in rows}
    hits = len(unique & truth)
    return {
        "rows": rows,
        "valid": True,
        "correct_triples": hits,
        "precision": hits / len(unique) if unique else None,
        "recall": hits / len(truth),
        "duplicates": len(rows) - len(unique),
        "exact": sorted(rows) == sorted(chunk),
    }


def projections(calls, chunks):
    full, lossy = [], []
    for call, chunk in zip(calls, chunks, strict=True):
        parsed = extract(call.get("content"), chunk)
        # Never replace mistaken extracted fields with source or gold fields.
        rows = parsed["rows"]
        full.append({"evidence": rows, "valid_extraction": parsed["valid"]})
        lossy.append(
            {
                "local_winners": solve(rows) if rows is not None else None,
                "valid_extraction": parsed["valid"],
            }
        )
    ids = [call["id"] for call in calls]
    return (
        {"reports": full, "acquisition_call_ids": ids},
        {"reports": lossy, "acquisition_call_ids": ids},
    )


def parent_request(coordinate, arm, reports):
    text = (
        original(coordinate) + "\nThree advisory child reports follow. Reports may be incomplete "
        "or incorrect; the original records above remain available. local_winners means matches "
        "found within that one chunk only; evidence means extracted purchase triples. null means "
        "an unavailable or malformed extraction, not an empty result.\nReports:\n"
        + json.dumps(reports["reports"], separators=(",", ":"))
        + "\n"
        + ANSWER
    )
    return request(coordinate["id"] + "-parent-" + arm, text, coordinate["seed"], 256, arm)


def score(content, gold, customers):
    try:
        answer = json.loads(content)
        valid = (
            isinstance(answer, list)
            and all(isinstance(x, str) and x in customers for x in answer)
            and len(answer) == len(set(answer))
            and answer == sorted(answer)
        )
        if not valid:
            raise ValueError("invalid final array")
    except (ValueError, TypeError):
        return {"valid": False, "answer": None, "correct": False}
    return {"valid": True, "answer": answer, "correct": answer == gold}


def cost(calls):
    return {
        "calls": len(calls),
        **{
            key: sum(call[key] for call in calls)
            if all(call.get(key) is not None for call in calls)
            else None
            for key in ("prompt_tokens", "output_tokens", "seconds")
        },
    }


def episode(coordinate, calls):
    indexed = {call["id"]: call for call in calls}
    prefix = coordinate["id"]
    endpoints = {}
    for arm in ("ordinary", "lossy", "full", "direct_short", "direct_expanded"):
        identifier = prefix + ("-" if arm.startswith("direct") else "-parent-") + arm
        final = indexed.get(identifier)
        acquisition = (
            []
            if arm.startswith("direct")
            else [
                prefix + f"-{'ordinary' if arm == 'ordinary' else 'extract'}-{i}" for i in range(3)
            ]
        )
        required = acquisition + [identifier]
        complete = all(k in indexed and indexed[k].get("content") is not None for k in required)
        endpoints[arm] = {
            "score": score(final.get("content"), coordinate["gold"], coordinate["customers"])
            if final and final.get("content") is not None
            else None,
            "complete_pipeline": complete,
            "acquisition_call_ids": acquisition,
            "cost": cost([indexed[k] for k in required if k in indexed]),
        }
    extractions = [
        extract(indexed.get(prefix + f"-extract-{i}", {}).get("content"), chunk)
        for i, chunk in enumerate(coordinate["chunks"])
    ]
    if all(e["valid"] for e in extractions):
        implied = {
            "full": solve(sum([e["rows"] for e in extractions], [])),
            "lossy": sorted(set(sum([solve(e["rows"]) for e in extractions], []))),
        }
        for arm, answer in implied.items():
            endpoints[arm]["report_implied_answer"] = answer
            endpoints[arm]["reports_imply_gold"] = answer == coordinate["gold"]
            actual = endpoints[arm]["score"]
            endpoints[arm]["matches_report_implication"] = (
                actual["answer"] == answer if actual and actual["valid"] else None
            )
    return {
        "id": prefix,
        "world_id": coordinate["world_id"],
        "partition": coordinate["partition"],
        "gold": coordinate["gold"],
        "actual_calls": len(calls),
        "endpoints": endpoints,
        "extraction": extractions,
    }
