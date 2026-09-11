"""Credited-position projection helpers; Torch is imported only inside GPU/CPU entries."""


def position_list(turn):
    prompt = turn.get("prompt_length")
    actions = turn.get("old_logprobs")
    inputs = turn.get("input_ids")
    if type(prompt) is not int or prompt < 1 or not isinstance(actions, list) or not actions:
        raise ValueError("invalid current-action span")
    count = len(actions)
    if not isinstance(inputs, list) or prompt + count != len(inputs):
        raise ValueError("action span does not end at input boundary")
    return list(range(prompt - 1, prompt - 1 + count))


def selected_tis_loss(logits, turn, *, advantage, temperature, tis):
    """Adapt already-selected [1, action, vocab] logits to the qualified loss unchanged."""
    count = len(position_list(turn))
    if tuple(logits.shape[:2]) != (1, count):
        raise ValueError("selected logits shape differs from credited action span")
    local = dict(turn)
    local["prompt_length"] = 1
    local["input_ids"] = [turn["input_ids"][turn["prompt_length"] - 1], *turn["input_ids"][turn["prompt_length"] :]]
    local["labels"] = [-100, *turn["input_ids"][turn["prompt_length"] :]]
    local["loss_mask"] = [0, *([1] * count)]
    return tis.tis_action_loss(logits, local, advantage=advantage, temperature=temperature)
