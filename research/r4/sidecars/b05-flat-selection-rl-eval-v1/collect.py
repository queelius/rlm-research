"""Reviewed raw-wire collector, only frozen per-call model/request dispatch changes."""
import types
import study

path=study.SOURCE/'runner_collect.py';text=path.read_text()
old='body = study.request_body(prompt, call["seed"], call["max_tokens"])'
assert text.count(old)==1
text=text.replace(old,'body = study.request_for(call)')
inherited=types.ModuleType('ba18_eval_reviewed_native_collector');inherited.__file__=str(path)
with study.aliases({'runner_study':study},study.ROOT):exec(compile(text,str(path), 'exec'),inherited.__dict__)

class Collector(inherited.Collector):
    def root(self,root):
        plan=[c for c in study.calls() if c['root_id']==root['root_id']]
        for c in plan:self.call(c,study.prompt(c),child=study.child(c))
        value=dict(root_id=root['root_id'],split=root['split'],planned_call_ids=[study.call_id(c) for c in plan],all4_accounted=len(plan)==4)
        study.write_x(self.output/'roots'/f"{root['root_id']}.json",value);return value

inherited.Collector=Collector
execute=inherited.execute
