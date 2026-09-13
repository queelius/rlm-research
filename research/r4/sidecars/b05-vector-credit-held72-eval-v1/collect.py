"""Reviewed raw collector with exact per-call model dispatch."""
import study
path=study.SOURCE/"runner_collect.py";text=path.read_text();old='body = study.request_body(prompt, call["seed"], call["max_tokens"])';assert text.count(old)==1
text=text.replace(old,'body = study.request_for(call)')
import types
inherited=types.ModuleType("vector_credit_held_native_collector");inherited.__file__=str(path)
with study.aliases({"runner_study":study},study.ROOT):exec(compile(text,str(path),"exec"),inherited.__dict__)
class Collector(inherited.Collector):
    def root(self,root):
        plan=[c for c in study.calls() if c["root_id"]==root["root_id"]]
        for call in plan:self.call(call,study.prompt(call))
        value={"root_id":root["root_id"],"planned_call_ids":[study.call_id(c) for c in plan],"all6_accounted":len(plan)==6}
        study.write_x(self.output/"roots"/f"{root['root_id']}.json",value);return value
inherited.Collector=Collector;execute=inherited.execute
