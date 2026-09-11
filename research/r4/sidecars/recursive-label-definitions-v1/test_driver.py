import ast

from driver import example_code


def test_definitions_change_the_child_instruction_not_the_selected_batch():
    plain = example_code("example_only")
    defined = example_code("example_definitions")
    ast.parse(plain)
    ast.parse(defined)
    assert "batch = records[:4]" in plain and "batch = records[:4]" in defined
    assert "Classify the type of answer requested" not in plain
    assert "Classify the type of answer requested" in defined
    assert " + definitions + " in defined
