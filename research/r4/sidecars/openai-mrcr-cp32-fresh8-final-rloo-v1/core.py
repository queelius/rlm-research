"""Only the previously exercised mathematical/scoring primitives, not its old runner."""
import sys
import study

math=study.load('fresh8rloo_existing_token_math',study.PRIOR/'math_core.py')
old={n:sys.modules.get(n) for n in ('study','math_core')}
sys.modules.update(study=study,math_core=math)
try:scorer=study.load('fresh8rloo_existing_selected_scorer',study.PRIOR/'trainer.py')
finally:
    for n,v in old.items():
        if v is None:sys.modules.pop(n,None)
        else:sys.modules[n]=v
selected_logprobs=scorer.selected_logprobs
replay_check=scorer.replay_check
save_rng=scorer.save_rng
restore_rng=scorer.restore_rng

def loss(values,weights,advantage):
    return next(iter(math.token_tis_terms([[values]],[[weights]],[advantage],denominator=32)))
