"""Completed actual fixture observations, not a generated-code reexecution."""
import cl_study as s

def test_actual_loader_recovers_canonical_copies_after_retained_name_error():
    output=s.ROOT/'qualification-native-001'
    file=s.read(output/'CL_CPU_0.json')['traces'][0]
    loader=s.read(output/'CL_CPU_1.json')['traces'][0]
    file_observations=[n['message'].get('content') for n in file['nodes'] if n['message'].get('role')=='tool']
    loader_observations=[n['message'].get('content') for n in loader['nodes'] if n['message'].get('role')=='tool']
    assert file_observations==['4\n']
    assert len(loader_observations)==2 and 'NameError: AUTHORED_CPU_RELOAD_CHECK' in loader_observations[0]
    assert loader_observations[1]=='4\n'
    assert file['root_reply']==loader['root_reply']=='Answer: 4'
