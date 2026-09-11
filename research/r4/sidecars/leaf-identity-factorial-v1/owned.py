"""Count-checked private96→384/cap adapter; unchanged owned service semantics."""
from pathlib import Path
import hashlib

SOURCE_PATH = Path(__file__).resolve().parent.parent / 'leaf-identity-counter-v1/owned.py'
SOURCE_SHA256 = '8b3f18ec32748ba5189a61d64aea99c5ce087b15b53ae999e643c60e48261d29'
_text = SOURCE_PATH.read_text()
if hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() != SOURCE_SHA256:
    raise ValueError('qualified owned wrapper changed')
EDITS = [('identity_counter', 'identity_factorial', 5), ('96', '384', 2),
         ('1080', '2280', 1), ('630', '1830', 1), ('1200', '2400', 3), ('600', '1800', 1),
         ('if __name__ == "__main__":', 'if False:', 1)]
for before, after, count in EDITS:
    if _text.count(before) != count:
        raise ValueError('owned adapter occurrence changed: ' + before)
    _text = _text.replace(before, after)
ADAPTED_SHA256 = hashlib.sha256(_text.encode()).hexdigest()
# __file__ is this new owned sidecar; imported helpers remain read-only and pinned.
exec(compile(_text, str(SOURCE_PATH) + ':factorial-private-adapter', 'exec'), globals())

if __name__ == '__main__':
    main()
