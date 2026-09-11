"""Qualified checkpoint math; window1..12 is distinct from Adam0..12."""
import functools
import qsr_study as s
c=s.load('qsr_qualified_common',s.CAMPAIGN/'campaign_common.py',s.PINS[s.CAMPAIGN/'campaign_common.py'])
_authenticate=c.authenticate_policy;c.ROOT=s.ROOT;c.SEED=s.SEED;c.verify_campaign=s.verify_prepared
c.pilot_math=functools.lru_cache(maxsize=1)(c.pilot_math)
def starting_decision():
    value=s.read(s.ROOT/'START.json');policy=s.fixed_start()
    if value['policy']!=policy:raise ValueError('fixed low66c starting decision changed')
    return s.ROOT/'START.json',value,policy
def authenticate_policy(policy):
    if policy['step']==0:
        if policy!=starting_decision()[2]:raise ValueError('not low66c / fresh RL Adam0')
    else:_authenticate(policy)
def check_generation(generation,policy,optimizer_step):
    if s.digest({k:v for k,v in generation.items() if k!='generation_id'})!=generation['generation_id']:raise ValueError('generation identity changed')
    if generation['fixed_child_sha256']!=s.CHILD_SHA or generation['previous_policy']!=policy:raise ValueError('stale root/child generation')
    if type(generation['round'])!=int or not 1<=generation['round']<=12:raise ValueError('actual Adam generation outside1..12')
    if generation['round']!=policy['step']+1 or optimizer_step!=policy['step']:raise ValueError('actual Adam cursor mismatch')
    if not generation['round']<=generation['candidate_window']<=12:raise ValueError('window/Adam cursor mismatch')
    return generation['round']
c.authenticate_policy=authenticate_policy;c.original_policy=lambda:starting_decision()[2];c.check_generation=check_generation
def generation(window,policy):
    g=c.generation_identity(s.verify_prepared()['campaign_id'],policy['step']+1,policy,s.digest(s.candidate_plan(window)))
    g['candidate_window']=window;g['generation_id']=s.digest({k:v for k,v in g.items() if k!='generation_id'});check_generation(g,policy,policy['step']);return g
def transition(completed,policy,window,new_policy):
    if window!=completed+1 or not 1<=window<=12:raise ValueError('noncontiguous scheduled window')
    if new_policy is not None and (new_policy['step']!=policy['step']+1 or new_policy['adapter_sha256']==policy['adapter_sha256']):raise ValueError('actual update must advance Adam and weights once')
    chosen=policy if new_policy is None else new_policy
    return dict(completed_windows=window,optimizer_steps=chosen['step'],next_window=window+1,policy=chosen,decision='noop' if new_policy is None else 'update')
