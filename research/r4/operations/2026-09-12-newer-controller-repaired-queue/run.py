"""Same reviewed two-model queue, additive repaired READY and fresh output only."""
import hashlib
from pathlib import Path

original = Path(__file__).resolve().parent.parent/'2026-09-12-newer-controller-screen-queue/run.py'
source = original.read_text()
for before, after, count in (
    ('SIDE / "READY.json"', 'SIDE / "READY_V2.json"', 1),
    ('7c86dbdfa4fe125563cc0e642e7241455fda872469339c5ecb1f63bf46c51b5e', 'ef75f8a04b5d631194fd34f390e0e9e99f4bf292b870243cb8497ec2d069afe7', 1),
    ('outputs/attempt-001', 'outputs/attempt-002', 2),
    ('Full source, native-template fixtures and inherited lifecycle reviewed. MAIN actual owner verify passed 5820 source pins and model stat receipts; CPU-only native two-turn qualification passed both model packages.',
     'MAIN fully read original screen and all V2 repair/test/seal files. Actual owner_v2 verify passed5844 pins. Four focused tests pass, including two-tool native budget completion; CPU882-token validation0.039s. Only vocabulary-size lookup hoisted, all checks preserved. Failed945-second attempt remains separate, no model-ranking evidence from it.', 1),
):
    assert source.count(before) == count, before
    source = source.replace(before, after)
# Execute only MAIN-authored, fully inspected operation source. __file__ keeps
# receipts in this new operation; no previous file or artifact is modified.
exec(compile(source, str(original)+':reviewed-v2-ready-output', 'exec'), globals())
