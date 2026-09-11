import runtime as r
import results


def test_later_global_cap_does_not_censor_prior_completed_answer():
    raw=r.read(r.ROOT/'qualification-attempt-001/control-EPISODE.json')
    audits={}
    for path in (r.ROOT/'qualification-attempt-001/role-audit').glob('*-result.json'):
        value=r.read(path)
        audits[value['request_id']]={**value,'_path':str(path),'_sha':r.file_hash(path)}
    record={'episode':raw,'timing':{'wall_seconds':1},'budget_censored':False,'coordinate':{'arm':'control'}}
    good=results.episode_record(record,audits)
    assert good['observable_reward']==1 and not good['budget_censored']
    # Completed observable wrong stays zero, not null, before a later global STOP.
    import copy
    wrong=copy.deepcopy(record)
    wrong['episode']['traces'][-1]['rewards']['correctness']['score']=0
    wrong['episode']['traces'][-1]['root_reply']='Answer: 99'
    assert results.episode_record(wrong,audits)['observable_reward']==0
    later={'episode':{'ok':False,'traces':[],'errors':[]},'timing':{'wall_seconds':1},
        'budget_censored':True,'coordinate':{'arm':'child_role_suffix'}}
    stopped=results.episode_record(later,audits)
    assert stopped['observable_reward'] is None and stopped['budget_censored']
    assert good['observable_reward']==1
    assert good['root_calls']==2 and good['child_calls']==2
    assert len(good['invocations'])==2
