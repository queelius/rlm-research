"""Private namespace/seed adapter; authenticated original identity helpers unchanged."""
import hashlib
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "root-rlvr-campaign-v1"
CONT = ROOT.parent / "root-recovered-child-continuation-v1"
SEED = 981265001
PINS = {
    OLD / "campaign_common.py": "17e888550668638673fa725c6a580b7580b6abd975bd27f69b8be7ad628800ea",
    OLD / "campaign.py": "fc94c8ff29fd043d27ff2e13e023214c87214379e5b557c3119cf41566a7c193",
    OLD / "campaign_native.py": "876c084e8f76924becd6f11b2be72e43fd00061b82729e20d98111efcc71a807",
    OLD / "campaign_train.py": "38fe3087b8deb94ee8e0fa2e0330ca34a822f84192031c389ff32acf00d79d1f",
    OLD / "campaign_lifecycle_v2.py": "568927528f46a203669a6b7671facc9e7419191850d3f050a58de066e5c6c0d5",
    OLD / "CAMPAIGN.json": "8ea80a8f8ebbc48eebe7816e121d6ee32b1d3cd2d17ce4c069e0c47383f57c2f",
    OLD / "RECIPE.json": "94c703334e8b2808ac0a859c009eb7c3516737af1c3e15fc79588b4d47d3a200",
    CONT / "native_amendment.py": "718ed07886e05c4ddcaaad06edda54fe1db017b2fa17cb525232fd9224ddc491",
}


def private(name, path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != PINS[path]:
        raise ValueError("qualified upstream source changed: " + str(path))
    loader = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(loader)
    sys.modules[name] = module
    loader.loader.exec_module(module)
    return module


impl = private("independent_seed_private_common", OLD / "campaign_common.py")
impl.ROOT = ROOT
impl.SEED = SEED


def __getattr__(name):
    return getattr(impl, name)
