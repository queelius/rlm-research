"""Bind V2 process ownership checks to this sidecar's actual base-service wrapper."""

import ast

import study as s

RUNTIME = s.SIDE / "runtime-an27-5780-v1"
SOURCE = s.SIDE / "root-rlvr-campaign-v1/campaign_lifecycle_v2.py"
SOURCE_SHA256 = "568927528f46a203669a6b7671facc9e7419191850d3f050a58de066e5c6c0d5"
SERVICE = s.ROOT / "service_wrapper_v2.py"


def claim_source():
    if s.sha(SOURCE) != SOURCE_SHA256:
        raise ValueError("pinned lifecycle source changed")
    node = next(n for n in ast.parse(SOURCE.read_text()).body
                if isinstance(n, ast.FunctionDef) and n.name == "claim_service")
    text = ast.get_source_segment(SOURCE.read_text(), node)
    before = 'c.ROLE / "source/serve.py"'
    if text.count(before) != 2:
        raise ValueError("ownership identity seam changed")
    return text.replace(before, "ALLOCATION_SERVICE")


def install(suite):
    manifest = s.read(RUNTIME / "LIFECYCLE_READY_V2.json")
    for path, expected in manifest["source_sha256"].items():
        if s.sha(path) != expected:
            raise ValueError("allocation lifecycle source changed: " + path)
    suite.SERVE = SERVICE
    suite.life.__dict__["ALLOCATION_SERVICE"] = SERVICE
    exec(compile(claim_source(), str(SOURCE) + ":free-id-actual-wrapper", "exec"),
         suite.life.__dict__)

