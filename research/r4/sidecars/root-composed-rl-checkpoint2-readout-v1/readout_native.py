import readout_study as study
with study.aliases({"terminal_study": study}):
    qualified = study.load("checkpoint2_terminal_native", study.SOURCE / "terminal_native.py")
stack=qualified.stack; prompt=qualified.prompt; make_task=qualified.make_task
first_prefix=qualified.first_prefix; interface=qualified.interface
exact_turns=qualified.exact_turns; validate_typed_audit=qualified.validate_typed_audit
