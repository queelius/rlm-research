"""Original numeric metric/all16 accounting; no annotation or syntax repair."""
import study
with study.aliases({"study":study,"science":study.science},study.PARENT):
    inherited=study.load("finqa_fresh_original_metrics",study.PARENT/"metrics.py")


def summarize(output,runtime_qualified):
    result=inherited.summarize(output,runtime_qualified)
    result["schema"]="finqa-two-example-fresh16-replication-result-v1"
    result["prior_panel_result_sha256"]=study.PRIOR_RESULT_SHA
    result["panels_have_different_pages_and_seed_namespace"]=True
    result["two_example_prompt_builder_and_interpreter_unchanged"]=True
    result["not_weight_learning_or_new_method"]=True
    return result
