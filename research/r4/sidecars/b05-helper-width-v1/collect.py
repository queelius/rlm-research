"""Four workers across nine cases; every case executes all fourteen helper calls."""
import study
with study.aliases({'runner_study':study},study.SOURCE):
    inherited=study.load('width_native_collector',study.SOURCE/'runner_collect.py')

class Collector(inherited.Collector):
    def root(self,root):
        plan=[c for c in study.calls() if c['root_id']==root['root_id']]
        assert len(plan)==14
        for call in plan:
            self.call(call,study.prompt(call),child=study.child(call))
        receipt=dict(root_id=root['root_id'],planned_call_ids=[study.call_id(c) for c in plan],
                     planned_physical=14,root_model_calls=0,all_conditions_outcome_independent=True)
        study.write_x(self.output/'roots'/f"{root['root_id']}.json",receipt)
        return receipt

inherited.Collector=Collector
execute=inherited.execute
