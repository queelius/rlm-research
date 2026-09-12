"""Seal the approved two-model CPU-qualified screen; never starts an inference engine."""
import importlib.metadata
import os
from pathlib import Path
import sys
import time

import owner
import service
import study as s


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
    assert not (s.ROOT/'READY.json').exists() and not s.ATTEMPT.exists()
    evidence=s.read(s.ROOT/'CPU_EVIDENCE_FINAL.json')
    assert evidence['returncode']==0 and '2 passed' in evidence['stdout']
    assert evidence['GPU_calls']==0 and evidence['model_weight_loads']==0
    assert len(evidence['actual_service_entrypoint_cpu_checks'])==2
    for path,expected in evidence['fixture_files_sha256'].items():assert s.sha(path)==expected,path
    owner.dependencies();service.environment_adapter();s.official_grade()
    closure={}
    inherited=[s.SHORT/'READY_V2.json',s.MUSIQUE/'READY.json',s.QWEN35/'READY.json']
    for path in inherited:
        value=s.read(path)
        for name,expected in value.get('closure_sha256',value.get('source_sha256',{})).items():
            assert name not in closure or closure[name]==expected,name
            closure[name]=expected
        closure[str(path)]=s.sha(path)
    paths=list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.md'))+list(s.INPUTS.glob('*.json'))
    paths += [s.ROOT/'CPU_EVIDENCE_FINAL.json',s.QWEN35/'WEIGHTS.json',
              s.QWEN35/'SHARD_HASH_OBSERVATION.json',service.ENV_SOURCE,s.NATIVE.resolve()]
    paths += [Path(p) for p in evidence['fixture_files_sha256']]
    for row in s.selected():
        paths += [Path(row['prompt_json_path']),Path(row['final_question_path'])]
    fixture_fidelity={}
    for arm in s.ARMS:
        s.renderer(arm)
        directory=s.ROOT/'cpu-fixture-004/test_actual_two_turn_native_te0'/arm
        derived=s.read(directory/'DERIVED.json')
        assert derived['initial_prefix_verified'] and derived['root_actions_returned']==2
        assert derived['child_actions_returned']==0 and derived['first_action']['schema_correct']
        f=derived['final_text_fidelity']
        strings={key:__import__('hashlib').sha256(f[key].encode()).hexdigest() for key in (
            'raw_model_final_stop_tokens_removed','parsed_native_final','original_harness_final')}
        fixture_fidelity[arm]={'derived_sha256':s.sha(directory/'DERIVED.json'),
            'episode_sha256':s.sha(directory/'EPISODE.json'),'UTF8_string_sha256':strings,
            'raw_equals_native_parsed':f['raw_equals_native_parsed'],
            'raw_to_native_difference_is_exactly_strip':f['raw_to_native_difference_is_exactly_strip'],
            'native_to_harness_difference_is_exactly_strip':f['native_to_harness_difference_is_exactly_strip']}
    # Pin actually imported implementation files in addition to the reviewed inherited closure.
    roots=('/project/alex_phd/','/home/atowell/')
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name and str(name).startswith(roots) and Path(name).suffix=='.py' and Path(name).is_file():
            paths.append(Path(name))
    for path in paths:
        name=str(path.resolve());actual=s.sha(path)
        assert name not in closure or closure[name]==actual,name
        closure[name]=actual
    for path,expected in closure.items():assert s.sha(path)==expected,path
    weights=s.read(s.QWEN35/'WEIGHTS.json')
    stats=weights['weight_stat_identity']
    for name,expected in stats.items():
        st=Path(name).stat();assert [st.st_size,st.st_mtime_ns,st.st_ino]==expected,name
    prefixes=s.read(s.PREFIX_FILE)
    assert len(prefixes)==16 and all(p['official_initial_template_equal'] for p in prefixes.values())
    assert all(len(p['token_ids'])+1024<=8192 for p in prefixes.values())
    packages={}
    for package in ('transformers','vllm','torch','renderers','verifiers','httpx','aiohttp',
                    'pydantic','jsonschema','tokenizers','openai'):
        packages[package]=importlib.metadata.version(package)
    ready={'schema':'released-controller-screen-ready-v1','status':'CPU_READY_MAIN_REVIEW_NO_GPU_LAUNCH',
        'created_epoch':time.time(),'identity':None,'closure_sha256':closure,
        'model_stat_receipts':stats,'models':s.MODELS,'adapter':None,'optimizer_steps':0,
        'fixed_argv':[str(s.NATIVE),str(s.ROOT/'owner.py'),'run'],'cwd':str(s.ROOT),
        'output':str(s.ATTEMPT),'schedule_sha256':s.digest(s.plan()),
        'data_manifest_sha256':s.sha(s.INPUTS/'MANIFEST.json'),
        'prefix_inventory_sha256':s.sha(s.PREFIX_FILE),
        'initial_max_prefix_plus_output':max(len(p['token_ids'])+1024 for p in prefixes.values()),
        'actual_every_call_prefix_plus_output_cap':8192,'native_output_tokens_per_call':1024,
        'max_physical_calls':32,'planned_episodes':16,'paired_contexts':8,'root_turns_per_episode':2,
        'children':0,'sampling':{'temperature':.5,'top_p':1.,'top_k':-1,'min_p':0.,'nonthinking':True,
            'seed_base':202609190000,'same_case_seed_across_models':True},
        'caps':{'science_per_arm':600,'science_total':1200,'owner':1800,'external':1900},
        'arm_order':list(s.ARMS),'batch_invariant':'explicitly disabled in both services',
        'CPU_evidence_sha256':s.sha(s.ROOT/'CPU_EVIDENCE_FINAL.json'),
        'CPU_fixture_files_sha256':evidence['fixture_files_sha256'],'CPU_fixture_fidelity':fixture_fidelity,
        'python':sys.version,'python_executable':str(s.NATIVE),'packages':packages,
        'primary':'original harness root_reply exact and untouched official MRCR scorer',
        'fidelity_diagnostics_do_not_replace_primary':True,
        'claim_boundary':'released-model/native-template/parser package usability on 8 exposed training contexts; no weight-only, recursion, learning or heldout-generalization claim',
        'GPU_launch_authority':'MAIN only; shared exclusive lock required'}
    del ready['identity'];ready['identity']=s.digest(ready)
    s.write_x(s.ROOT/'READY.json',ready)
    assert s.verify()==ready
    print({'READY_sha256':s.sha(s.ROOT/'READY.json'),'identity':ready['identity'],
           'pins':len(closure),'fixed_argv':ready['fixed_argv'],'caps':ready['caps']})


if __name__=='__main__':main()
