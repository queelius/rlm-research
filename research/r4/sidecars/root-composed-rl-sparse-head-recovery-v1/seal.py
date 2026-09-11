"""Write READY only after the current campaign and CPU receipts exist."""
import json

import sparse_study as study


def seal():
    campaign = study.read(study.ROOT / "CAMPAIGN.json")
    if study.digest({key: value for key, value in campaign.items() if key != "identity"}) != campaign["identity"]:
        raise ValueError("campaign identity")
    for path, pin in {**campaign["source_sha256"], **campaign["input_sha256"]}.items():
        study.check(path, pin)
    receipt = study.read(study.ROOT / "CPU_TEST_RECEIPT.json")
    if receipt["returncode"] != 0 or receipt["tests_passed"] != 7 or not receipt["trainer_preflight_passed"]:
        raise ValueError("CPU qualification incomplete")
    value = {"schema": "root-composed-rl-sparse-head-ready-v1",
        "identity": campaign["identity"], "campaign_sha256": study.sha(study.ROOT / "CAMPAIGN.json"),
        "cpu_test_receipt_sha256": study.sha(study.ROOT / "CPU_TEST_RECEIPT.json"),
        "gpu_executed": False, "main_only_launch": True}
    path = study.ROOT / "READY.json"
    if path.exists() and json.loads(path.read_text()) != value:
        raise ValueError("READY differs")
    if not path.exists():
        study.write(path, value)
    return value


if __name__ == "__main__":
    print(seal()["identity"])
