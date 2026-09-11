"""Add fixed-confuser and actual executed-denominator diagnostics; never selects data."""
from collections import Counter
import qs_study as s
def main():
    rows=s.read(s.ROOT/'inputs/ALL_SPECS.json');public={c['id']:c for c in s.read(s.ROOT/'inputs/PUBLIC.json')};host=s.read(s.ROOT/'inputs/HOST_GOLD.json');first={r['slot']:r for r in s.problem.specs('train',0)}
    diagnostics=[]
    for row in rows:
        records=public[row['context_id']]['records'];labels=host[row['context_id']]['labels'];scoped=[r for r in records if r['user'] in row['users']];a=[r for r in scoped if labels[r['id']]==row['target']]
        values={'zero':0,'scoped_A_record_count':len(a),'scoped_A_distinct_users':len({r['user'] for r in a}),'scoped_A_pooled_weight':sum(r['weight'] for r in a),'scoped_A_max_weight':max([0,*[sum(r['weight'] for r in a if r['user']==u) for u in row['users']]]),'requested_operator_all_user_scope':s.answer(records,labels,{**row,'users':['u0','u1','u2','u3']}),'first_train_slot_literal_parameters':s.answer(records,labels,{**row,**first[row['slot']]})}
        if row['operator']=='threshold_users':values['threshold_on_pooled_A']=int(sum(r['weight'] for r in a)>row['threshold'])
        if row['operator']=='conditional_weight':
            values['scoped_B_pooled_weight']=sum(r['weight'] for r in scoped if labels[r['id']]==row['target_b'])
            values['conditional_reversed_AB']=s.answer(records,labels,{**row,'target':row['target_b'],'target_b':row['target']})
        gold=host[row['context_id']]['answers'][row['slot']]
        diagnostics.append(dict(coordinate_id=row['id'],split=row['split'],slot=row['slot'],gold=gold,confusers=values,coincident_confusers=[k for k,v in values.items() if v==gold]))
    baselines={}
    for name,plan in [('train','TRAIN_PLAN.json'),('development_executed','DEV_PLAN.json'),('protected','FREE_PLAN.json')]:
        selected=s.read(s.ROOT/'inputs'/plan);counts=Counter(host[r['context_id']]['answers'][r['slot']] for r in selected)
        baselines[name]=dict(planned_per_policy=len(selected),histogram={str(k):v for k,v in sorted(counts.items())},zero=counts[0],best_constant=max(counts.values()))
    s.write(s.ROOT/'inputs/ANTI_COINCIDENCE.json',dict(rows=diagnostics,selection_uses_these_values=False,confusers_fixed_before_model_outputs=True))
    s.write(s.ROOT/'inputs/EXECUTED_BASELINES.json',dict(cohorts=baselines,original_BASELINES_dev_scope='all36 defined dev specs, not actual8 executed dev slots',input_bytes_unchanged=True))
    print({k:(v['planned_per_policy'],v['zero']) for k,v in baselines.items()})
if __name__=='__main__':main()
