"""Exact old24 versus fixed new6; no partial checkpoint substitution."""
import qs_study as s
old=s.load('qs_qualified_fixed_selection',s.OLD/'od_binding.py',s.cf_ready['source_sha256'][str(s.OLD/'od_binding.py')],{'od_study':s})
selected=old.selected
def binding(arm,chosen=None):
    chosen=chosen or selected(arm);value=s.read(s.ROOT/'inputs/START_BINDING.json')['base_binding']
    value['models'].pop(value['role_map']['root']);alias='strict-rlm-qwen3-4b-question-sensitive-'+arm+'-v1'
    value['models'][alias]=dict(path=chosen['checkpoint'],adapter_sha256=chosen['adapter_sha256'],config_sha256=chosen['config_sha256']);value['role_map']['root']=alias
    value.pop('procedural_card',None);value['study']=s.ROOT.name;value['campaign_id']=s.ROOT.name
    value['question_sensitive']=dict(arm=arm,starting_adapter_sha256=s.starting_policy()['adapter_sha256'],fixed_new_updates=6,no_test_card=True)
    if value['models'][value['fixed_child']]['adapter_sha256']!=s.CHILD_SHA:raise ValueError('fixed c32')
    return value
def validate(value,descriptor,path):
    if value!=binding(value['question_sensitive']['arm']):raise ValueError('actual binding changed')
    j=s.joint();validator=s.load('qs_qualified_descriptor',j.SOURCE/'binding.py','865e84908e4f8f198c81587605a37c003fe7f02c69bf1bbbd0fc8c495c18afd1',{'study':j.original})
    validator.validate_descriptor(value,descriptor,s.sha(path))
