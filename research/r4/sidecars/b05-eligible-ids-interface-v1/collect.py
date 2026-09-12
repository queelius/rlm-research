"""Same native child call path, with only the new IDs output contract."""
import interface
import study

with study.aliases({"runner_study": study}, study.SOURCE):
    inherited = study.load("ids_only_native_collector", study.SOURCE / "runner_collect.py")


class Collector(inherited.Collector):
    def root(self, root):
        for call in study.calls():
            if call["root_id"] == root["root_id"]:
                index = call["child_index"]
                self.call(call, interface.render(root["child_prompts"][index]), child=root["safe_children"][index])
        return {"root_id": root["root_id"], "planned_child_calls": 6, "root_model_calls": 0}


inherited.Collector = Collector
execute = inherited.execute
