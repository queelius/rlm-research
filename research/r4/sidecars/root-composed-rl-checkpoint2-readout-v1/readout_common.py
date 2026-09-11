import readout_study as study
with study.aliases({"terminal_study": study}):
    qualified = study.load("checkpoint2_terminal_common", study.SOURCE / "terminal_common.py")
c = qualified.c
starting_decision=qualified.starting_decision
generation=qualified.generation
transition=qualified.transition
