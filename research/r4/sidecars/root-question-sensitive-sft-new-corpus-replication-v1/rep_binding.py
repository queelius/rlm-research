"""Exact fixed24 capture and new-corpus checkpoint6 binding."""
from pathlib import Path
import rep_study as s
import qs_binding as qualified


def selected(arm):
    if arm == "unchanged":
        return s.starting_policy()
    if arm != "new_corpus_sft6":
        raise ValueError("fixed policy")
    directory = s.ATTEMPT / "training"
    result = s.read(directory / "RESULT.json"); chosen = s.read(directory / "SELECTION.json")
    start = s.starting_policy()
    if (not result["complete"] or result["identity"] != s.verify()["identity"] or
            result["optimizer_steps"] != 6 or result["selected"] != chosen or chosen["step"] != 6 or
            result["starting_adapter_sha256"] != start["adapter_sha256"] or
            not result["fresh_optimizer"] or result["child_loaded"] or result["child_updated"]):
        raise ValueError("exact new-corpus fixed6 required")
    previous = None; corpus = s.sha(s.ATTEMPT / "capture/CORPUS_READY.json")
    for step in range(1, 7):
        path = directory / f"checkpoint-{step:04}"; state = s.read(path / "state.json")
        if ((state["step"], state["epoch"], state["cursor"]) != (step, step, 0) or
                state["previous_state_sha256"] != previous or state["identity"] != result["identity"] or
                state["corpus_sha256"] != corpus):
            raise ValueError("checkpoint ancestry")
        for name, pin in state["files_sha256"].items():
            if Path(name).name != name or s.sha(path / name) != pin:
                raise ValueError("checkpoint member changed")
        previous = s.sha(path / "state.json")
    if chosen["checkpoint"] != str(path) or chosen["state_sha256"] != previous:
        raise ValueError("selection closure")
    return chosen


def binding(arm):
    if arm == "unchanged": value = qualified.binding("unchanged")
    else: value = qualified.binding("sft6", selected(arm))
    value["study"] = s.ROOT.name; value["campaign_id"] = s.ROOT.name
    value["question_sensitive"]["arm"] = arm
    value["question_sensitive"]["new_corpus_replication"] = True
    return value


def validate(value, descriptor, path):
    expected = binding(value["question_sensitive"]["arm"])
    if value != expected:
        raise ValueError("binding differs")
    joint = s.base.joint()
    validator = s.load("rep_qualified_descriptor", joint.SOURCE / "binding.py",
        "865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1",
        {"study": joint.original})
    validator.validate_descriptor(value, descriptor, s.sha(path))
