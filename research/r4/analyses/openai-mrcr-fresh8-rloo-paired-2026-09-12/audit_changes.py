"""Inert all-path comparison; token arrays are read, generated Python is never executed."""
import ast
from collections import Counter
from difflib import SequenceMatcher
import functools
import os
from pathlib import Path
import analyze as a

SOURCE_SHA='57f739304d92c03ff704f0edbbc494c8ae4cd4401ff06f9965c038bb3ddf18e3'

@functools.lru_cache(None)
def native(directory):
    return [a.read(p) for p in sorted((directory/'native-calls').glob('*-result.json'))]

def programs(trace):
    output=[]
    for node in trace.get('nodes',[]):
        for call in node.get('message',{}).get('tool_calls') or []:
            if call.get('name')!='ipython':continue
            args=call['arguments'];args=a.core.json.loads(args) if isinstance(args,str) else args
            code=args['code'];values={};tree=None
            try:
                tree=ast.parse(code)
                for n in tree.body:
                    if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Constant):
                        if n.targets[0].id in ('request_text','ordinal','marker'):values[n.targets[0].id]=n.value.value
            except SyntaxError:pass
            output.append({'code_sha256':a.digest(code),'characters':len(code),
                'AST_sha256':a.digest(ast.dump(tree)) if tree else None,'literal_slots':values})
    return output

def load_episode(row):
    p=Path(row['episode_path']);assert a.sha(p)==row['episode_file_sha256']
    item=a.read(p);assert a.digest(item['episode'])==item['episode_sha256']
    trace=item['episode']['traces'][0];session=[n for n in native(p.parents[1]) if n.get('session_id')==trace['id']]
    session.sort(key=lambda n:n['index'])
    assert len(session)==len(row['native_actions'])
    for n,saved in zip(session,row['native_actions'],strict=True):
        assert n['status']==saved['status']
        assert a.digest(n.get('response',{}).get('tokens',{}).get('prompt_ids'))==saved['prompt_sha256']
        assert a.digest(n.get('response',{}).get('tokens',{}).get('completion_ids'))==saved['action_sha256']
    return item,trace,session

def action(n):
    if n is None:return None
    p=n.get('response') or {};t=p.get('tokens') or {};ids=t.get('completion_ids') or []
    message=p.get('message') or {}
    return {'index':n['index'],'status':n['status'],'prompt_tokens':len(t.get('prompt_ids') or []),
        'completion_tokens':len(ids),'completion_tail_token_ids':ids[-8:],'finish_reason':p.get('finish_reason'),
        'native_content_characters':len(message.get('content') or ''),
        'native_reasoning_characters':len(message.get('reasoning_content') or ''),
        'parsed_tool_count':len(message.get('tool_calls') or []),
        'prompt_sha256':a.digest(t.get('prompt_ids')),'action_sha256':a.digest(ids)}

def run():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    source=a.ROOT/'readout-002.json';assert a.sha(source)==SOURCE_SHA
    r=a.read(source);assert r['status']=='COMPLETE_PAIRED_AUDIT'
    s=a.bindings().study;summaries={};changed=[]
    for phase,x in r['phases'].items():
        pairs=x['comparisons']['cp32']['pairs'];summary=Counter()
        for pair in pairs:
            ident=pair['coordinate']['id'];left=x['arms']['cp32']['rows'][ident];right=x['arms']['updated']['rows'][ident]
            old,ot,on=load_episode(left);new,nt,nn=load_episode(right)
            def same(z,w,key):
                return z.get('response',{}).get('tokens',{}).get(key)==w.get('response',{}).get('tokens',{}).get(key)
            allsame=len(on)==len(nn) and all(b['status']==c['status'] and same(b,c,'prompt_ids') and same(b,c,'completion_ids') for b,c in zip(on,nn))
            assert allsame==pair['native_token_paths_equal_descriptive_only']
            summary['pairs']+=1;summary['all_native_paths_identical']+=allsame
            summary['first_prompt_identical']+=bool(on and nn and same(on[0],nn[0],'prompt_ids'))
            summary['first_action_identical']+=bool(on and nn and same(on[0],nn[0],'completion_ids'))
            summary['programs_identical']+=pair['programs_equal'];summary['observations_identical']+=pair['observations_equal']
            if allsame:continue
            gold=old['derived']['answer'];assert gold==new['derived']['answer']
            ofinal=ot['root_reply'];nfinal=nt['root_reply'];assert a.digest(ofinal)==left['final_sha256'] and a.digest(nfinal)==right['final_sha256']
            obs=[]
            for trace in (ot,nt):
                values=[n['message']['content'] for n in trace['nodes'] if n.get('message',{}).get('role')=='tool']
                obs.append({'count':len(values),'characters':sum(len(v) for v in values),
                    'hashes':[a.digest(v) for v in values],'gold_exact_or_plus_print_newline':any(v in (gold,gold+'\n') for v in values)})
            turns=[]
            for i in range(max(len(on),len(nn))):
                b=on[i] if i<len(on) else None;c=nn[i] if i<len(nn) else None
                turns.append({'position':i,'old':action(b),'new':action(c),
                    'prompt_arrays_identical':bool(b and c and same(b,c,'prompt_ids')),
                    'action_arrays_identical':bool(b and c and same(b,c,'completion_ids'))})
            edits=[]
            for tag,i,j,k,l in SequenceMatcher(None,ofinal,nfinal,autojunk=False).get_opcodes():
                if tag!='equal':edits.append({'operation':tag,'old_bounds':[i,j],'new_bounds':[k,l],
                    'old_codepoints':[ord(z) for z in ofinal[i:j]] if j-i<=16 else None,
                    'new_codepoints':[ord(z) for z in nfinal[k:l]] if l-k<=16 else None})
            changed.append({'phase':phase,'coordinate':pair['coordinate'],'win':pair['win'],'loss':pair['loss'],
                'old_exact':left['raw_exact'],'new_exact':right['raw_exact'],
                'old_official_score':left['official_score'],'new_official_score':right['official_score'],
                'old_copy_type':left['copy_type'],'new_copy_type':right['copy_type'],
                'old_final_characters':len(ofinal),'new_final_characters':len(nfinal),'gold_characters':len(gold),
                'old_missing_only_final_two_spaces':ofinal+'  '==gold,
                'new_missing_only_final_two_spaces':nfinal+'  '==gold,
                'old_stop':ot['stop_condition'],'new_stop':nt['stop_condition'],
                'programs_identical':pair['programs_equal'],'observations_identical':pair['observations_equal'],
                'old_programs':programs(ot),'new_programs':programs(nt),'observations':obs,'turns':turns,
                'final_edits':edits,'old_episode_path':left['episode_path'],'new_episode_path':right['episode_path']})
        summaries[phase]=dict(summary)
    result={'schema':'fresh8-rloo-all-changed-native-paths-v1','source_readout_sha256':SOURCE_SHA,
        'paired_path_inventory':summaries,'changed_paths':changed,'changed_total':len(changed),
        'source_sha256':dict(a.PINS),'GPU_calls':0,'generated_programs_executed':False,
        'limitation':'All arrays compared inertly against the qualified cp32 controls; changed weights mean these are not clamp-only causal or replication claims. One exposed secondary exact gain is unreplicated.'}
    a.write(a.ROOT/'CHANGED_PATHS.json',result)
    print({'changed_total':len(changed),'inventory':summaries})

if __name__=='__main__':run()
