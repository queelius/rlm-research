"""Explicit qualified study/service namespaces around the proven an27 base launcher."""
from pathlib import Path
import study as s


def main():
    with s.aliases({'study': s.qualified.free, 'service': s.service}):
        wrapper = s.load('join_actual_qualified_service', s.FREE / 'service_wrapper_v3.py',
                         '4347c92894a24e357a74f8b9e372edcc4b3327532de183d9a59873331dc5a9d0')
        wrapper.__file__ = str(Path(__file__).resolve())
        wrapper.main()


if __name__ == '__main__': main()

