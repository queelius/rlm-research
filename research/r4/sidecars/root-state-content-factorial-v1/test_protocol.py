import json
import protocol as p

def files():
    return {"state/history.json": json.dumps([
        {"role":"system","content":"SYSTEM_NOT_INLINE"},
        {"role":"user","content":"OLD_USER_NOT_INLINE"},
        {"role":"assistant","content":None,"tool_calls":[{"name":"ipython","arguments":"ACTION_MARKER","id":"old0"}]},
        {"role":"tool","content":"OBSERVATION_MARKER"},
    ]), "state/map-01.json":"OBSERVATION_MARKER", "state/metadata.json":"METADATA_MARKER"}

def test_visibility_factors_are_independent_and_never_mutate_files():
    f=files();before=dict(f)
    for arm in p.ARMS:
        value=p.prompt("CURRENT_GOAL",f,arm)
        assert ("ACTION_MARKER" in value)==(arm[1]=="1")
        assert ("OBSERVATION_MARKER" in value)==(arm[3]=="1")
        assert "METADATA_MARKER" in value and "state/history.json" in value
        assert "SYSTEM_NOT_INLINE" not in value and "OLD_USER_NOT_INLINE" not in value
    assert f==before

def test_paired_plan_preserves_every_state_and_balances_rotation():
    states=[{"source_id":f"s{i}","native_context_id":i//4,"width":4 if i%2 else 16} for i in range(16)]
    rows=p.plan(states);assert len(rows)==64 and len({r["id"] for r in rows})==64
    orders=[]
    for state in states:
        four=[r for r in rows if r["source_id"]==state["source_id"]]
        assert {r["representation"] for r in four}==set(p.ARMS)
        assert len({r["seed"] for r in four})==1
    for index in range(16):orders.append(tuple(r["representation"] for r in rows if r["pair_order"]==index))
    assert len(set(orders))==4 and all(orders.count(v)==4 for v in set(orders))

def test_missing_slot_keeps_null():
    row={"id":"unrun"};result=p.null_row(row,"preplanned")
    assert result["coordinate"]==row and result["reward"] is None and result["available"] is False
