"""Read-only post-hoc audit: printed evidence is not a correct extraction program."""

import ast
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
SIDE = HERE.parents[1] / "sidecars/openai-mrcr-short32-base-calibration-v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def main():
    signal_path = HERE / "SIGNAL_ADDENDUM.json"
    if sha(signal_path) != "396bda9a0f914aaec53d4141367d532dd46303cffdf8a0f96477d84273d59e51":
        raise ValueError("source signal changed")
    gold = read(SIDE / "inputs/HOST_GOLD.json")
    public = read(SIDE / "inputs/PUBLIC.json")
    rows = []
    for row in read(signal_path)["records"]:
        if (row.get("official_raw_reward") or 0) < 0.9:
            continue
        path = Path(row["episode_path"])
        if sha(path) != row["episode_sha256"]:
            raise ValueError("episode changed")
        trace = read(path)["episode"]["traces"][0]
        context_sha = public["context_sha256_by_record"][row["record_id"]]
        context_path = SIDE / "inputs/contexts" / (context_sha + ".json")
        if sha(context_path) != context_sha:
            raise ValueError("public context changed")
        context = read(context_path)
        truth = gold[row["record_id"]]
        target = truth["answer"].removeprefix(truth["random_string_to_prepend"])
        variants = {
            "raw": target,
            "python_repr_body": repr(target)[1:-1],
            "json_string_body": json.dumps(target)[1:-1],
        }
        tools, parsed_prints = [], []
        for node in trace["nodes"]:
            message = node.get("message") or {}
            if message.get("role") == "assistant":
                for call in message.get("tool_calls") or []:
                    if call.get("name") != "ipython":
                        continue
                    arguments = json.loads(call["arguments"])
                    # Parse only; never execute generated code.
                    tree = ast.parse(arguments["code"])
                    parsed_prints.extend(
                        ast.unparse(item)
                        for item in ast.walk(tree)
                        if isinstance(item, ast.Call)
                        and isinstance(item.func, ast.Name)
                        and item.func.id == "print"
                        and any(isinstance(n, ast.Name) and n.id == "data" for n in ast.walk(item))
                    )
            if message.get("role") == "tool":
                content = message.get("content") or ""
                tools.append({
                    "characters": len(content),
                    "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
                    "traceback_present": "Traceback" in content,
                    "truncation_warning_present": content.startswith("Warning: truncated output"),
                    "full_target_representation_present": {key: value in content for key, value in variants.items()},
                    "tool_content_equals_exact_answer": content == truth["answer"],
                    "tool_content_equals_exact_answer_plus_stdout_newline": content == truth["answer"] + "\n",
                })
        rows.append({
            "coordinate_id": row["coordinate_id"], "record_id": row["record_id"],
            "episode_path": str(path), "episode_sha256": sha(path),
            "context_sha256": context_sha, "context_messages": len(context),
            "official_raw_reward": row["official_raw_reward"], "raw_exact": row["raw_exact"],
            "bulk_data_print_calls_parsed_not_executed": parsed_prints,
            "tool_observations": tools,
        })
    result = {
        "schema": "mrcr-short32-program-versus-terminal-posthoc-audit-v1",
        "created_epoch": time.time(), "source_signal_sha256": sha(signal_path),
        "source_script_sha256": sha(__file__), "selected_scope": "All four raw-similarity>=.90 outcomes; post-hoc mechanism review",
        "records": rows, "model_or_generated_code_execution": False,
        "claim_boundary": "A correct passage in a broad printed observation does not mean Python selected it correctly. No repaired score or direct-return counterfactual success is assigned.",
    }
    with (HERE / "PROGRAM_VS_TERMINAL_ADDENDUM.json").open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
