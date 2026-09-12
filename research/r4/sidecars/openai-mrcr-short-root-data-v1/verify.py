"""Read-only source/rank/gold/query-byte validation of the finalized data-only freeze."""

import hashlib
import json
import stat
from pathlib import Path

import prepare as source


def verify():
    ready = source.read(source.ROOT / "DATA_READY_V2.json")
    if source.digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("V2 source identity differs")
    for path, expected in ready["closure_sha256"].items():
        if source.sha(path) != expected:
            raise ValueError("frozen source/input changed: " + path)
    public = source.read(ready["model_inputs_path"])
    ranking = source.read(source.ROOT / "RANKING.json")["ranking"]
    original_rows = [json.loads(line) for line in (source.INVENTORY / "ROWS.jsonl").read_text().splitlines()]
    reranked = sorted(ranking, key=lambda row: (hashlib.sha256((source.NAMESPACE + "|" + row["row_sha256"]).encode()).hexdigest(), row["row_sha256"]))
    if ranking != reranked or len(ranking) != 89:
        raise ValueError("namespace/full-row-hash ordering differs")
    selected = ranking[:48]
    gold_path = source.ROOT / "host/HOST_GOLD.json"
    if stat.S_IMODE(gold_path.stat().st_mode) != 0o600 or stat.S_IMODE(gold_path.parent.stat().st_mode) != 0o700:
        raise ValueError("protected gold mode differs")
    gold = source.read(gold_path)
    expected = {"train": selected[:32], "heldout": selected[32:]}
    for split, records in public.items():
        if len(records) != len(expected[split]) or len(records) != len(gold[split]):
            raise ValueError("exact32/16 inventory differs")
        for row, ranked in zip(records, expected[split], strict=True):
            original = original_rows[ranked["ordinal"]]
            raw = Path(row["prompt_json_path"]).read_bytes()
            if (row["source_row_sha256"] != ranked["row_sha256"]
                    or hashlib.sha256(raw).hexdigest() != original["full_prompt_sha256"]):
                raise ValueError("ranked original prompt bytes differ")
            messages = json.loads(raw)
            host = gold[split][row["id"]]
            if (Path(row["final_question_path"]).read_bytes() != messages[-1]["content"].encode()
                    or host["answer"].removeprefix(host["random_string_to_prepend"])
                    != messages[host["desired_msg_index"] + 1]["content"]
                    or not source.question_check(host, messages)["exact_question_match"]
                    or row["source_conversation_qwen_chat_input_tokens"] < 1000):
                raise ValueError("query/gold link or corrected token inventory differs")
    return {"passed": True, "ready_sha256": source.sha(source.ROOT / "DATA_READY_V2.json"),
            "identity": ready["identity"], "records": ready["records"], "pins": len(ready["closure_sha256"]),
            "host_gold_mode": "0600", "no_queries_or_optimizer": True}


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
