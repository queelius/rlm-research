"""Exact recovery checkpoint binding; fixed24 start and child remain unchanged."""
import recovery_study as s
import qs_binding as qualified


def selected(arm):
    if arm != "sft6": raise ValueError("recovery serves only sft6")
    value = s.read(s.ATTEMPT / "training/SELECTION.json")
    if value["step"] != 6 or s.sha(value["checkpoint"] + "/adapter_model.safetensors") != value["adapter_sha256"]:
        raise ValueError("exact recovered fixed6 unavailable")
    return value


def binding(arm):
    return qualified.binding("sft6", selected(arm))

