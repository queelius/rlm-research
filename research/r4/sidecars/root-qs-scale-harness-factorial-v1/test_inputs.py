import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / "inputs" / name).read_text())


def test_frozen_inventory_and_exclusions_are_exact():
    public = read("PUBLIC.json")
    groups = read("GROUPS.json")
    provenance = read("PROVENANCE.json")
    selected = provenance["selected_group_ids"]
    assert provenance["base_pool"] == 5065
    assert provenance["eligible"] == 1961
    assert provenance["excluded"] == 3104
    assert len(selected) == len(set(selected)) == 1024
    assert not set(selected) & set(provenance["excluded_group_ids"])
    assert len(public) == len(groups) == 16
    assert all(group["group_ids"] == selected[group["cluster"] * 256 : group["cluster"] * 256 + group["size"]] for group in groups)


def test_ready_seals_native_prompts_and_all_inputs():
    ready = json.loads((ROOT / "READY_v3.json").read_text())
    body = {key: value for key, value in ready.items() if key != "identity"}
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    assert hashlib.sha256(encoded).hexdigest() == ready["identity"]
    assert ready["planned"] == 64
    assert ready["scientific_gpu_calls"] == 0
    prompts = read("PROMPTS_ACCURATE.json")
    plan = read("FREE_PLAN.json")
    assert set(prompts) == {row["id"] for row in plan}
    assert all(row["prefix_tokens"] + 2048 <= 32768 for row in prompts.values())
    for path, expected in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected
