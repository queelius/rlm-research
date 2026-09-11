"""Cross-model stable-anchor bindings for released Qwen3-8B."""
import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
PRIOR = SIDE / "leaf-mnli-stable-anchor-vs-sequence-counting-v1"
FREE = SIDE / "leaf-free-id-correspondence-v1"
MODEL_PATH = Path("/project/alex_phd/research-cache/models/Qwen--Qwen3-8B--b968826d9c46dd6066d109eabc6255188de91218")
MODEL = {"alias": "qwen3-8b-stable-anchor", "path": str(MODEL_PATH),
         "revision": "b968826d9c46dd6066d109eabc6255188de91218",
         "manifest_sha256": "2d7abf2289f2067ee55f3629430e619de4718e0a8decd454af7f26448ffaa2f4"}
MODELS = {"qwen3": MODEL}
ATTEMPT = ROOT / "outputs/attempt-001"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")


def sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read(path): return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        handle.write("\n")


write_once = write
serialize = lambda value: json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
digest = lambda value: hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@contextlib.contextmanager
def aliases(values):
    old = {key: sys.modules.get(key) for key in values}; sys.modules.update(values)
    try: yield
    finally:
        for key, value in old.items():
            if value is None: sys.modules.pop(key, None)
            else: sys.modules[key] = value


def load(name, path, pin=None, aliases_map=None):
    if pin and sha(path) != pin: raise ValueError("source changed: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    with aliases(aliases_map or {}): spec.loader.exec_module(module)
    return module


prior = load("qwen8b_stable_prior", PRIOR / "study.py",
             "a11a23ba286745a32a16b9c47e9cbceaa995fffa9bf3a1cbbecf9fa399b13243")
base, lifecycle = prior.base, prior.lifecycle
service = load("qwen8b_stable_service_contract", FREE / "service.py",
               "51215324f767d3b7fc214bed4c64e61592fb3be8223c8d5f1dd4773fae4c48cd",
               {"study": sys.modules[__name__]})


def tokenizer():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True, trust_remote_code=False)


def verify():
    prior.verify()
    ready = read(ROOT / "READY.json")
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready["identity"]:
        raise ValueError("READY identity")
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        if sha(path) != pin: raise ValueError("closure changed: " + path)
    manifest = read(MODEL_PATH / "local-research-manifest.json")
    if manifest["huggingface_revision"] != MODEL["revision"] or sha(MODEL_PATH / "local-research-manifest.json") != MODEL["manifest_sha256"]:
        raise ValueError("8B model manifest changed")
    return ready
