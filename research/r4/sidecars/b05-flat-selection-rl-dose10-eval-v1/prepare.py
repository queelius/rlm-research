"""Reuse actual checkpoint/native-environment qualifier and owner CPU entry seal."""
import types
import study as s
import owner

def main():
    text=(s.PARENT/'prepare.py').read_text()
    line="closure=dict(s.read(s.train.READY)['closure_sha256']);closure[str(s.train.READY)]=s.sha(s.train.READY)"
    assert text.count(line)==1
    extra=line+"\n    closure.update(s.read(s.PARENT/'READY.json')['closure_sha256'])\n    closure[str(s.PARENT/'READY.json')]=s.sha(s.PARENT/'READY.json')\n    closure[str(s.train.OUTPUT/'INITIAL_PAIRED.json')]=s.sha(s.train.OUTPUT/'INITIAL_PAIRED.json')"
    text=text.replace(line,extra)
    module=types.ModuleType('BA18_dose_same_prepare');module.__file__=str(s.PARENT/'prepare.py')
    with s.aliases({'study':s,'owner':owner},s.ROOT):
        exec(compile(text,module.__file__,'exec'),module.__dict__);module.main()

if __name__=='__main__':main()
