"""One genuine acquisition and exact parameterized observed-state reduction."""
import functools
import qs_study as s
old=s.load('qs_qualified_od_protocol',s.OLD/'od_protocol.py',s.cf_ready['source_sha256'][str(s.OLD/'od_protocol.py')],{'od_study':s})
with s.aliases({'od_study':s}):old.shared()
row,scalar,layout,visible_maps,target_spans,physical_cost=old.row,old.scalar,old.layout,old.visible_maps,old.target_spans,old.physical_cost
def producer(coordinate,index):
    if coordinate['width']!=16 or index!=0:raise ValueError('one complete16 native acquisition')
    return old.producer(coordinate,index)
def reduction(coordinate):
    n=coordinate['names'];records=n['records'];labels=n['labels'];selected=n['selected'];result=n['result'];a=coordinate['target'];users=coordinate['users'];op=coordinate['operator']
    code=f'{selected} = [record for record in {records} if record["user"] in {users!r} and {labels}[record["id"]] == {a!r}]\n'
    if op in ('count','distinct_users','weight_sum'):
        value={'count':f'len({selected})','distinct_users':f'len({{record["user"] for record in {selected}}})','weight_sum':f'sum(record["weight"] for record in {selected})'}[op]
    elif op in ('threshold_users','maximum_weight'):
        code+=f'per_user_totals = {{user: 0 for user in {users!r}}}\nfor record in {selected}:\n    per_user_totals[record["user"]] += record["weight"]\n'
        value=f'sum(value > {coordinate["threshold"]} for value in per_user_totals.values())' if op=='threshold_users' else 'max(per_user_totals.values(), default=0)'
    elif op=='conditional_weight':
        code+=f'qualifying_users = {{record["user"] for record in {selected}}}\n'
        value=f'sum(record["weight"] for record in {records} if record["user"] in qualifying_users and {labels}[record["id"]] == {coordinate["target_b"]!r})'
    else:raise ValueError('approved operator')
    return code+f'{result} = {value}\nprint({result})'
def correction(pieces,coordinate,target):
    if coordinate['target']!=target:raise ValueError('category drift')
    return reduction(coordinate),{'payload_lines':[]}
