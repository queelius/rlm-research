"""Supervisor-owned source-bound accumulation; no task target or gold inputs."""
import copy
import hashlib
import json
from pathlib import Path

LABELS=('human being','location','abbreviation','entity','description and abstract concept','numeric value')

class Ledger:
    def __init__(self,root_id,config,request_for,strict_map,audit_path=None):
        self.root_id=root_id;self.coordinate=config['coordinate'];self.arm=config['arm']
        if self.arm not in ('map','ledger'):raise ValueError('unknown ledger arm')
        self.context_id=config['context_id'];self.records=copy.deepcopy(config['records'])
        self.public={r['id']:{'id':r['id'],'text':r['text']} for r in self.records}
        if len(self.public)!=len(self.records):raise ValueError('duplicate public source ID')
        self.request_for=request_for;self.strict_map=strict_map;self.pending={};self.values={};self.events=[]
        self.audit_path=Path(audit_path) if audit_path else None
        self.emit({'event':'initialized','public_ids':list(self.public)})

    def emit(self,event):
        event={'coordinate':self.coordinate,'context_id':self.context_id,'root_invocation':self.root_id,**event}
        self.events.append(event)
        if self.audit_path:
            with self.audit_path.open('a') as stream:stream.write(json.dumps(event,ensure_ascii=False,separators=(',',':'))+'\n')
        return event

    def stage(self,key,parent_id,child_id,prompt,answer,depth):
        event={'event':'child_result','parent_invocation':parent_id,'child_invocation':child_id,
               'depth':depth,'request':prompt,'raw_answer':answer,'eligible':False,'reason':'not_source_bound'}
        if parent_id!=self.root_id or depth!=1:event['reason']='not_direct_child_of_this_root'
        else:
            try:
                if not isinstance(prompt,str) or prompt.count('\nRecords: ')!=1:raise ValueError('request boundary')
                rows=json.loads(prompt.split('\nRecords: ')[1]);ids=[r['id'] for r in rows]
                selected=[self.public[i] for i in ids]
                if len(ids)!=len(set(ids)) or self.request_for(selected)!=prompt:raise ValueError('exact source request mismatch')
                event['requested_ids']=ids
                labels=self.strict_map(answer,ids)
                event.update(eligible=True,reason='strict_source_bound_map',labels=labels)
            except (ValueError,KeyError,TypeError) as error:event['detail']=str(error)
        self.pending[key]=self.emit(event)

    def deliver(self,key):
        event=self.pending.pop(key,None)
        if event is None:return False
        if event['eligible']:
            for identifier,label in event['labels'].items():self.values.setdefault(identifier,set()).add(label)
        self.emit({'event':'delivered','child_invocation':event['child_invocation'],
                   'eligible':event['eligible'],'summary':self.summary()})
        return True

    def summary(self):
        counts={label:0 for label in LABELS};conflicts=0
        for labels in self.values.values():
            if len(labels)==1:counts[next(iter(labels))]+=1
            else:conflicts+=1
        seen=len(self.values);resolved=seen-conflicts
        return {'counts':counts,'unique_seen':seen,'resolved':resolved,'source_records':len(self.public),
                'unqueried':len(self.public)-seen,'conflicts':conflicts,'partial':resolved!=len(self.public)}

    def observe(self,invocation,original_truncated,raw_original=None):
        if invocation!=self.root_id:return original_truncated
        summary=self.summary();suffix=''
        if self.arm=='ledger' and any(e['event']=='delivered' and e['eligible'] for e in self.events):
            suffix='\n\n[Harness accumulation ledger: counts of returned child labels, not verified truth; unresolved/partial coverage is explicit.]\n'+json.dumps(summary,separators=(',',':'))
            if len(suffix)>2048:raise ValueError('bounded ledger suffix exceeded')
        content=original_truncated+suffix
        self.emit({'event':'root_observation','raw_original':raw_original,'original_truncated':original_truncated,
                   'appended_summary':bool(suffix),'summary':summary,'actual_content':content,
                   'actual_content_sha256':hashlib.sha256(content.encode()).hexdigest()})
        return content
