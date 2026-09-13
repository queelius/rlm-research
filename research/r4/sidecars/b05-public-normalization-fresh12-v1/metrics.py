"""Identical score formulas, only prospective counts/schema changed 36→48."""
import study
path=study.PRIOR/'metrics.py';text=path.read_text()
for old,new,count in [('"planned":18','"planned":24',1),('selected],18)','selected],24)',1),('available==36','available==48',1),('"planned":36','"planned":48',1),('"unknown":36-available','"unknown":48-available',1),('"context_units":9','"context_units":12',1),('"paired_seed_units":18','"paired_seed_units":24',1),('list(records.values()),36','list(records.values()),48',1),('normalization-held9-result','normalization-fresh12-result',1)]:
    assert text.count(old)==count,(old,text.count(old));text=text.replace(old,new)
exec(compile(text,str(path),'exec'),globals())
