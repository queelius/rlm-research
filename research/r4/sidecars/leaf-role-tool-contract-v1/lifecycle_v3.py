"""Bind qualified ownership lifecycle to service wrapper V5."""

import ast

import study as s

SOURCE = s.SIDE / "root-rlvr-campaign-v1/campaign_lifecycle_v2.py"
SOURCE_SHA256 = "568927528f46a203669a6b7671facc9e7419191850d3f050a58de066e5c6c0d5"
RUNTIME = s.SIDE / "runtime-an27-5780-v1"
SERVICE = s.ROOT / "service_wrapper_v5.py"


def claim_source():
    if s.sha(SOURCE) != SOURCE_SHA256:
        raise ValueError("qualified lifecycle source changed")
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
    exec(compile(claim_source(), str(SOURCE) + ":leaf-role-wrapper-v5", "exec"),
         suite.life.__dict__)
