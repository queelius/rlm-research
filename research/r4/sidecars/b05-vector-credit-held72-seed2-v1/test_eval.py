import hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v4/test_eval.py";assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="25a1ede04c9987f17331f101a3d0a5bf89bb9059ea3cf8fbdcc12872014435ef";exec(compile(SOURCE.read_text(),str(SOURCE),"exec"),globals())
def test_fresh_seed_namespace_and_schedule():
    assert sorted({c["seed"] for c in study.calls()})==list(range(202609520000,202609520024))
    assert study.read(study.ROOT/"SCHEDULE.json")["calls"]==[{"call":c,"prompt":study.prompt(c),"request":study.request_for(c)} for c in study.calls()]
