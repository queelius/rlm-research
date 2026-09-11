"""Exercise the adapted coordinator with external GPU boundaries replaced by fixtures."""
import argparse
import importlib
import time

import campaign_common as c


def test_seven_to_sixteen_and_fixed_final_transfer(tmp_path,monkeypatch):
    campaign=importlib.import_module('campaign');co=campaign.impl
    native=importlib.import_module('campaign_native')
    recipe=c.read(c.ROOT/'RECIPE.json');plans=c.read(c.ROOT/'inputs/PLANS.json')
    monkeypatch.setattr(c,'ROOT',tmp_path)
    c.write_once(tmp_path/'CAMPAIGN.json',{'campaign_id':'CPU_ONLY'})
    c.write_once(tmp_path/'RECIPE.json',recipe);c.write_once(tmp_path/'inputs/PLANS.json',plans)
    run=tmp_path/'run'
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','CPU_FAKE_NOT_A_DEVICE')
    c.write_once(run/'RUN.json',{'campaign_sha256':c.file_hash(tmp_path/'CAMPAIGN.json'),
        'gpu':'CPU_FAKE_NOT_A_DEVICE','started_epoch':time.time(),'deadline_epoch':time.time()+18000})
    policies={i:{'step':i} for i in range(8)}
    monkeypatch.setattr(c,'verify_campaign',lambda:{'campaign_id':'CPU_ONLY'})
    monkeypatch.setattr(co,'committed_policies',lambda directory:policies.copy())
    monkeypatch.setattr(co,'ports_free',lambda:True)
    monkeypatch.setattr(native,'authenticate_export',lambda path:None)
    started=[];collected=[]
    def service(directory,policy,deadline):
        started.append(policy['step']);return directory/'binding',directory/'endpoint'
    monkeypatch.setattr(co,'start_service',service)
    monkeypatch.setattr(co,'stop_service',lambda path:None)
    def stage(directory,phase,binding,endpoint,deadline,cap,generation=None):
        collected.append(phase)
        result={'strict_successes':15 if phase=='validation-8' else 2,
            'admitted_outcomes':16,'training_group_episodes':16,'integrity_failures':[]}
        c.write_once(directory/'export/MANIFEST.json',result)
        if generation: c.write_once(directory/'export/GROUP.json',{'fixture':True})
        return result
    monkeypatch.setattr(co,'stage',stage)
    for i in (0,4): stage(run/f'validation-{i:02d}',f'validation-{i}',None,None,0,0)
    def command(argv,log,timeout,**kwargs):
        g=c.read(argv[argv.index('--generation')+1]);step=g['round']
        assert step==max(policies)+1
        policies[step]={'step':step}
    monkeypatch.setattr(co,'owned_command',command)
    result=co.run_campaign(argparse.Namespace(output=run,resume=True))
    assert [x for x in collected if x.startswith('round-')]==[f'round-{i}' for i in range(8,17)]
    assert result['optimizer_steps']==result['final_policy']['step']==16
    assert result['selection']['descriptive_earliest_max_validation_step']==8
    assert result['selection']['policy']['step']==16
    assert started[-2:]==[0,16]
    assert list(result['transfer'])==['original','final']
    assert 'validation-8' in collected and 'validation-12' in collected and 'validation-16' in collected
