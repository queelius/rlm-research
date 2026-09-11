"""MAIN review gate; creates READY but never launches GPU or service."""
import lr_study as study


def seal():
    campaign = study.read(study.ROOT / "CAMPAIGN.json")
    review_path = study.ROOT / "MAIN_REVIEW.json"
    review = study.read(review_path)
    if review.get("approved") is not True or review.get("campaign_identity") != campaign["identity"]:
        raise ValueError("exact MAIN approval required")
    if study.verify_campaign() != campaign:
        raise ValueError("campaign changed after review")
    value = {
        "schema": "root-question-sensitive-terminal-rlvr-lr1e5-ready-v1",
        "campaign_id": campaign["campaign_id"], "campaign_identity": campaign["identity"],
        "campaign_sha256": study.sha(study.ROOT / "CAMPAIGN.json"),
        "main_review_sha256": study.sha(review_path),
        "entry": str(study.ROOT / "lr_owner.py"), "attempt": str(study.ATTEMPT),
        "source_sha256": campaign["source_sha256"], "input_sha256": campaign["input_sha256"],
        "gpu_launched_during_preparation": False,
    }
    value["identity"] = study.digest(value)
    study.write(study.ROOT / "READY.json", value)
    return value


if __name__ == "__main__":
    print(seal()["identity"])
