"""Only full raw inline visibility varies; all source facts remain in the file."""
import random
import study as s

SOURCE = s.SIDE / 'root-native-partition-join-v1'
old = s.load('externalization_original_protocol', SOURCE / 'protocol.py',
             '6d12052bcdf2b930a8d2f39216d24407e61594c5d4cbb53f0b298c9a886e49c2')
SYSTEM, serialize, digest = old.SYSTEM, old.serialize, old.digest
score, null_row, oracle = old.score, old.null_row, old.oracle
query, record_text = old.query, old.record_text
MASTER = 981591001
ORDERS = ('random','reverse')
INVENTORY_PINS = {
    'root-native-partition-join-v1': 'd7ee9d28742aaa6260bc414e114f099ebb888092f1182eb37d176f6cee211bf6',
    'root-record-interface-v1': 'd7ee9d28742aaa6260bc414e114f099ebb888092f1182eb37d176f6cee211bf6',
    'root-record-externalization-v1': 'd7ee9d28742aaa6260bc414e114f099ebb888092f1182eb37d176f6cee211bf6',
    'root-partition-report-pilot-v1': 'ceb5e8f0ca0e05f7dd54535304882cfdc64d3088b19af28e8a63f54e3619b0c4',
}
REPRESENTATIONS = ('I', 'E')


def inventory():
    result=[]
    for name,pin in INVENTORY_PINS.items():
        path=s.SIDE/name/'WORLDS.json'
        if s.sha(path)!=pin:raise ValueError('explicit historical world inventory changed')
        result.extend(s.read(path))
    return result

def worlds():
    historical=inventory();used_customers={r[1] for w in historical for r in w['records']}
    used_ids={r[0] for w in historical for r in w['records']};result=[]
    for wi in range(8):
        seed=981591011+wi;rng=random.Random(seed)
        customers=rng.sample([f'c{x:04}' for x in range(1000,10000) if f'c{x:04}' not in used_customers],12)
        ids=rng.sample([f'r{x:05}' for x in range(10000,100000) if f'r{x:05}' not in used_ids],48)
        used_customers.update(customers);used_ids.update(ids)
        products=rng.sample(['K','L','M','N','P','R','S','T'],4)
        records=[[ids[4*ci+pi],customer,rng.choice(products)] for ci,customer in enumerate(customers) for pi in range(4)]
        result.append(dict(id=f'fresh-order-join-{wi}',index=wi,generator_seed=seed,
            order_seed=981591201+wi,customers=sorted(customers),products=products,
            query_products=products[:2],records=records))
    return result

def ordered_world(world,order):
    if order not in ORDERS:raise ValueError('record order')
    indices=list(range(48));random.Random(world['order_seed']).shuffle(indices)
    if order=='reverse':indices.reverse()
    return {**world,'records':[world['records'][i] for i in indices],'record_order':order}

def plan(population):
    cells=[('I','random'),('E','random'),('I','reverse'),('E','reverse')]
    rows=[]
    for wi in sorted(range(8),key=lambda i:digest([MASTER,'world-dispatch',i])):
        world=population[wi];order=cells[wi%4:]+cells[:wi%4]
        for position,(arm,record_order) in enumerate(order):
            row=dict(world_id=world['id'],world_index=wi,block=2*wi+ORDERS.index(record_order),
                repeat=0,seed=981591101+wi,record_order=record_order,representation=arm,python=True,
                pair_position=position,dispatch_order=len(rows))
            row['id']=digest(['root-fresh-join-externalization-order-v1',row]);rows.append(row)
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
