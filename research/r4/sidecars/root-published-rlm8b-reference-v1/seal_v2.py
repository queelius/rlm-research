"""Additive V2 seal; preserve original READY and scientific sources."""
import copy,xml.etree.ElementTree as ET
import rv_study as s,owner_v2
def main():
    assert not s.ATTEMPT.exists() and s.sha(s.ROOT/'READY.json')==owner_v2.OLD_READY
    test=ET.parse(s.ROOT/'CPU_TESTS_V2_002.xml').getroot().find('testsuite')
    assert int(test.attrib['tests'])==15 and int(test.attrib['errors'])==int(test.attrib['failures'])==0
    ready=copy.deepcopy(s.read(s.ROOT/'READY.json'));ready.pop('identity');pins=ready['source_sha256']
    names=['READY.json','owner_v2.py','collect_v2.py','test_accounting_v2.py','test_native_block_v2.py','AMENDMENT_V2.md','seal_v2.py','CPU_TESTS_V2.xml','CPU_TESTS_V2_002.xml']
    for name in names:
        path=s.ROOT/name;pins[str(path)]=s.sha(path)
    for name in ('qualification-v2-001','qualification-v2-002'):
        for path in (s.ROOT/name).rglob('*'):
            if path.is_file():pins[str(path.resolve())]=s.sha(path)
    ready.update(schema='published-rlm8b-reference-ready-v2',previous_ready_sha256=owner_v2.OLD_READY,additive_corrections=['every-coordinate physical ledger reconciliation','current-iteration in-block FINAL_VAR native authentication'],owner_argv=[str(s.NATIVE),str(s.ROOT/'owner_v2.py'),'run','--output',str(s.ATTEMPT)],verify_argv=[str(s.NATIVE),str(s.ROOT/'owner_v2.py'),'verify'],v2_qualification=dict(tests=15,seconds=float(test.attrib['time']),junit_sha256=s.sha(s.ROOT/'CPU_TESTS_V2_002.xml'),actual_isolated_native_block_fixture=True))
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY_v2.json',ready)
    print(dict(ready_sha256=s.sha(s.ROOT/'READY_v2.json'),identity=ready['identity'],pins=len(pins)))
if __name__=='__main__':main()
