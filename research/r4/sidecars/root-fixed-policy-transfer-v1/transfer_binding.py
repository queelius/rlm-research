"""Reuse actual fixed-step ancestry checks, not a fresh checkpoint competition."""
import transfer_study as s
old=s.original_binding()
EXPECTED={'unchanged':s.START_SHA,'joint':'ffa49801af0cfc03daa0de51ccb3beed03b068d7f8c1b94ad57e418c2429fd00','reduction_stop':'eaa80a9f7243a2ceb283c954b7091ad0ab5838831c46c0c9e18a050fe32c81ac'}
def selected(arm):
    if arm not in EXPECTED:raise ValueError('unknown fixed policy')
    chosen=old.selected(arm)
    if chosen['adapter_sha256']!=EXPECTED[arm]:raise ValueError('fixed adapter changed')
    return chosen
def binding(arm,chosen):
    value=old.binding(arm,chosen);value['campaign_id']=s.ROOT.name
    value['fixed_policy_transfer']=dict(arm=arm,ready_sha256=s.sha(s.ROOT/'READY.json'),source_training_ready=str(s.OLD/'READY.json'),source_training_ready_sha256=s.sha(s.OLD/'READY.json'),no_training=True)
    return value
def validate(value,descriptor,path):
    arm=value['fixed_policy_transfer']['arm']
    if value!=binding(arm,selected(arm)):raise ValueError('actual fixed-policy binding changed')
    old.old.validate_descriptor(value,descriptor,s.sha(path))
