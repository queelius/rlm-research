"""Authenticate additive V2 sources while retaining the sealed V1 campaign."""
import warm_study as study

_verify_v1 = study.verify_prepared


def verify():
    ready = study.read(study.ROOT / "V2_QUALIFICATION.json")
    if study.digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("V2 qualification identity changed")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        study.check(path, pin)
    campaign = _verify_v1()
    if ready["campaign_id"] != campaign["campaign_id"] or ready["attempt"] != str(study.ROOT / "outputs/attempt-002"):
        raise ValueError("V2 campaign/output binding changed")
    return campaign


def install():
    study.verify_prepared = verify
