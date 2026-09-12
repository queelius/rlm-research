"""Same qualified core, local output and fixed fresh training seed schedule only."""
import reuse

reuse.execute("core.py", globals(), [
    ("view.SEED = 202609125000", "view.SEED = 20260912910000"),
    ('rows = read(DATA / f"inputs/step-{step:03d}/REQUESTS.json")',
     'rows = read(ROOT / f"inputs/step-{step:03d}/REQUESTS.json")'),
])
