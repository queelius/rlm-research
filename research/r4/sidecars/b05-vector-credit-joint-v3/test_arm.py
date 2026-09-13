"""Joint entry uses the same owner-created-directory repair and CPU guard."""
import study
def test_joint_actual_preflight_and_cpu_guard(monkeypatch):
 import train
 ready,rows=train.preflight();assert ready["credit_mode"]=="joint" and len(rows)==64
 monkeypatch.setenv("CUDA_VISIBLE_DEVICES","")
 try:train.trainer.run(study,study.OUTPUT,study.SCIENCE_SECONDS)
 except RuntimeError as error:assert str(error)=="CPU_ENTRY_VERIFIED: MAIN must assign one GPU before training"
 else:raise AssertionError("CPU guard absent")
 assert not study.OUTPUT.exists()
