"""Only full raw inline visibility varies; all source facts remain in the file."""
import study as s

SOURCE = s.SIDE / 'root-native-partition-join-v1'
old = s.load('externalization_original_protocol', SOURCE / 'protocol.py',
             '6d12052bcdf2b930a8d2f39216d24407e61594c5d4cbb53f0b298c9a886e49c2')
SYSTEM, serialize, digest = old.SYSTEM, old.serialize, old.digest
score, null_row, oracle = old.score, old.null_row, old.oracle
query, record_text = old.query, old.record_text
MASTER = 981492001
REPRESENTATIONS = ('I', 'E')


def worlds():
    path=SOURCE/'WORLDS.json'
    if s.sha(path) != 'd7ee9d28742aaa6260bc414e114f099ebb888092f1182eb37d176f6cee211bf6':
        raise ValueError('immutable exposed worlds changed')
    return s.read(path)


def plan(population):
    blocks=sorted(range(8),key=lambda b:digest([MASTER,'block',b]));rows=[]
    for block in blocks:
        world=population[block//2]
        arms=REPRESENTATIONS if block%2==0 else tuple(reversed(REPRESENTATIONS))
        for position,arm in enumerate(arms):
            row=dict(world_id=world['id'],world_index=world['index'],block=block,repeat=block%2,
                seed=981492101+block,representation=arm,python=True,pair_position=position,dispatch_order=len(rows))
            row['id']=digest(['root-record-externalization-v1',row]);rows.append(row)
    return rows


def evidence(world,representation,acquisitions):
    if representation not in REPRESENTATIONS or acquisitions:
        raise ValueError('only direct full source records, without acquisition')
    typed=serialize([dict(record_id=r,customer_id=c,product=t) for r,c,t in world['records']])
    return dict(available=True,arm=representation,text=typed if representation=='I' else '',
        files={'evidence.dat':typed},acquisition_ids=[])


def prompt(world,package):
    return (query(world)+'\nCustomers: '+', '.join(world['customers'])+
        '\nEvidence format: a JSON array of objects; each object has the string fields '
        'record_id, customer_id, product, containing the purchase record ID, customer ID and product.'
        '\nThe file evidence.dat contains all 48 purchase facts for this task in source order. '
        'Any evidence printed below is the same JSON data. '
        'File access is possible only through an advertised tool; tool use is optional.'
        '\nFiles: evidence.dat\nEvidence:\n'+package['text']+
        '\nReturn only a JSON array of distinct customer IDs in ascending order; use [] if none.')
