"""Attempt-003 collector: V2 scoring with the exact recovered owned namespace."""

from pathlib import Path
from types import ModuleType

import scoring_v2
import study as s

SOURCE = s.ROOT / "driver.py"
SOURCE_SHA256 = "ebc9e3cc9a9fee3d214fab518390fd004fc92bb7f668f5410f569fc3155c0e51"
AUTHORIZED_OUTPUT = s.ROOT / "outputs/attempt-003/rollout"


def source_text():
    if s.sha(SOURCE) != SOURCE_SHA256:
        raise ValueError("frozen collector V1 changed")
    source = SOURCE.read_text()
    before = 's.ROOT / "outputs/attempt-001/rollout"'
    after = 's.ROOT / "outputs/attempt-003/rollout"'
    if source.count(before) != 1:
        raise ValueError("collector output authorization seam changed")
    return source.replace(before, after)


def validate_owner_argv(argv):
    expected_prefix = [str(Path(argv[0])), str(Path(__file__).resolve()), "run", "--endpoint"]
    if argv[:4] != expected_prefix or len(argv) != 9:
        raise ValueError("collector argv shape changed")
    if argv[5] != "--output" or argv[7] != "--deadline":
        raise ValueError("collector argv field order changed")
    endpoint = Path(argv[4])
    output = Path(argv[6])
    if output.resolve() != AUTHORIZED_OUTPUT.resolve():
        raise ValueError("only exact attempt-003 rollout is authorized")
    return {"endpoint": endpoint, "output": output, "deadline": float(argv[8])}


s.score_content = scoring_v2.score_content
s.score_missing = scoring_v2.score_missing
s.summarize = scoring_v2.summarize
module = ModuleType("free_id_driver_attempt003")
module.__file__ = str(Path(__file__).resolve())
exec(compile(source_text(), str(SOURCE) + ":attempt003", "exec"), module.__dict__)
verify = module.verify


if __name__ == "__main__":
    module.main()
