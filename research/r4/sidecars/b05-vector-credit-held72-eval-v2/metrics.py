"""Bind the inherited rollout's generic diagnostics import explicitly."""
import study as s
diagnostics=s.load("vector_credit_held_v2_diagnostics",s.ROLLOUT/"diagnostics.py")
with s.aliases({"study":s,"interface":s.interface,"diagnostics":diagnostics},s.ROOT):prior=s.load("vector_credit_held_v2_grader",s.ROLLOUT/"metrics.py")
grade=prior.grade;aggregate=prior.aggregate;costs=prior.costs
SOURCE=s.ROOT.parent/"b05-vector-credit-held72-eval-v1/metrics.py"
text=SOURCE.read_text();start=text.index("def summarize")
exec(compile(text[start:],str(SOURCE),"exec"),globals())
