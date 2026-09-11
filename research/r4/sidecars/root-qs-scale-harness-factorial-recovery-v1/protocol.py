"""Complete protocol surface expected by the reused operator collector."""

import study as s

qualified = s.prior.protocol()
for name in dir(qualified):
    if not name.startswith("__"):
        globals()[name] = getattr(qualified, name)
joint = qualified.old.shared()
null_row = joint.null_row
verify_replay = joint.verify_replay
error_probe = joint.old.error_probe
