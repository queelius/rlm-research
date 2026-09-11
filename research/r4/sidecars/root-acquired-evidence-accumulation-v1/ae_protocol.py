"""Task-local decoder return-scope package; no semantic labels or task solver."""
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ANCESTOR=ROOT.parent/'adaptive-filter-pilot-v1/batch_contract.py'
ANCESTOR_SHA='d2c7f8df62a4190930dbf3e14f7e68cfb27cc573898bbc343117e8d97190bd88'

def helper_bytes(arm):
    if arm not in ('B','C'):raise ValueError('batch or cumulative arm required')
    raw=ANCESTOR.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ANCESTOR_SHA:raise ValueError('original decoder changed')
    source=raw.decode()
    if source.count('def strict_map(raw, ids):')!=1:raise ValueError('exact validator entry')
    source=source.replace('def strict_map(raw, ids):','def _validate_current(raw, ids):')
    return (source+'\n_CUMULATIVE = '+str(arm=='C')+'\n'+(ROOT/'decoder_tail.py').read_text()).encode()

def extra_prompt(arm):
    if arm=='B':
        scope='returns a fresh ordinary dict containing only the current validated batch.'
    elif arm=='C':
        scope=('returns a fresh ordinary dict containing all IDs and labels from this and prior successfully validated decoder inputs in this episode, not only the current batch. '
               'For a repeated ID, the latest successfully decoded value wins. Editing the returned dict does not edit the stored values.')
    else:raise ValueError('unknown return scope')
    return ('\n\nDecoder return contract: strict_map(raw, ids) still requires the current input to contain exactly the current requested IDs with canonical labels. It '+scope+
            ' The stored or returned labels are decoded predictions, not verified dataset truth. No decoder call requests labels or performs a task reduction.')
