"""All-planned denominators and paired base/local/joint held metrics."""
import study as s
with s.aliases({"study":s,"interface":s.interface},s.ROOT):prior=s.load("vector_credit_held_grader",s.ROLLOUT/"metrics.py")
grade=prior.grade;aggregate=prior.aggregate;costs=prior.costs
def summarize(output,qualified):
    records={p.stem:s.read(p) for p in (output/"calls").glob("*.json")};starts={p.stem:s.read(p) for p in (output/"starts").glob("*.json")};expected={s.call_id(c) for c in s.calls()}
    assert set(records)<=expected and set(starts)<=expected;start_only=set(starts)-set(records)
    for key in start_only:records[key]={**starts[key],"transport_valid":False,"usage":{},"status":"start_only_provider_unknown"}
    gold=s.gold();rows=[grade(c,records.get(s.call_id(c),{}),s.task(c)["public_order"],gold[c["root_id"]]) for c in s.calls()]
    arms={arm:{**aggregate([r for r in rows if r["arm"]==arm]),"cost":costs([records.get(r["call_id"],{}) for r in rows if r["arm"]==arm],24)} for arm in s.ARMS}
    pairs=[]
    for root in s.tasks():
      for repeat in range(2):
        trio={arm:next(r for r in rows if r["root_id"]==root["root_id"] and r["repeat"]==repeat and r["arm"]==arm) for arm in s.ARMS}
        assert len({r["seed"] for r in trio.values()})==1
        pairs.append({"root_id":root["root_id"],"repeat":repeat,"seed":trio["base"]["seed"],"all_available":all(r["available"] for r in trio.values()),
          **{f"{arm}_exact":trio[arm]["exact"] for arm in s.ARMS},**{f"{arm}_valid":trio[arm]["semantic_valid"] for arm in s.ARMS},
          "local_BA_change":trio["local"]["balanced_accuracy"]-trio["base"]["balanced_accuracy"] if trio["local"]["semantic_valid"] and trio["base"]["semantic_valid"] else None,
          "joint_BA_change":trio["joint"]["balanced_accuracy"]-trio["base"]["balanced_accuracy"] if trio["joint"]["semantic_valid"] and trio["base"]["semantic_valid"] else None})
    available=sum(r["available"] for r in rows)
    return {"schema":"b05-vector-credit-held72-result-v1","complete":bool(qualified and available==72 and not start_only),"runtime_qualified":qualified,
      "planned":72,"available":available,"unknown":72-available,"arms":arms,"pairs":pairs,"rows":rows,"cost":costs(list(records.values()),72),
      "start_only":sorted(start_only),"unattempted":sorted(expected-set(records)),"held_context_units":12,"paired_seed_units":24,
      "local_wins":sum(p["local_exact"] and not p["base_exact"] for p in pairs),"local_losses":sum(p["base_exact"] and not p["local_exact"] for p in pairs),
      "joint_wins":sum(p["joint_exact"] and not p["base_exact"] for p in pairs),"joint_losses":sum(p["base_exact"] and not p["joint_exact"] for p in pairs),
      "unknown_is_not_wrong":True,"fixed_held_only":True,"no_checkpoint_or_arm_selection":True}
