"""Unchanged qualified math, plus mandatory actual tensor identity at initialization."""
import study as s
with s.aliases({'study':s},s.ORIGINAL):original=s.load('BA18_dose_original_core',s.ORIGINAL/'core.py')
for name in ('math','scorer','selected_logprobs','replay_check','save_rng','restore_rng','selection_loss'):
    globals()[name]=getattr(original,name)

def exact_initial(actual,expected):
    import torch
    assert list(actual)==list(expected),'initial parameter order changed'
    assert all(torch.equal(actual[k],expected[k]) for k in actual),'initial tensors differ from original zero-B branch'

def initialize(base):
    import torch
    model=original.initialize(base)
    actual=math.snapshot_trainable(model)
    expected=torch.load(s.INITIAL_REFERENCE,map_location='cpu',weights_only=True)
    exact_initial(actual,expected)
    s.write_x(s.OUTPUT/'INITIAL_PAIRED.json',dict(exact=True,reference_path=str(s.INITIAL_REFERENCE),
        reference_sha256=s.sha(s.INITIAL_REFERENCE),initial_identity=math.snapshot_digest(actual),
        fresh_seeded_zero_B=True,prior_updated_weights_loaded=False))
    return model
