"""Leaf-local base wrapper with an explicitly loaded qualified service module."""

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import study as s

SOURCE = s.SIDE / "leaf-qwen35-identity-v1/source/serve.py"
SOURCE_SHA256 = "5d6aab04e29f4f5dd486fbecc03116c81940fb55d615d7462085a8ff9a8164f0"
QUALIFIED_SERVICE = s.SIDE / "leaf-free-id-correspondence-v1/service.py"
QUALIFIED_SERVICE_SHA256 = "51215324f767d3b7fc214bed4c64e61592fb3be8223c8d5f1dd4773fae4c48cd"
LAUNCHER_SHA256 = "d511492f9add5a8bcd7325b7899bf844febe95512aa7c562f0666c9191d6609a"
DRIVER_LIBRARY = "/export/software/system/nvidia/580.159.04/lib"
WEIGHTS_SHA256 = "c5ceac33ed456db7ba88e4b439f2e8ce85c4fbc4ca7ed8e3bcca6fcaa2e704f2"


def load_qualified_service():
    if s.sha(QUALIFIED_SERVICE) != QUALIFIED_SERVICE_SHA256:
        raise ValueError("qualified released-base service changed")
    spec = importlib.util.spec_from_file_location("leaf_role_qualified_base_service", QUALIFIED_SERVICE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def adapt_environment(environment):
    value = dict(environment)
    libraries = [p for p in value.get("LD_LIBRARY_PATH", "").split(":")
                 if p and "580.126.09" not in p and p != DRIVER_LIBRARY]
    value["LD_LIBRARY_PATH"] = ":".join([DRIVER_LIBRARY, *libraries])
    value["PATH"] = value["PATH"].replace(
        "/export/software/system/nvidia/580.126.09/bin",
        "/export/software/system/nvidia/580.159.04/bin")
    return value


def source_text():
    if s.sha(SOURCE) != SOURCE_SHA256 or s.sha(s.ROOT / "WEIGHTS.json") != WEIGHTS_SHA256:
        raise ValueError("pinned released-base source or leaf manifest changed")
    source = SOURCE.read_text()
    replacements = {
        "import service": ("service=qualified_service", 1),
        "    binding=s.read(a.binding);model=s.MODELS[binding['model']]":
            ("    binding=s.read(a.binding);model=s.MODEL", 1),
        "binding['weights_sha256']!=s.sha(s.ROOT/'WEIGHTS.json')":
            ("binding['weights_sha256']!='" + WEIGHTS_SHA256 + "'", 1),
        "    pin=s.read(s.ROOT/'SPEC.json')['source_sha256'];path=service.OLD/'scripts/launch.py'\n"
        "    if s.sha(path)!=pin[str(path)]:raise ValueError('inference launcher changed')":
            ("    path=service.OLD/'scripts/launch.py';expected='" + LAUNCHER_SHA256 + "'\n"
             "    if s.sha(path)!=expected:raise ValueError('inference launcher changed')", 1),
    }
    environment = "    env=helper._server_environment(helper._environment(),0);env['CUDA_VISIBLE_DEVICES']=gpu"
    replacements[environment] = (environment + (
        "\n    env=adapt_environment(env)"
        "\n    s.write_once(a.run_dir/'ALLOCATION_DRIVER.json',"
        "{'source_sha256':'" + SOURCE_SHA256 + "','wrapper_sha256':s.sha(__file__),"
        "'qualified_service_sha256':'" + QUALIFIED_SERVICE_SHA256 + "',"
        "'driver_library':env['LD_LIBRARY_PATH'],'old_driver_removed':True,"
        "'launcher_sha256':'" + LAUNCHER_SHA256 + "','weights_sha256':'" + WEIGHTS_SHA256 + "'})"
    ), 1)
    for before, (after, count) in replacements.items():
        if source.count(before) != count:
            raise ValueError("released-base service seam changed: " + before[:80])
        source = source.replace(before, after)
    return source


def main():
    if not Path(DRIVER_LIBRARY).is_dir():
        raise ValueError("allocation driver library missing")
    qualified_service = load_qualified_service()
    module = ModuleType("leaf_role_tool_actual_base_service_v5")
    module.__file__ = str(Path(__file__).resolve())
    module.__dict__.update(adapt_environment=adapt_environment,
                           qualified_service=qualified_service)
    exec(compile(source_text(), str(SOURCE) + ":leaf-role-attempt003", "exec"), module.__dict__)
    module.main()


if __name__ == "__main__":
    main()
