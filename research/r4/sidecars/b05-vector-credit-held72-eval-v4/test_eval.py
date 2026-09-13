import hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"b05-vector-credit-held72-eval-v3/test_eval.py";assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=="04959b3d29cd467d36832adbe428adee3bcfed358ef205e11d5cb43763234bea";exec(compile(SOURCE.read_text(),str(SOURCE),"exec"),globals())
def test_native_selection_receipt_contract():
    value=study.binding();path=Path(value["selection_path"]);assert path==study.ROOT/"CHECKPOINT_QUALIFICATION.json" and study.sha(path)==value["selection_sha256"]
    assert len(value["models"])==2 and value["selection"]=="both fixed sole step1; no accuracy selection"
