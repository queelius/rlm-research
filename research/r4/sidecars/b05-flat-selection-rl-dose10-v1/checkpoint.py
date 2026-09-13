"""Same complete checkpoint qualifier with exact prospective LR and initial-identity gate."""
import types
import study as s
import core

def qualified_source():
    text=(s.ORIGINAL/'checkpoint.py').read_text()
    for old,new in [('learning_rate=1e-4','learning_rate=1e-3'),("group[0]['lr']==1e-4","group[0]['lr']==1e-3"),
        ('expected=start-1e-4','expected=start-1e-3')]:
        assert text.count(old)==1; text=text.replace(old,new)
    return text

def endpoint():
    text=qualified_source()
    module=types.ModuleType('BA18_dose_checkpoint');module.__file__=str(s.ORIGINAL/'checkpoint.py')
    with s.aliases({'study':s,'core':core},s.ROOT):
        exec(compile(text,module.__file__,'exec'),module.__dict__);result=module.endpoint()
    paired=s.read(s.OUTPUT/'INITIAL_PAIRED.json');assert paired['exact'] and paired['reference_sha256']==s.sha(s.INITIAL_REFERENCE)
    import torch
    actual=torch.load(s.OUTPUT/'initial-trainable.pt',map_location='cpu',weights_only=True)
    expected=torch.load(s.INITIAL_REFERENCE,map_location='cpu',weights_only=True)
    core.exact_initial(actual,expected)
    result.update(exact_original_zero_B_initialization=True,initial_pair_receipt_sha256=s.sha(s.OUTPUT/'INITIAL_PAIRED.json'),learning_rate=1e-3,
        sole_recipe_change='10x learning rate; same original initialization, actions, masks, G2/all18, fresh AdamW, RNG and gates')
    return result
