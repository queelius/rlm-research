"""New-node driver adaptation with actual wrapper identity for the pinned base service."""

from pathlib import Path
from types import ModuleType

import study as s

SOURCE = s.SIDE / "leaf-qwen35-identity-v1/source/serve.py"
SOURCE_SHA256 = "5d6aab04e29f4f5dd486fbecc03116c81940fb55d615d7462085a8ff9a8164f0"
DRIVER_LIBRARY = "/export/software/system/nvidia/580.159.04/lib"


def adapt_environment(environment):
    value = dict(environment)
    libraries = [p for p in value.get("LD_LIBRARY_PATH", "").split(":")
                 if p and "580.126.09" not in p and p != DRIVER_LIBRARY]
    value["LD_LIBRARY_PATH"] = ":".join([DRIVER_LIBRARY, *libraries])
    value["PATH"] = value["PATH"].replace(
        "/export/software/system/nvidia/580.126.09/bin",
        "/export/software/system/nvidia/580.159.04/bin",
    )
    return value


def source_text():
    if s.sha(SOURCE) != SOURCE_SHA256:
        raise ValueError("pinned released-base service changed")
    source = SOURCE.read_text()
    before = "    env=helper._server_environment(helper._environment(),0);env['CUDA_VISIBLE_DEVICES']=gpu"
    if source.count(before) != 1:
        raise ValueError("base service environment seam changed")
    after = before + "\n    env=adapt_environment(env)\n    s.write_once(a.run_dir/'ALLOCATION_DRIVER.json',{'source_sha256':'" + SOURCE_SHA256 + "','wrapper_sha256':s.sha(__file__),'driver_library':env['LD_LIBRARY_PATH'],'old_driver_removed':True})"
    return source.replace(before, after)


def main():
    if not Path(DRIVER_LIBRARY).is_dir():
        raise ValueError("allocation driver library missing")
    module = ModuleType("free_id_actual_base_service_v2")
    module.__file__ = str(Path(__file__).resolve())
    module.__dict__.update(adapt_environment=adapt_environment)
    exec(compile(source_text(), str(SOURCE) + ":free-id-allocation-driver-v2", "exec"),
         module.__dict__)
    module.main()


if __name__ == "__main__":
    main()
