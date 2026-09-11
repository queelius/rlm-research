"""Same fixed6 binding, with the training-only output namespace."""
import recovery_study_v3 as s
import recovery_binding_v3 as qualified

OUTPUT = s.SOURCE_ROOT / 'outputs/attempt-002'


def selected(arm):
    if arm != 'sft6':
        raise ValueError('only fixed6 is available')
    value = s.read(OUTPUT / 'training/SELECTION.json')
    if value['step'] != 6:
        raise ValueError('fixed6 required; no partial selection')
    if s.sha(value['checkpoint'] + '/adapter_model.safetensors') != value['adapter_sha256']:
        raise ValueError('fixed6 adapter changed')
    return value


def binding(arm):
    return qualified.qualified.binding('sft6', selected(arm))


def validate(value, descriptor, path):
    if value != binding(value['question_sensitive']['arm']):
        raise ValueError('training-only recovered binding changed')
    j = s.base.joint()
    validator = s.load('postcapture_descriptor', j.SOURCE / 'binding.py',
        '865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1',
        {'study': j.original})
    validator.validate_descriptor(value, descriptor, s.sha(path))
