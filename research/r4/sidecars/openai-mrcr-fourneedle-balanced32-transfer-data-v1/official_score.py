from difflib import SequenceMatcher

def grade(response, answer, random_string_to_prepend) -> float:
    """
    Compare response and answer.
    """
    if not response.startswith(random_string_to_prepend):
        return 0
    response = response.removeprefix(random_string_to_prepend)
    answer = answer.removeprefix(random_string_to_prepend)
    return float(SequenceMatcher(None, response, answer).ratio())
