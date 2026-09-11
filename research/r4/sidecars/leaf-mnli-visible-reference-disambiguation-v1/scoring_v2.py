"""Strict displayed-semantic primary and wrong-visible named-record diagnostics."""
import protocol_v2 as p
import study as s

path=s.QUALIFIED/'scoring.py';pin='202505b014734c3d403ca179b5f13d235649d9330f792bb6414f730d6813bb62'
base=s.load('visible_reference_disambiguation_base_score',path,pin,{'study':s,'protocol':p})
verified_response=base.verified_response
def missing(context):
    value=base.missing(context);value.update(named_correct_disagree=None,named_disagree_items=None,third_correct_disagree=None);return value
def score(message,context,arm):
    value=base.score(message,context,arm);value.update(named_correct_disagree=None,named_disagree_items=None,third_correct_disagree=None)
    if value['contract_valid'] and arm.startswith('wrong_'):
        labels=value['predictions'];tags=p.requested_tags(context);by_id={r['id']:r['gold_label'] for r in context['records']};pairs=[]
        for predicted,tag,record in zip(labels,tags,context['records'],strict=True):
            named=by_id[tag];displayed=record['gold_label']
            if named!=displayed:pairs.append((predicted,named,displayed))
        value.update(named_disagree_items=len(pairs),named_correct_disagree=sum(predicted==named for predicted,named,_ in pairs),
            third_correct_disagree=sum(predicted not in (named,displayed) for predicted,named,displayed in pairs))
    return value
