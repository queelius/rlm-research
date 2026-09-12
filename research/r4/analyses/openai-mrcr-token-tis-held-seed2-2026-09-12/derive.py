"""Two frozen seed blocks, all arms; saved code is parsed inertly, never executed."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
STORE=ROOT.parents[1]
SIDES=STORE/'sidecars'
ARMS=('base','lr1e-5','lr1e-4')
BLOCKS={
    'seed1':{'side':'openai-mrcr-short-root-token-tis-held-eval-v1','ready':'CPU_READY_V4.json',
             'ready_sha':'fb703d787841976e04a016e69e95841e1aa1ab4003840b0d4afb2cd0f8a0c65d',
             'study':'study_v4','checkpoint':'checkpoint_v4','owner':'owner_v4','collect':'collect_v4','outputs':'outputs-v4'},
    'seed2':{'side':'openai-mrcr-short-root-token-tis-held-seed2-v1','ready':'CPU_READY.json',
             'ready_sha':'25e43f052f9339cc80efe456911ce3b07c3db1a60d05b596b23c85fce919ae07',
             'study':'study','checkpoint':'checkpoint','owner':'owner','collect':'collect','outputs':'outputs'},
}
SOURCE_SHA256={}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def text_sha(value):return hashlib.sha256(value.encode()).hexdigest()
def read(path):
    path=Path(path);SOURCE_SHA256[str(path)]=sha(path)
    return json.loads(path.read_text())


def load(name,path):
    path=Path(path);SOURCE_SHA256[str(path)]=sha(path)
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module)
    return module


def pair(left,right):
    before={r['record_id']:r for r in left};after={r['record_id']:r for r in right}
    assert set(before)==set(after) and len(before)==16
    known=[(before[k],after[k]) for k in before if before[k]['available'] and after[k]['available']]
    return {'planned_contexts':16,'both_available':len(known),'unknown_either':16-len(known),
            'exact_wins_right':sum(not a['raw_exact'] and b['raw_exact'] for a,b in known),
            'exact_losses_right':sum(a['raw_exact'] and not b['raw_exact'] for a,b in known),
            'changed_first_programs':sum(a['first_program_sha256']!=b['first_program_sha256'] for a,b in known),
            'changed_known_replies':sum(a['root_reply_utf8_sha256']!=b['root_reply_utf8_sha256'] for a,b in known),
            'official_similarity_delta_sum_known':math.fsum(b['official_similarity']-a['official_similarity'] for a,b in known)}


def block(name):
    config=BLOCKS[name];side=SIDES/config['side'];sys.path.insert(0,str(side))
    ready=read(side/config['ready']);assert sha(side/config['ready'])==config['ready_sha']
    modules={key:load(config[key],side/(config[key]+'.py')) for key in ('study','checkpoint','owner','collect')}
    owner=modules['owner'];study=owner.study
    assert Path(study.ROOT)==side and Path(study.READY)==side/config['ready']
    owner.verify('base')
    inspector=modules['collect'].source_module()
    helpers=load('paired_tis_procedure_helpers',STORE/'analyses/openai-mrcr-shaped-root-update-2026-09-12/analyze.py')
    features=load('paired_tis_inert_ast',STORE/'analyses/openai-mrcr-procedural-sft-dose32-readout-2026-09-12/analyze.py')
    scorer=load('paired_tis_independent_raw_scorer',SIDES/'openai-mrcr-short-root-data-v1/official_score.py')
    source_derive=STORE/'analyses/openai-mrcr-token-tis-held-three-arm-2026-09-12/derive.py'
    SOURCE_SHA256[str(source_derive)]=sha(source_derive)
    plan={r['id']:r for r in study.schedule('held')}
    golds=read(study.input_dir('held')/'HOST_GOLD.json');prefixes=read(study.input_dir('held')/'PREFIXES.json')
    public=read(study.input_dir('held')/'PUBLIC.json');assert public['plan']==list(plan.values())
    arms={}
    for arm in ARMS:
        output=side/config['outputs']/(arm+'-001');assert owner.STAGES[arm]==output
        terminal=read(output/'OWNER_TERMINAL.json');original=read(output/'science/RESULT.json')
        assert terminal['released'] and original['complete']
        binding=read(output/'owned-service/BINDING.json')
        natives=[(p,read(p)) for p in sorted((output/'science/native-calls').glob('*-result.json'))]
        native=[n for _,n in natives];wrappers=[];rows=[]
        for path in sorted((output/'science/episodes').glob('*.json')):
            wrapper=read(path);coordinate=wrapper['coordinate'];raw=wrapper['episode'];wrappers.append(wrapper)
            assert coordinate==plan[coordinate['id']] and study.digest(raw)==wrapper['episode_sha256']
            gold=golds[coordinate['record_id']];trace=raw['traces'][0]
            d=inspector.inspect_trace(raw,gold,native,prefixes[coordinate['id']]['token_ids'],wrapper['derived']['terminal_status']=='deadline_censored')
            assert d==wrapper['derived'],(name,arm,coordinate['record_id'],'saved derivation differs')
            reply=trace.get('root_reply');exact=isinstance(reply,str) and reply==gold['answer']
            score=scorer.grade(reply,gold['answer'],gold['random_string_to_prepend'])
            assert exact==d['raw_exact'] and (not d['scientifically_available'] or math.isclose(score,d['reward'],abs_tol=1e-12))
            returned=sorted([(p,n) for p,n in natives if n.get('session_id')==trace['id'] and n.get('model')==binding['role_map']['root'] and n.get('status')=='returned'],key=lambda v:v[1]['index'])
            physical=returned[0][1]['response']['tokens']['prompt_ids'] if returned else None
            assert physical==prefixes[coordinate['id']]['token_ids']
            finals=[(p,n) for p,n in returned if not n['response']['message'].get('tool_calls')]
            final_match=[(p,n) for p,n in finals if n['response']['message'].get('content')==reply]
            assert not reply or final_match,(name,arm,coordinate['record_id'],'raw native final mismatch')
            programs=[];observations=[]
            for node in trace['nodes']:
                message=node.get('message') or {}
                if message.get('role')=='tool':observations.append(message.get('content') or '')
                for call in message.get('tool_calls') or []:
                    if call.get('name')!='ipython':continue
                    args=call.get('arguments');args=json.loads(args) if isinstance(args,str) else args
                    code=args['code'];programs.append({'code_inert':code,'code_utf8_sha256':text_sha(code),**features.program_features(code,None)})
            clean_values={gold['answer'],gold['answer']+'\n',gold['answer'].removeprefix(gold['random_string_to_prepend']),gold['answer'].removeprefix(gold['random_string_to_prepend'])+'\n'}
            observations_detail=[{'characters':len(v),'sha256':text_sha(v),'clean_correct_target':v in clean_values,
                                   'traceback':'Traceback' in v,'tail':v[-180:]} for v in observations]
            row={'record_id':coordinate['record_id'],'row_index':coordinate['row_index'],'coordinate_id':coordinate['id'],'seed':coordinate['seed'],
                 'context_sha256':coordinate['context_sha256'],'source_row_sha256':coordinate['source_row_sha256'],
                 'episode_path':str(path),'episode_sha256':sha(path),'available':d['scientifically_available'],
                 'raw_exact':exact if d['scientifically_available'] else None,
                 'official_similarity':score if d['scientifically_available'] else None,
                 'root_reply_utf8_sha256':text_sha(reply) if isinstance(reply,str) else None,'gold_utf8_sha256':text_sha(gold['answer']),
                 'independent_raw_comparison_exact':exact,'native_nonempty_final_verified':bool(final_match) if reply else None,
                 'final_native_path':str(final_match[-1][0]) if final_match else None,
                 'initial_physical_prefix_sha256':study.digest(physical),'independently_verified_initial_prefix':True,
                 'first_program_sha256':programs[0]['code_utf8_sha256'] if programs else None,
                 'role_ordinal_successor_candidate':any(p['role_tests'] and p['ordinal_index'] and p['successor_index'] for p in programs),
                 'broad_document_dump_program':any(p['broad_document_dump'] for p in programs),
                 'clean_correct_target_observed':any(v['clean_correct_target'] for v in observations_detail),
                 'failure_class':d['failure_class'],'terminal_status':d['terminal_status'],
                 'trace_errors':trace.get('errors'),'root_actions':d['root_actions_returned'],'child_actions':d['child_actions_returned'],
                 **helpers.procedure(trace)}
            if exact or not row['available'] or coordinate['record_id']=='omrcr-2568744ab02d7c2786c8':
                row.update(programs=programs,observations=observations_detail)
            rows.append(row)
        assert len(rows)==16 and {r['coordinate_id'] for r in rows}==set(plan)
        rescored=inspector.summarize(wrappers,'held',arm)
        for key,value in rescored.items():assert original[key]==value,(name,arm,key)
        known=[r for r in rows if r['available']]
        arms[arm]={'owner_complete':terminal['complete'],'recorded':16,'available':len(known),'unknown':16-len(known),
                   'raw_exact':sum(r['raw_exact'] for r in known),'near_exact':sum(r['official_similarity']>=.9 for r in known),
                   'raw_similarity_sum':math.fsum(r['official_similarity'] for r in known),
                   'role_ordinal_successor_candidates':sum(r['role_ordinal_successor_candidate'] for r in rows),
                   'clean_correct_target_observed':sum(r['clean_correct_target_observed'] for r in rows),
                   'broad_document_dump_episodes':sum(r['broad_document_dump_program'] for r in rows),
                   'tool_tracebacks':sum(r['tool_tracebacks'] for r in rows),'rows':rows,
                   'binding':binding}
    paired={left+'_to_'+right:pair(arms[left]['rows'],arms[right]['rows']) for left,right in [('base','lr1e-5'),('base','lr1e-4'),('lr1e-5','lr1e-4')]}
    return {'seed_block':name,'arms':arms,'paired':paired,'source_sha256':SOURCE_SHA256,
            'all48_saved_derivations_reproduced':True,'all48_raw_final_gold_comparisons_independent':True,
            'all48_initial_physical_prefixes_independently_verified':True,'ready_identity':ready['identity']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--block',choices=BLOCKS);args=parser.parse_args()
    if args.block:
        print(json.dumps(block(args.block),sort_keys=True));return
    # Fresh interpreters prevent inherited generic study/checkpoint module aliases
    # from crossing the explicit first-block and second-block boundaries.
    blocks={name:json.loads(subprocess.run([sys.executable,str(Path(__file__)),'--block',name],capture_output=True,text=True,check=True).stdout) for name in BLOCKS}
    contexts=[]
    for ident in sorted({r['record_id'] for r in blocks['seed1']['arms']['base']['rows']}):
        units={seed:{arm:next(r for r in blocks[seed]['arms'][arm]['rows'] if r['record_id']==ident) for arm in ARMS} for seed in BLOCKS}
        flat=[r for arms in units.values() for r in arms.values()]
        assert len({r['context_sha256'] for r in flat})==len({r['gold_utf8_sha256'] for r in flat})==len({r['initial_physical_prefix_sha256'] for r in flat})==1
        contexts.append({'record_id':ident,'context_sha256':flat[0]['context_sha256'],'prefix_sha256':flat[0]['initial_physical_prefix_sha256'],
                         'by_seed':{seed:{arm:{k:row[k] for k in ('available','raw_exact','official_similarity','first_program_sha256','root_reply_utf8_sha256')} for arm,row in arms.items()} for seed,arms in units.items()}})
    for arm in ARMS:assert blocks['seed1']['arms'][arm]['binding']==blocks['seed2']['arms'][arm]['binding']
    sources={str(Path(__file__)):sha(Path(__file__))}
    for value in blocks.values():sources.update(value.pop('source_sha256'))
    result={'schema':'mrcr-token-tis-two-seed-block-fixed-three-arm-readout-v1','blocks':blocks,'context_units':contexts,
            'independent_context_units':16,'seed_blocks':2,'new_gpu_or_model_calls':0,'generated_code_executed':False,
            'unknowns_are_null_not_zero':True,'all_fixed_arms_retained':True,'both_blocks_same_context_gold_prefix_and_binding':True,
            'source_sha256':sources,'limits':['Two decoding draws of the same16 held contexts; never32 independent contexts.','Single fixed training corpus and gradient; not a training-seed replication.','Original scored final pipeline is unchanged; parser diagnostic is not a retroactive score correction.','Prior adaptive held-panel exposure precludes confirmatory transfer claims.']}
    output=ROOT/'DERIVED.json'
    with output.open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'path':str(output),'sha256':sha(output),'sources':len(sources),'blocks':{name:{'arms':{arm:{k:v for k,v in a.items() if k not in ('rows','binding')} for arm,a in block['arms'].items()},'paired':block['paired']} for name,block in blocks.items()}},indent=2))


if __name__=='__main__':main()
