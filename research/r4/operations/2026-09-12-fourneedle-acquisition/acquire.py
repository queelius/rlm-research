"""Bounded official data acquisition, pinned revision and LFS content checks."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import time

from huggingface_hub import HfApi, hf_hub_download

ROOT=Path(__file__).resolve().parent
REV='f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d'
DEST=Path('/project/alex_phd/research-cache/datasets')/('openai-mrcr-fourneedle-'+REV)
FILES=['README.md','4needle/4needle_0.parquet','4needle/4needle_1.parquet']

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def write(name,value):
    with (ROOT/name).open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')

def run():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    assert not DEST.exists() and not (ROOT/'ACQUISITION.json').exists()
    started=time.time()
    info=HfApi().repo_info('openai/mrcr',repo_type='dataset',revision=REV,files_metadata=True)
    assert info.sha==REV
    chosen={x.rfilename:x for x in info.siblings if x.rfilename in FILES}
    assert set(chosen)==set(FILES)
    assert sum(x.size for x in chosen.values())<=600*1024**2
    write('PLAN.json',dict(question='Does two-needle-trained retrieval transfer to third/fourth matching requests?',
        dataset='openai/mrcr',revision=REV,source_url='https://huggingface.co/datasets/openai/mrcr/tree/'+REV,
        files=FILES,expected_bytes=sum(x.size for x in chosen.values()),cap_bytes=600*1024**2,
        output=str(DEST),GPU_calls=0,model_queries=0,started_epoch=started))
    artifacts=[]
    for name in FILES:
        path=Path(hf_hub_download('openai/mrcr',name,repo_type='dataset',revision=REV,local_dir=DEST))
        entry=chosen[name];actual=sha(path)
        assert path.stat().st_size==entry.size
        expected=getattr(entry.lfs,'sha256',None) if entry.lfs else None
        if expected:assert actual==expected
        artifacts.append(dict(name=name,path=str(path),bytes=path.stat().st_size,sha256=actual,
                              repository_blob_id=entry.blob_id,lfs_sha256=expected))
    assert 'license: mit' in (DEST/'README.md').read_text().lower()
    write('ACQUISITION.json',dict(dataset='openai/mrcr',revision=REV,license='MIT',
        retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),artifacts=artifacts,
        elapsed_seconds=time.time()-started,source_script_sha256=sha(__file__),
        GPU_calls=0,model_queries=0,third_party_code_executed=False,
        split_provenance='Official four-needle files; no cohort, train/test assignment or model outcomes yet.'))
    print(dict(complete=True,bytes=sum(x['bytes'] for x in artifacts),output=str(DEST)))

if __name__=='__main__':run()
