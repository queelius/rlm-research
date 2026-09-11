"""Private unchanged checkpoint math; fixed SFT8 becomes fresh RL generation0."""
import functools
import study as s
c=s.load('refill_common',s.CAMPAIGN/'campaign_common.py',s.PINS[s.CAMPAIGN/'campaign_common.py'])
original_authenticate=c.authenticate_policy
c.ROOT,c.SEED=s.ROOT,s.SEED;c.verify_campaign=s.verify_prepared
c.pilot_math=functools.lru_cache(maxsize=1)(c.pilot_math)
def starting_decision():
    value=s.read(s.ROOT/'START.json');policy=s.fixed_start()
    if value['policy']!=policy or value['approval_sha256']!=s.sha(value['approval_path']):raise ValueError('fixed MAIN choice changed')
    return s.ROOT/'START.json',value,policy
def authenticate_policy(policy):
    if policy['step']==0:
        if policy!=starting_decision()[2]:raise ValueError('not fixed SFT8/fresh Adam0')
    else:original_authenticate(policy)
c.original_policy=lambda:starting_decision()[2]
c.authenticate_policy=authenticate_policy
def generation(window,policy):
    value=c.generation_identity(s.verify_prepared()['campaign_id'],policy['step']+1,policy,s.digest(s.candidate_plan(window)))
    value['candidate_window']=window;value['generation_id']=c.digest({k:v for k,v in value.items() if k!='generation_id'})
    return value
