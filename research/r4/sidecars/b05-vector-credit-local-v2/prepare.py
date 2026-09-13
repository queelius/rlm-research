import study
prepare_arm = study.load("vector_local_v2_prepare", study.SHARED / "prepare_arm.py")
if __name__ == "__main__": prepare_arm.prepare(study)
