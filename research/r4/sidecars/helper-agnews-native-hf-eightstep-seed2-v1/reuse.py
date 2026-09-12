"""Execute only authenticated, already reviewed predecessor source at local seams."""
import ast
import hashlib
from pathlib import Path

PRIOR = Path(__file__).resolve().parent.parent / "helper-agnews-native-hf-eightstep-v1"
PINS = {
    "core.py": "31ba5174f83cd559d5267a09718eec09b25b66630b7086408fd64dea1bd1f5c7",
    "train_step.py": "05a87c5a4b72c62fef9a195997a180b469f273a9e94541b89d1334912ed582e3",
    "train_ag.py": "d130f345278770ec7be08cda2aea0a563812ebbdba2ef6ba0cba54983c7daeff",
    "prepare_masks.py": "ec11625a60e41dc5712ff4195969f45d45c95b46790a00034692cc8dd84bc0a3",
    "owner.py": "8a361f5d66b5252d08027646ab4b4f84e51243dc4eaa5345f28d69b591fdcfce",
    "owner_v2.py": "35980282cd0bebb4426a1bbedf50734abb4b0af77c2cce5498e0c0c510059ed6",
    "test_continuity.py": "78f49d4e363cd3a5cc9791ce20702ba3dac92a5f811f004e9f3a295779fad8e5",
    "test_native.py": "d722833fb667264e880693b923cf2afbd96f5c2991cb9e7e7bbe3bed97ad198b",
}


def execute(name, scope, replacements=(), *, skip_main=False):
    path = PRIOR / name
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != PINS[name]:
        raise ValueError("qualified predecessor source changed: " + name)
    text = payload.decode()
    for before, after in replacements:
        if text.count(before) != 1:
            raise ValueError("exact replica seam differs: " + before)
        text = text.replace(before, after)
    tree = ast.parse(text, filename=str(path))
    if skip_main:
        guards = [node for node in tree.body if isinstance(node, ast.If)
                  and ast.unparse(node.test) == "__name__ == '__main__'"]
        if len(guards) != 1:
            raise ValueError("one predecessor CLI guard required")
        tree.body.remove(guards[0])
    # __file__ stays the new local path, so default arguments bind the NEW attempt
    # at definition time; never mutate a live predecessor module's globals.
    exec(compile(tree, str(path), "exec"), scope)
