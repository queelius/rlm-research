"""Write immutable public input/provenance artifacts, never select on results."""
import paper_prompt,rv_protocol as p,rv_study as s
def main():
    x=paper_prompt.extract();directory=s.ROOT/'inputs';directory.mkdir(exist_ok=False)
    for key,name in [('tex','paper-methods.tex'),('base','paper-base.txt'),('published_diff','paper-published.diff'),('reconstructed','paper-Qwen8B.txt'),('actual_diff','paper-applied.diff')]:
        with (directory/name).open('x') as f:f.write(x[key])
    s.write(directory/'PAPER_RECEIPT.json',dict(url='https://arxiv.org/src/2512.24601v2',version='v2',archive=str(s.PAPER),archive_sha256=s.sha(s.PAPER),member='appendix/sec3-methods.tex',replacements=x['replacements'],deviation='Contextual FINAL_VAR insertion after closed final example; published line numbers do not align; paper-derived not authenticated training prompt'))
    rows=p.plan();s.write(directory/'PLAN.json',rows)
    s.write(directory/'TASKS.json',{r['id']:p.task(r) for r in rows})
    s.write(directory/'HOST_GOLD.json',{r['id']:p.gold(r) for r in rows})
    s.write(directory/'SOURCE.json',{str(s.QSR/n):s.sha(s.QSR/n) for n in ['PUBLIC.json','QUERIES.json','HOST_GOLD.json','GROUPS.json']})
    s.write(directory/'MODELS.json',{k:dict(model=v,manifest_sha256=s.sha(s.MODEL_ROOT/ s.MODEL_ROOT.joinpath(v['path']).name/'local-research-manifest.json')) for k,v in s.MODELS.items()})
    print(dict(planned=len(rows),nonzero_per_policy=sum(p.gold(r)>0 for r in rows[:24]),paper_sha256=s.sha(directory/'paper-Qwen8B.txt')))
if __name__=='__main__':main()
