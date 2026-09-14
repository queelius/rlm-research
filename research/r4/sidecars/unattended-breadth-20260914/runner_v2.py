"""Pin the installed tokenizer's return representation explicitly."""
import hashlib
from pathlib import Path
SOURCE=Path(__file__).with_name('runner.py')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='df1fcef621aa40603b0ff4849f1c7bcbaf79527630e1dfcdd9d8c19717fcc154'
source=SOURCE.read_text()
old='tokenize=True,add_generation_prompt=True,enable_thinking=False)'
assert source.count(old)==1
source=source.replace(old,'tokenize=True,return_dict=False,add_generation_prompt=True,enable_thinking=False)')
exec(compile(source,str(SOURCE),'exec'),globals())
