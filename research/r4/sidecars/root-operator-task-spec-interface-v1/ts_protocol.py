"""Redundant public task parameters only; no algorithm or labels."""
import json

def spec(row):
    op=row['operator']
    if op not in ('threshold_users','maximum_weight','conditional_weight'):raise ValueError('composition panel only')
    return dict(operator=op,category_a=row['target'],category_b=row['target_b'] if op=='conditional_weight' else None,scope='all records and all users',threshold=5 if op=='threshold_users' else None,threshold_comparison='strictly greater than' if op=='threshold_users' else None)
def prose(value):
    fields=(('Requested operator','operator'),('Category A','category_a'),('Category B','category_b'),('Scope','scope'),('Threshold','threshold'),('Threshold comparison','threshold_comparison'))
    return ' '.join(name+': '+('not applicable' if value[key] is None else str(value[key]))+'.' for name,key in fields)+'\n'
def file_content(row):
    arm=row['interface_arm'];value=spec(row)
    if arm=='U':return None,None
    if arm=='P':return 'task.txt',prose(value).encode()
    if arm=='J':return 'task.json',(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
    raise ValueError('unknown task interface')
def extra_prompt(row):
    arm=row['interface_arm']
    return '' if arm=='U' else '\n\nA redundant task description is available in '+('task.txt (plain text).' if arm=='P' else 'task.json (JSON).')
