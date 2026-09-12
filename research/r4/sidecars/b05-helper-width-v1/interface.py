"""Only strict scoped-ID validation; no eligibility lookup/repair."""
import study
with study.aliases({'study':study},study.IDS):
    inherited=study.load('width_original_ID_validator',study.IDS/'interface.py')
grade=grade_child_response=inherited.grade
render=inherited.render
