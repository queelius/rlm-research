"""Use the frozen two-example prompt builder verbatim, without a new variant."""
import study
with study.aliases({"study":study},study.PRIOR):
    inherited=study.load("finqa_fresh_identical_interface",study.PRIOR/"interface.py")
prompt=inherited.prompt
examples=inherited.examples
FACTS=inherited.FACTS
