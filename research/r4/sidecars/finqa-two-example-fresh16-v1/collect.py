"""Original qualified plain32 collector, fresh fixed plan only."""
import study
with study.aliases({"study":study},study.PARENT):
    inherited=study.load("finqa_fresh_original_collector",study.PARENT/"collect.py")
Collector=inherited.Collector
execute=inherited.execute
