"""Exact stable-panel three-arm protocol with a new 8B model binding."""
import study as s

q = s.load("qwen8b_stable_protocol_source", s.PRIOR / "protocol.py",
           "e5bff89950d15b164ad27cace14e38b2a69675010910a762b6a1d9d7715b1309",
           {"study": s})
LABELS, RELATIONS = q.LABELS, q.RELATIONS
ANCHORS = ("labels_only", "sequential_numeric", "opaque")
ARMS = tuple(f"{relation}_{anchor}" for relation in RELATIONS for anchor in ANCHORS)
SYSTEM, SEMANTIC = q.SYSTEM, q.SEMANTIC
contexts = q.contexts
requested_tags = q.requested_tags
context_manifest = q.context_manifest
anchor_values = q.anchor_values
visible_records = q.visible_records
schema = q.schema
null_row = q.null_row


def plan(): return s.read(s.ROOT / "PLAN.json")


def request(context, row, alien=None):
    value = q.request(context, row, alien)
    value["model"] = s.MODEL["alias"]
    value["cache_salt"] = s.ROOT.name
    return value
