"""Unchanged supplied-target metric; explicit adaptive few-shot condition."""
import study
with study.aliases({"study":study,"science":study.science},study.PARENT):
    inherited=study.load("finqa_fewshot_original_metrics",study.PARENT/"metrics.py")


def summarize(output,runtime_qualified):
    result=inherited.summarize(output,runtime_qualified)
    result["schema"]="finqa-two-synthetic-example-calibration-result-v1"
    result["condition"]="two synthetic demonstrations, requested representation per arm"
    result["cached_zero_shot_result_sha256"]=study.BASE_RESULT_SHA
    result["adaptive_exposed_panel_interface_calibration"]=True
    result["same_eval_examples_seeds_budget_interpreter"]=True
    return result
