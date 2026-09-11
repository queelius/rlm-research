"""Correctly bind the qualified wrapper to its immediate ancestral study."""

from pathlib import Path
import study as s


def main():
    # The immediate qualified wrapper requires ALIEN from its own study. Attempt-001
    # incorrectly rebound it to the leaf replication study, which lacks that interface.
    with s.aliases({"study": s.qualified}):
        wrapper = s.load(
            "field_order_recovery_qualified_service",
            s.QUALIFIED / "service_wrapper.py",
            "72bd90f6af3cb9fb52818a20ffc6822804a9d42a8bb9f8ed6974ad6b3173ba73",
        )
    wrapper.__file__ = str(Path(__file__).resolve())
    wrapper.main()


if __name__ == "__main__":
    main()

