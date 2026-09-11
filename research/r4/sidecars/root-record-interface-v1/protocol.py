"""Lossless record formats; no algorithm or source acquisition in model packages."""
import itertools
import random
import study as s

SOURCE = s.SIDE / 'root-native-partition-join-v1'
old = s.load('record_interface_protocol_source', SOURCE / 'protocol.py',
             '6d12052bcdf2b930a8d2f39216d24407e61594c5d4cbb53f0b298c9a886e49c2')
SYSTEM, serialize, digest = old.SYSTEM, old.serialize, old.digest
score, null_row, oracle = old.score, old.null_row, old.oracle
query, record_text = old.query, old.record_text
MASTER = 981397001
REPRESENTATIONS = ('T', 'F', 'I')


def worlds():
    path = SOURCE / 'WORLDS.json'
    if s.sha(path) != 'd7ee9d28742aaa6260bc414e114f099ebb888092f1182eb37d176f6cee211bf6':
        raise ValueError('original exposed source worlds changed')
    return s.read(path)


def plan(population):
    rng = random.Random(MASTER)
    orders = list(itertools.permutations(REPRESENTATIONS)); rng.shuffle(orders)
    blocks = list(range(8)); rng.shuffle(blocks)
    result = []
    for block in blocks:
        world = population[block // 2]
        for position, arm in enumerate(orders[block % 6]):
            row = dict(world_id=world['id'], world_index=world['index'], block=block,
                       repeat=block % 2, seed=981397101 + block, representation=arm,
                       python=True, pair_position=position, dispatch_order=len(result))
            row['id'] = digest(['root-record-interface-v1', row]); result.append(row)
    return result


def evidence(world, representation, acquisitions):
    if representation not in REPRESENTATIONS or acquisitions:
        raise ValueError('only direct T/F/I source facts; no acquisitions')
    sentences = record_text(world['records'])
    typed = serialize([dict(record_id=r, customer_id=c, product=t) for r, c, t in world['records']])
    return dict(available=True, arm=representation, text=typed if representation == 'I' else sentences,
                files={'evidence.dat': sentences if representation == 'T' else typed}, acquisition_ids=[])


def prompt(world, package):
    sentence_format = ('sentence lines with the format '
                       '<record_id>: customer <customer_id> purchased product <product>.')
    json_format = ('a JSON array of objects; each object has the string fields '
                   'record_id, customer_id, product, containing the purchase record ID, customer ID and product')
    inline_format = json_format if package['arm'] == 'I' else sentence_format
    file_format = sentence_format if package['arm'] == 'T' else json_format
    return (query(world) + '\nCustomers: ' + ', '.join(world['customers']) +
            '\nInline evidence format: ' + inline_format +
            '\nFile evidence.dat format: ' + file_format +
            '\nThe file contains exactly the same purchase facts, in the same order, as the inline evidence. '
            'File access is possible only through an advertised tool; tool use is optional. '
            'No additional facts are hidden in the file.\nFiles: evidence.dat\nEvidence:\n' + package['text'] +
            '\nReturn only a JSON array of distinct customer IDs in ascending order; use [] if none.')
