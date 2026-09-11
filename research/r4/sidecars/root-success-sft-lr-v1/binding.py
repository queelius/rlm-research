"""Low fixed8 and independently trained high fixed8; same actual root alias/child."""
import study as s

low=s.private('binding.py',view=s.old)
high=s.private('binding.py')


def training_source(arm):
    if arm not in ('low','high'):raise ValueError('unknown LR arm')
    return (s.OLD if arm=='low' else s.ROOT)/'outputs/attempt-001/training'


def selected(arm):
    training_source(arm)
    chosen=(low if arm=='low' else high).selected('success_sft')
    if arm=='low' and chosen['adapter_sha256']!=s.LOW_SHA:raise ValueError('not exact low fixed8')
    return chosen


def binding(arm,chosen):
    value=(low if arm=='low' else high).binding('success_sft',chosen)
    value['campaign_id']=s.ROOT.name
    value['success_sft_lr_study']={'arm':arm,'learning_rate':2e-5 if arm=='low' else 1e-4,'root_ready_sha256':s.sha(s.ROOT/'READY.json')}
    return value


validate_descriptor=low.validate_descriptor
