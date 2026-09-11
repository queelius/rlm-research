"""Exact intermediate-checkpoint readout namespace."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "root-operator-dose-readout-v1"
ATTEMPT = ROOT / "outputs/attempt-001"
SOURCE_READY_SHA = "e51be544e14d037dcd92427310f5514609ea1f38f8ab33c176187d5433685f42"
_spec = importlib.util.spec_from_file_location("intermediate_dose_source_study", SOURCE / "dr_study.py")
base = importlib.util.module_from_spec(_spec); sys.modules[_spec.name] = base; _spec.loader.exec_module(base)
base.dose.check(SOURCE / "READY.json", SOURCE_READY_SHA)
sha, read, write, digest = base.sha, base.read, base.write, base.digest
NATIVE, aliases, OLD, JOINT, CHILD_SHA = base.NATIVE, base.aliases, base.OLD, base.JOINT, base.CHILD_SHA

CHECKPOINTS = {
    "sft6": (6, base.dose.START, "efe7efc1b7b1ed642d04a1bee0ea4a3d5a6c1ac5b9575f89ad22d3e3ac2518cb", "4825d2da2bf078bdb55918ee1fc0333270dec7740736d566c0ea19502499536a", "fa6c9a8b53cfc541b626779f08dcbbb4b7337eb96ad7e4aea4fbbcff949476bc"),
    "sft12": (12, base.dose.ATTEMPT / "training/checkpoint-0012", "1f1a201eb5f3f9a2322a7159c7c7821d50a77ac7e422ad9238beabe752b0b1c9", "9cab91502118f13b1a7d41118182a563285b23d2b1a77c8bd6e153ca38fe20bd", "93352c753e4548e57ca7906cae552b69fe1988e280076228c56bd5f99124349e"),
    "sft18": (18, base.dose.ATTEMPT / "training/checkpoint-0018", "bc3387d239d17af9e24dedd5592c81e6c5569994ba728d606394be246de13725", "9cab91502118f13b1a7d41118182a563285b23d2b1a77c8bd6e153ca38fe20bd", "a755108693d8ea0f8d67c19ffc2550b658781545fb5535d1eef1d56b67818e61"),
    "sft24": (24, base.dose.ATTEMPT / "training/checkpoint-0024", "94022838a64a530e1abc8daf6cd43502d8aec7d549b6bfec10dd4928b0ca9006", "9cab91502118f13b1a7d41118182a563285b23d2b1a77c8bd6e153ca38fe20bd", "75b3138884cf526503bba311dae932158b7305a4958b478f73d286ad3a755171"),
}


def select_panel(plan, gold):
    master = "operator-dose-intermediate-panel-v1"
    contexts = []
    for name in sorted({row["context_id"] for row in plan}):
        rows = [row for row in plan if row["context_id"] == name]
        contexts.append((rows, 2 if rows[0]["stratum"] == "root_new" else 1))
    # State: three operator counts, three scope counts, root-zero count, exposed-zero count.
    states = {(0, 0, 0, 0, 0, 0, 0, 0): (0, [])}
    for rows, size in contexts:
        updated = {}
        for choice in itertools.combinations(rows, size):
            add = [sum(row["operator"] == value for row in choice) for value in ("count", "distinct", "weight")]
            add += [sum(row["scope"] == value for row in choice) for value in ("all", "single", "union")]
            root_zero = sum(gold[row["context_id"]]["answers"][row["family"]] == 0 and row["stratum"] == "root_new" for row in choice)
            exposed_zero = sum(gold[row["context_id"]]["answers"][row["family"]] == 0 and row["stratum"] == "exposed_repeatability" for row in choice)
            score = sum(int(hashlib.sha256(f"{master}|{row['id']}".encode()).hexdigest(), 16) for row in choice)
            for state, (prior_score, prior_rows) in states.items():
                candidate = tuple(state[index] + add[index] for index in range(6)) + (state[6] + root_zero, state[7] + exposed_zero)
                if any(value > 6 for value in candidate[:6]) or candidate[6] > 2 or candidate[7] > 1:
                    continue
                value = (prior_score + score, prior_rows + list(choice))
                if candidate not in updated or value[0] < updated[candidate][0]:
                    updated[candidate] = value
        states = updated
    eligible = [(state, value) for state, value in states.items()
                if sorted(state[:3]) == [5, 5, 6] and sorted(state[3:6]) == [5, 5, 6] and state[6:] == (2, 1)]
    if not eligible:
        raise ValueError("no exact mechanically balanced panel")
    state, (_, selected) = min(eligible, key=lambda item: item[1][0])
    ids = [row["id"] for row in selected]
    digest = hashlib.sha256(json.dumps(ids, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    receipt = {
        "algorithm": "integer SHA256 sum minimization under explicit label-zero/operator/scope/context quotas",
        "fields_used": ["context_id", "id", "operator", "scope", "stratum", "gold_is_zero"],
        "model_outcome_fields_used": [],
        "state": state,
        "ordered_ids_sha256": digest,
    }
    return selected, receipt


def selected(policy):
    if policy not in CHECKPOINTS: raise ValueError("fixed checkpoints 6/12/18/24 only")
    step, directory, adapter, config, state = CHECKPOINTS[policy]
    if sha(directory / "adapter_model.safetensors") != adapter: raise ValueError("adapter hash")
    if sha(directory / "adapter_config.json") != config: raise ValueError("adapter config hash")
    if sha(directory / "state.json") != state or read(directory / "state.json")["step"] != step: raise ValueError("state hash/step")
    return {"checkpoint": str(directory), "step": step, "adapter_sha256": adapter,
            "config_sha256": config, "state_sha256": state,
            "rule": "fixed checkpoint ordinal; no performance selection"}


def binding(policy, chosen=None):
    chosen = chosen or selected(policy)
    value = base.binding(policy, chosen)
    value["study"] = ROOT.name; value["campaign_id"] = ROOT.name
    value["operator_dose_intermediate"] = {
        "policy": policy, "step": chosen["step"], "source_ready_sha256": SOURCE_READY_SHA,
        "fixed_checkpoint_no_performance_selection": True,
    }
    value["selection_path"] = str(Path(chosen["checkpoint"]) / "state.json")
    value["selection_sha256"] = chosen["state_sha256"]
    value["selection_semantics"] = "fixed checkpoint ordinal; contemporaneous new-seed comparison"
    value["operator_dose"]["final_rule"] = "fixed checkpoints 6/12/18/24; no performance selection"
    return value


def load(name, path, pin, mapping=None): return base.load(name, path, pin, mapping)
def runtime(): return base.runtime()
def interface(output): return base.interface(output)
def protocol(): return base.protocol()
def answer(records, labels, row): return base.answer(records, labels, row)


def stack():
    native = base.stack().native
    def task(context, prompt, gold, name):
        query = read(ROOT / "inputs/PROMPTS_ACCURATE.json")[name]["plain_query"]
        value = base.dose.original().qnative().make_task(context, query, gold, name)
        if value.data.prompt != prompt: raise ValueError("frozen native prompt changed")
        value.data = value.data.model_copy(update={"source_split": "intermediate-dose named-panel repeat"})
        return value
    return SimpleNamespace(native=SimpleNamespace(**{**vars(native), "task": task}))


def validate(value, descriptor, path):
    if value != binding(value["operator_dose_intermediate"]["policy"]): raise ValueError("actual binding differs")
    joint = base.dose.original().joint()
    old = load("intermediate_dose_descriptor_validator", joint.SOURCE / "binding.py",
               "865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1",
               {"study": joint.original})
    old.validate_descriptor(value, descriptor, sha(path))


def verify():
    ready = read(ROOT / "READY.json")
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]: raise ValueError("identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items(): base.dose.check(path, pin)
    base.verify(); return ready
