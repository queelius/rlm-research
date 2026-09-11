"""V3 binding uses coherent study identity and recovered fixed6 validator."""
import recovery_study_v3 as s
import qs_binding as qualified


def selected(arm):
    if arm != "sft6": raise ValueError("recovery serves only sft6")
    value = s.read(s.ATTEMPT / "training/SELECTION.json")
    if value["step"] != 6 or s.sha(value["checkpoint"] + "/adapter_model.safetensors") != value["adapter_sha256"]:
        raise ValueError("exact recovered fixed6 unavailable")
    return value


def binding(arm):
    return qualified.binding("sft6", selected(arm))


def validate(value, descriptor, path):
    if value != binding(value["question_sensitive"]["arm"]):
        raise ValueError("actual recovered binding changed")
    j = s.base.joint()
    validator = s.load("qs_recovery_v3_qualified_descriptor", j.SOURCE / "binding.py",
        "865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1", {"study": j.original})
    validator.validate_descriptor(value, descriptor, s.sha(path))
