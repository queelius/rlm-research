"""Owned wrapper with launcher identity bound to this sidecar."""

from pathlib import Path

import study as s


def main():
    wrapper = s.load("positional_anchor_new_context_service", s.PRIOR / "service_wrapper_v2.py", "54aee392085062fb81cee40b0b09458542991d4db4f5aba5a7b147c5b8f17101", {"recovery_study": s.qualified})
    wrapper.__file__ = str(Path(__file__).resolve())
    wrapper.main()


if __name__ == "__main__":
    main()
