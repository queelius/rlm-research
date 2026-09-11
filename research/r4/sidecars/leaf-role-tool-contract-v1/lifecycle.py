"""Bind the qualified an27 ownership lifecycle to the proven released-base wrapper."""

import ast

import study as s

SOURCE = s.SIDE / "root-rlvr-campaign-v1/campaign_lifecycle_v2.py"
SOURCE_SHA256 = "568927528f46a203669a6b7671facc9e7419191850d3f050a58de066e5c6c0d5"
RUNTIME = s.SIDE / "runtime-an27-5780-v1"
SERVICE = s.SIDE / "leaf-free-id-correspondence-v1/service_wrapper_v3.py"
SERVICE_SHA256 = "4347c92894a24e357a74f8b9e372edcc4b3327532de183d9a59873331dc5a9d0"


def claim_source():
    if s.sha(SOURCE) != SOURCE_SHA256 or s.sha(SERVICE) != SERVICE_SHA256:
        raise ValueError("qualified lifecycle/service source changed")
    source = SOURCE.read_text()
    node = next(node for node in ast.parse(source).body
                if isinstance(node, ast.FunctionDef) and node.name == "claim_service")
    text = ast.get_source_segment(source, node)
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
    exec(compile(claim_source(), str(SOURCE) + ":role-tool-wrapper", "exec"), suite.life.__dict__)

