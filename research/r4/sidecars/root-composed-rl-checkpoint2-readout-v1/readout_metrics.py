import readout_study as study
import readout_native as native
with study.aliases({"terminal_study": study, "terminal_native": native}):
    qualified = study.load("checkpoint2_terminal_metrics", study.SOURCE / "terminal_metrics.py")
endpoint=qualified.endpoint; score_message=qualified.score_message
