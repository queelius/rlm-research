from pathlib import Path
import importlib

ROOT=Path(__file__).resolve().parent
def module():
    assert (ROOT/'analyze.py').exists(),'paired raw analyzer not implemented'
    return importlib.import_module('analyze')

def test_actual_frozen_cp32_raw_decoding_and_fixed_denominator():
    a=module();stage=a.stage('held','cp32')
    assert stage['available']==stage['planned']==32
    assert stage['correct']==a.bindings().study.read(a.SIDE/'READY.json')['baselines']['held']['correct']
    assert stage['physical']['start_only']==0 and stage['physical']['error_results']==0
    assert not stage['integrity_errors'] and stage['initial_prefix_verified']==32
    assert all(row['cost']['child']['calls']==0 for row in stage['rows'].values())

def test_paired_missing_case_is_not_wrong_or_an_independent_repeat():
    a=module();plan=[{'id':str(i),'record_id':str(i//2),'repeat':i%2,'seed':i} for i in range(4)]
    def row(c,correct,available=True):
        return {'coordinate':c,'available':available,'raw_exact':correct,'mechanism':{'category':'fixture'},
                'native_actions':[],'programs_sha256':'x','observations_sha256':'x','cost':{r:{'calls':0,'prompt_tokens':0,'completion_tokens':0} for r in ('root','child')}}
    left={c['id']:row(c,i==1) for i,c in enumerate(plan)}
    right={c['id']:row(c,i in (0,1),i!=2) for i,c in enumerate(plan)}
    pair=a.pair(plan,left,right)
    assert pair['planned']==4 and pair['paired_available']==3 and pair['unknown_pairs']==1
    assert pair['wins']==1 and pair['losses']==0 and pair['context_units']==2
    assert pair['complete_context_pairs']==1 and pair['contexts_with_positive_paired_delta']==1
