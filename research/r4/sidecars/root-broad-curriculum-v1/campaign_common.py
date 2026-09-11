"""Private, count-checked adaptation of the authenticated campaign identity helpers."""
import hashlib
import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / 'root-rlvr-campaign-v1'
CONT = ROOT.parent / 'root-recovered-child-continuation-v1'
DATA = ROOT.parent / 'root-curriculum-data-v1'
SEED = 981268001
PINS = {
    OLD/'campaign_common.py':'17e888550668638673fa725c6a580b7580b6abd975bd27f69b8be7ad628800ea',
    OLD/'campaign.py':'fc94c8ff29fd043d27ff2e13e023214c87214379e5b557c3119cf41566a7c193',
    OLD/'campaign_native.py':'876c084e8f76924becd6f11b2be72e43fd00061b82729e20d98111efcc71a807',
    OLD/'campaign_train.py':'38fe3087b8deb94ee8e0fa2e0330ca34a822f84192031c389ff32acf00d79d1f',
    OLD/'campaign_lifecycle_v2.py':'568927528f46a203669a6b7671facc9e7419191850d3f050a58de066e5c6c0d5',
    OLD/'CAMPAIGN.json':'8ea80a8f8ebbc48eebe7816e121d6ee32b1d3cd2d17ce4c069e0c47383f57c2f',
    OLD/'RECIPE.json':'94c703334e8b2808ac0a859c009eb7c3516737af1c3e15fc79588b4d47d3a200',
    OLD/'test_training.py':'5f9715d687b350c430bc633ffad5de1b2a9f158c699c046f481909c93bc7b265',
    ROOT.parent/'root-only-credit-v1/qualify_native.py':'17ef2be02ab8ab657fefc6940632161d15c2e0e9bc1dd517ddf1561d9072c736',
    CONT/'native_amendment.py':'718ed07886e05c4ddcaaad06edda54fe1db017b2fa17cb525232fd9224ddc491',
    ROOT.parent/'root-seed-lifecycle-continuation-v1/driver.py':'bdf75065eec803bb9a2952aa7ac5debcbaa4db1f35d69c48958dc1eaa964cbdd',
    DATA/'MANIFEST.json':'3b00b9a7ce4dd2cb086ed8937e459e852503139819d08c8e544d51f69c6bd0d6',
    OLD/'inputs/PLANS.json':'9c7af7f96517566fab48cda53ca0b4457407595872801209d7d5766ca18b86bb',
    ROOT.parent/'root-rlvr-independent-seed-v1/inputs/PLANS.json':'c1771ea4c6c1e69de36ab9ba3a610437a58fcab37f11a9cead86efe0a28aa116',
    ROOT.parent/'root-only-credit-v1/inputs/PLAN.json':'eda43b371d164ddeb3f928e822dcb7c1c938e87b903ba774bd442d3044c0f6a2',
    ROOT.parent/'root-credit-validation-replay-v1/SPEC_ORIGINAL.json':'c7a3c8d0bb4af8d22b6ab10c6f8a3131c6ecd4ab9a78468522c5d1dcab22d4b7',
    ROOT.parent/'root-return-contract-factorial-v1/inputs/PLAN.json':'d11ae450d79d201e0813ea3c95a9485c8a6a9fb4bb40325aa5008908f6cd4bd5',
    ROOT.parent/'root-receipt-ablation-v1/inputs/PLAN.json':'524bdb9f2a76d5bb8a8d3e882ca380e7c5dcd4a01392dd07369b3bf2dcb5ad1c',
}
TRANSFORMATIONS = {}


def adapted(name, path, replacements=(), extra=None):
    path = Path(path)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PINS[path]:
        raise ValueError('qualified upstream source changed: '+str(path))
    source = raw.decode()
    for before, after, count in replacements:
        if source.count(before) != count:
            raise ValueError('private replacement count changed: '+repr(before))
        source = source.replace(before, after)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__dict__.update(extra or {})
    sys.modules[name] = module
    exec(compile(source, str(path), 'exec'), module.__dict__)
    TRANSFORMATIONS[name] = {'source_path':str(path),'source_sha256':PINS[path],
        'executed_source_sha256':hashlib.sha256(source.encode()).hexdigest(),
        'replacements':[{'before':a,'after':b,'count':n} for a,b,n in replacements]}
    return module


private = adapted
impl = adapted('broad_private_common', OLD/'campaign_common.py', [
    ('generation["round"] <= 8','generation["round"] <= 16',1),
    ('must be1..8','must be1..16',1),
    ('read(ROOT / "READY.json")["campaign_sha256"]','read(ROOT / "PREPARED.json")["campaign_sha256"]',1)])
impl.ROOT, impl.SEED = ROOT, SEED


def __getattr__(name):
    return getattr(impl,name)
