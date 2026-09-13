"""Reuse the qualified32 plain-call collector; only frozen prompts change."""
import study
with study.aliases({"study":study},study.PARENT):
    inherited=study.load("finqa_fewshot_plain_collector",study.PARENT/"collect.py")
Collector=inherited.Collector
execute=inherited.execute
