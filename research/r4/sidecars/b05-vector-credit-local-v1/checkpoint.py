"""Candidate-local checkpoint qualifier."""

import study


qualifier = study.load("vector_local_checkpoint_qualifier", study.SHARED / "qualify_checkpoint.py")
endpoint = lambda: qualifier.endpoint(study)

