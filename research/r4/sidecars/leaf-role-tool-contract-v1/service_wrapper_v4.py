"""Bind the qualified released-base launcher to this sidecar's no-adapter manifest."""

from pathlib import Path
from types import ModuleType

import study as s

SOURCE = s.SIDE / "leaf-qwen35-identity-v1/source/serve.py"
SOURCE_SHA256 = "5d6aab04e29f4f5dd486fbecc03116c81940fb55d615d7462085a8ff9a8164f0"
LAUNCHER_SHA256 = "d511492f9add5a8bcd7325b7899bf844febe95512aa7c562f0666c9191d6609a"
DRIVER_LIBRARY = "/export/software/system/nvidia/580.159.04/lib"
WEIGHTS_SHA256 = "c5ceac33ed456db7ba88e4b439f2e8ce85c4fbc4ca7ed8e3bcca6fcaa2e704f2"


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
    if s.sha(SOURCE) != SOURCE_SHA256 or s.sha(s.ROOT / "WEIGHTS.json") != WEIGHTS_SHA256:
        raise ValueError("pinned released-base source or leaf manifest changed")
    source = SOURCE.read_text()
    replacements = {
        "    binding=s.read(a.binding);model=s.MODELS[binding['model']]":
            "    binding=s.read(a.binding);model=s.MODEL",
        "binding['weights_sha256']!=s.sha(s.ROOT/'WEIGHTS.json')":
            "binding['weights_sha256']!='" + WEIGHTS_SHA256 + "'",
        "    pin=s.read(s.ROOT/'SPEC.json')['source_sha256'];path=service.OLD/'scripts/launch.py'\n"
        "    if s.sha(path)!=pin[str(path)]:raise ValueError('inference launcher changed')":
            "    path=service.OLD/'scripts/launch.py';expected='" + LAUNCHER_SHA256 + "'\n"
            "    if s.sha(path)!=expected:raise ValueError('inference launcher changed')",
    }
    environment = "    env=helper._server_environment(helper._environment(),0);env['CUDA_VISIBLE_DEVICES']=gpu"
    replacements[environment] = environment + (
        "\n    env=adapt_environment(env)"
        "\n    s.write_once(a.run_dir/'ALLOCATION_DRIVER.json',"
        "{'source_sha256':'" + SOURCE_SHA256 + "','wrapper_sha256':s.sha(__file__),"
        "'driver_library':env['LD_LIBRARY_PATH'],'old_driver_removed':True,"
        "'launcher_sha256':'" + LAUNCHER_SHA256 + "','weights_sha256':'" + WEIGHTS_SHA256 + "'})"
    )
    for before, after in replacements.items():
        if source.count(before) != 1:
            raise ValueError("released-base service seam changed: " + before[:80])
        source = source.replace(before, after)
    return source


def main():
    if not Path(DRIVER_LIBRARY).is_dir():
        raise ValueError("allocation driver library missing")
    module = ModuleType("leaf_role_tool_actual_base_service_v4")
    module.__file__ = str(Path(__file__).resolve())
    module.__dict__.update(adapt_environment=adapt_environment)
    exec(compile(source_text(), str(SOURCE) + ":leaf-role-attempt002", "exec"), module.__dict__)
    module.main()


if __name__ == "__main__":
    main()
