"""Load only the preserved, qualified policy/activation-storage implementation seams."""

import importlib.util

from config import V2

spec = importlib.util.spec_from_file_location(
    "fourstep_qualified_decoder_wrapper", V2 / "runner.py"
)
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)
v1 = wrapper.v1
install_eval_checkpoints = wrapper.install_eval_checkpoints
read = wrapper.read
sha = wrapper.sha256
write = wrapper.write_json
