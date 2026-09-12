"""Reuse and authenticate the four endpoints fixed before DBpedia evaluation."""

import importlib.util
import sys

import study


SOURCE_STUDY = study.OFFICIAL_SOURCE / "study.py"
SOURCE_ELIGIBILITY = study.OFFICIAL_SOURCE / "eligibility.py"
SOURCE_STUDY_SHA256 = "5222a743b5007f7389034f7b25adc148fe60df42f7825f21d0064815651b1041"
SOURCE_ELIGIBILITY_SHA256 = "74a275b01d16b7f49fd4fda9c20e32b74902b38c833dfc25432b8d05ee8ddcef"
if study.sha(SOURCE_STUDY) != SOURCE_STUDY_SHA256 or study.sha(SOURCE_ELIGIBILITY) != SOURCE_ELIGIBILITY_SHA256:
    raise ValueError("official four-endpoint source changed")


def _load_source():
    spec = importlib.util.spec_from_file_location("dbpedia_official_endpoint_study", SOURCE_STUDY)
    source_study = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source_study)
    previous = sys.modules.get("study")
    sys.modules["study"] = source_study
    try:
        spec = importlib.util.spec_from_file_location(
            "dbpedia_official_endpoint_eligibility", SOURCE_ELIGIBILITY
        )
        source = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(source)
    finally:
        sys.modules["study"] = previous if previous is not None else study
    return source


SOURCE = _load_source()


def qualify(arm):
    if arm not in study.ARMS:
        raise ValueError("unknown endpoint arm")
    return SOURCE.qualify(arm)


def fixed_endpoints(arm):
    path = study.ROOT / "ENDPOINTS_FIXED.json"
    receipt = study.read(path)
    if (
        receipt.get("authority") != "MAIN"
        or receipt.get("new_dbpedia_model_calls_before_fix") != 0
        or receipt.get("evaluation_data_ready_sha256") != study.sha(study.EVAL_DATA / "DATA_READY.json")
        or set(receipt.get("trained_endpoints", {})) != set(study.ARMS)
    ):
        raise ValueError("four endpoints were not fixed before DBpedia queries")
    current = qualify(arm)
    expected = receipt["trained_endpoints"][arm]
    for key in ("checkpoint", "state_sha256", "binding_sha256"):
        if current.get(key) != expected.get(key):
            raise ValueError("fixed endpoint changed: " + arm + ":" + key)
    if arm != "c32" and current.get("step_commit_sha256") != expected.get("step_commit_sha256"):
        raise ValueError("fixed step commit changed: " + arm)
    return {
        "fixed_receipt_path": str(path),
        "fixed_receipt_sha256": study.sha(path),
        "selected_endpoints": receipt["trained_endpoints"],
        "arm_eligibility": current,
        "evaluation_inputs": {
            "path": str(study.EVAL_DATA / "DATA_READY.json"),
            "sha256": study.sha(study.EVAL_DATA / "DATA_READY.json"),
        },
        "checkpoint_training_inputs_separate_from_evaluation_inputs": True,
    }

