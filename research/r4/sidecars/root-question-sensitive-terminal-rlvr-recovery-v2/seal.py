"""MAIN review gate for READY; never launches a GPU or service."""
import terminal_study as study


def seal():
    campaign = study.read(study.ROOT / "CAMPAIGN.json")
    review_path = study.ROOT / "MAIN_REVIEW.json"
    review = study.read(review_path)
    if review.get("approved") is not True or review.get("campaign_identity") != campaign["identity"]:
        raise ValueError("exact MAIN approval of current campaign required")
    value = {
        "schema": "question-sensitive-terminal-rlvr-ready-v1",
        "campaign_id": campaign["campaign_id"],
        "campaign_identity": campaign["identity"],
        "campaign_sha256": study.sha(study.ROOT / "CAMPAIGN.json"),
        "main_review_sha256": study.sha(review_path),
        "source_sha256": campaign["source_sha256"],
        "input_sha256": campaign["input_sha256"],
        "attempt": str(study.ATTEMPT),
        "entry": str(study.ROOT / "terminal_owner.py"),
        "gpu_launched_during_preparation": False,
    }
    value["identity"] = study.digest(value)
    study.write(study.ROOT / "READY.json", value)
    return value


if __name__ == "__main__":
    print(seal()["identity"])
