"""Host trusted invocation decision, matching the actual transformed child prompt."""
import bridge
encoded=bridge.encoded

class Decisions:
    def __init__(self):self.values={}
    def choose(self,coordinate,arm,meta,messages,catalog):
        key=(coordinate,meta['invocation'])
        if key in self.values:return self.values[key]
        result={'matched':False,'apply':False,'reason':'root_or_unmatched_child','coordinate_id':coordinate,'arm':arm,
                'invocation':meta['invocation'],'depth':meta['depth'],'decision_before_first_dispatch':True}
        if meta['depth']==1 and meta['kind']=='ordinary':
            users=[m.get('content') for m in messages if m.get('role')=='user']
            if len(users)==1 and isinstance(users[0],str) and users[0].count('\nRecords: ')==1:
                try:
                    rows=bridge.json.loads(users[0].split('\nRecords: ')[1]);public={r['id']:r for r in catalog['records']}
                    selected=[public[r['id']] for r in rows];ids=[r['id'] for r in selected]
                    if ids and len(ids)==len(set(ids)) and bridge.child_prompt(selected,arm)==users[0]:
                        schema=bridge.schema(ids,arm);ordered=encoded(schema)
                        result.update(matched=True,apply=True,reason='exact_transformed_public_contract',requested_ids=ids,
                            selected_records=selected,request_text=users[0],original_request=bridge.batch.request_for(selected),
                            schema=schema,schema_ordered_json=ordered,schema_ordered_sha256=bridge.hashlib.sha256(ordered.encode()).hexdigest())
                except (ValueError,KeyError,TypeError):pass
        self.values[key]=result;return result
