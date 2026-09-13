import study
qualifier=study.load("vector_joint_v3_checkpoint",study.SHARED/"qualify_checkpoint.py");endpoint=lambda:qualifier.endpoint(study)
