"""Freeze all eight scale episodes and forty genuine c32 native requests."""
import copy
import json
import time

import protocol as p
import study as s

NAMESPACE = "root-lambda-supplied-plan-ceiling-20260910-v1"
SEEDS = tuple(999411101 + index for index in range(8))
DEFINITIONS = """Classify the type of answer requested, not words mentioned in the question.
human being: a person, an organization or group of people, or a person's role, title or description.
location: a geographic place, including a city, country, state, mountain or other place.
abbreviation: a shortened form, or the expanded wording represented by a shortened form.
entity: a nonhuman, nongeographic thing or name, including objects, organisms, works, events, substances, methods or synonymous terms.
description and abstract concept: a definition, explanation, reason or manner of doing something, rather than a particular name or number.
numeric value: a quantity, count, measurement, date, duration, rank or numerical code."""


def selected_episodes():
    if s.sha(s.SCALE / "READY_v3.json") != "35189b02f0604e8c9292d3cdf8458f0532bb8811b270534d1a061b7c3c281159":
        raise ValueError("scale READY changed")
    public = s.read(s.SCALE / "inputs/PUBLIC.json")
    host = s.read(s.SCALE / "inputs/HOST_GOLD.json")
    rows = s.read(s.SCALE / "inputs/FREE_PLAN.json")
    specs = {row["context_id"]: {key: row[key] for key in
             ("family", "operator", "target", "target_b", "scope", "users", "threshold")}
             for row in rows}
    episodes = [copy.deepcopy(row) for row in public if row["size"] in (64, 256)]
    episodes.sort(key=lambda row: (row["cluster"], row["size"]))
    return episodes, {row["id"]: copy.deepcopy(host[row["id"]]) for row in episodes}, specs


def build_plan(episodes, specs):
    plan = []
    for episode_index, episode in enumerate(episodes):
        spec = specs[episode["id"]]
        for batch, start in enumerate(range(0, episode["size"], 32)):
            records = episode["records"][start:start + 32]
            row = {"context_id": episode["id"], "cluster": episode["cluster"],
                   "size": episode["size"], "episode_index": episode_index,
                   "batch": batch, "seed": SEEDS[episode_index], "n": len(records),
                   "ids": [record["id"] for record in records], **spec,
                   "model_policy": "c32", "root_model_calls": 0,
                   "dispatch_order": len(plan)}
            row["id"] = s.digest([NAMESPACE, row])
            plan.append(row)
    return plan


def prompt(records):
    visible = [{"id": row["id"], "text": row["text"]} for row in records]
    return ("Classify the type of answer requested by each question using these TREC definitions:\n"
            + DEFINITIONS
            + "\nReturn only one JSON object mapping every supplied id exactly once to one of "
              "the six full category labels listed above. No missing or extra ids.\nRecords: "
            + json.dumps(visible, separators=(",", ":"), ensure_ascii=False))


def bodies(plan, episodes):
    template = copy.deepcopy(next(iter(s.read(s.QUERY / "inputs/REQUESTS.json").values())))
    _, tokenizer = s.renderer(); decoded = tokenizer.decode(template["token_ids"])
    marker = "<|im_start|>user\n"; start = decoded.index(marker) + len(marker)
    end = decoded.index("<|im_end|>\n<|im_start|>assistant", start)
    prefix, suffix = decoded[:start], decoded[end:]
    records = {episode["id"]: {row["id"]: row for row in episode["records"]}
               for episode in episodes}
    result = {}
    for coordinate in plan:
        batch = [records[coordinate["context_id"]][identifier]
                 for identifier in coordinate["ids"]]
        body = copy.deepcopy(template); body["model"] = s.binding()["fixed_child"]
        body["token_ids"] = tokenizer.encode(prefix + prompt(batch) + suffix,
                                               add_special_tokens=False)
        body["sampling_params"]["seed"] = coordinate["seed"]
        schema = {"type": "object", "properties": {
            identifier: {"type": "string", "enum": list(p.CATEGORIES)}
            for identifier in sorted(coordinate["ids"])},
            "required": coordinate["ids"], "additionalProperties": False}
        body["sampling_params"]["structured_outputs"]["json"] = schema
        if len(body["token_ids"]) + 2048 > 8192: raise ValueError("native context admission")
        result[coordinate["id"]] = body
    return result


def seed_scan():
    started = time.time(); needles = {str(seed) for seed in SEEDS}; matches = []
    for path in sorted(s.SIDE.glob("*/inputs/*.json")):
        if s.ROOT in path.parents: continue
        text = path.read_text(errors="replace")
        found = sorted(seed for seed in needles if seed in text)
        if found: matches.append({"path": str(path), "seeds": found})
    return {"started_epoch": started, "ended_epoch": time.time(),
            "scope": "named sidecar input JSON files existing at scan time", "matches": matches}


def main():
    episodes, host, specs = selected_episodes(); plan = build_plan(episodes, specs)
    requests = bodies(plan, episodes); scan = seed_scan()
    if scan["matches"]: raise ValueError("seed collision; no reroll")
    for episode in episodes:
        diagnostic = p.reduce_j1(episode["records"], host[episode["id"]]["labels"],
                                 specs[episode["id"]])
        if diagnostic["answer"] != host[episode["id"]]["answers"]["J1"]:
            raise ValueError("gold reducer diagnostic mismatch")
    sources = [s.SCALE / "READY_v3.json", s.SCALE / "inputs/PUBLIC.json",
               s.SCALE / "inputs/HOST_GOLD.json", s.SCALE / "inputs/PROVENANCE.json",
               s.QUERY / "READY.json", s.QUERY / "inputs/REQUESTS.json"]
    s.write(s.ROOT / "inputs/PUBLIC.json", episodes)
    s.write(s.ROOT / "inputs/HOST_GOLD.json", host)
    s.write(s.ROOT / "inputs/PLAN.json", plan)
    s.write(s.ROOT / "inputs/REQUESTS.json", requests)
    s.write(s.ROOT / "inputs/PROMPT_IDS.json",
            {key: value["token_ids"] for key, value in requests.items()})
    s.write(s.ROOT / "inputs/SEED_SCAN.json", scan)
    s.write(s.ROOT / "inputs/PROVENANCE.json", {
        "schema": "supplied-plan-scale-provenance-v1", "created_epoch": time.time(),
        "source_sha256": {str(path): s.sha(path) for path in sources},
        "selection": "all four frozen scale clusters at sizes64 and256; no subset selection",
        "records_and_ids": "byte-equivalent JSON values copied from frozen scale PUBLIC",
        "host_gold_private_analysis_only": True,
        "child_optimizer_exposed": True, "root_research_exposed": True,
        "dataset_license": "underlying cached TREC data rights unspecified; no redistribution grant inferred",
    })
    s.write(s.ROOT / "CPU_INPUT_NATIVE.json", {
        "episodes": len(episodes), "planned_calls": len(plan),
        "sizes": [64, 256], "seeds": list(SEEDS),
        "max_prompt_tokens": max(len(body["token_ids"]) for body in requests.values()),
        "all_fit_8192_with_2048_output": True, "gold_reducer_diagnostics": 8,
        "gpu_calls": 0,
    })


if __name__ == "__main__": main()
