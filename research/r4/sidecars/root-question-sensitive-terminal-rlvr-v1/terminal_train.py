"""Qualified trainer with exact terminal-RLVR native replay entry."""
import sys
import types

import terminal_common as common
import terminal_study as study

SOURCE = study.QSR / "qsr_train.py"
PIN = "a5064c270f80e157945775accde4e57cd9c5f9e82d1bb17862a118786cb13878"
study.check(SOURCE, PIN)
text = SOURCE.read_text()
before = "str(s.ROOT/'qsr_native.py')"
after = "str(s.ROOT/'terminal_native.py')"
if text.count(before) != 1:
    raise ValueError("qualified native replay seam changed")
qualified = types.ModuleType("terminal_qualified_qsr_train")
qualified.__file__ = str(SOURCE)
sys.modules[qualified.__name__] = qualified
with study.aliases({"qsr_study": study, "qsr_common": common}):
    exec(compile(text.replace(before, after), str(SOURCE) + ":terminal-native", "exec"),
         qualified.__dict__)

check_members = qualified.check_members
authenticate_group = qualified.authenticate_group
parse_args = qualified.parse_args
impl = qualified.impl


if __name__ == "__main__":
    import json
    import traceback
    import uuid
    args = parse_args()
    try:
        print(json.dumps(impl.train(args), sort_keys=True, allow_nan=False))
    except BaseException as error:
        if args.output is not None:
            study.write(args.output.parent / ("TRAIN_FAILURE-" + uuid.uuid4().hex + ".json"),
                        {"type": type(error).__name__, "error": str(error),
                         "traceback": traceback.format_exc(), "checkpoint_preserved": True})
        raise
