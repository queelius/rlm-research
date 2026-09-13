"""Grade every endpoint through the unchanged vector output contract."""
import study as s
PRIOR=s.ROOT.parent/"b05-decision-vector-v1"
with s.aliases({"study":s,"interface":s.interface},s.ROOT):base=s.load("vector_credit_held_v3_vector_grader",PRIOR/"metrics.py")
aggregate=base.aggregate;costs=base.costs
def grade(call,record,order,gold):
    original=dict(call);vector={**call,"arm":"vector"};row=base.grade(vector,record,order,gold)
    row["arm"]=original["arm"];row["call_id"]=s.call_id(original)
    return row
SOURCE=s.ROOT.parent/"b05-vector-credit-held72-eval-v1/metrics.py";text=SOURCE.read_text();start=text.index("def summarize")
exec(compile(text[start:],str(SOURCE),"exec"),globals())
