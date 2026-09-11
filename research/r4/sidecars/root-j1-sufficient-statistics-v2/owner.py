import importlib.util,sys
import collect
import study as s
old={"collect":sys.modules.get("collect"),"study":sys.modules.get("study")};sys.modules.update({"collect":collect,"study":s})
try:spec=importlib.util.spec_from_file_location("ss_v2_owner_base",s.V1/"owner.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
finally:
 for n,v in old.items():
  if v is None:sys.modules.pop(n,None)
  else:sys.modules[n]=v
collector_argv=m.collector_argv;execute=m.execute;main=m.main
if __name__=="__main__":main()
