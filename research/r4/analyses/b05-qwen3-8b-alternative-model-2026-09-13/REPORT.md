# Qwen3-8B B05 alternative-model audit

Status: COMPLETE_RAW_NATIVE_AUDIT. All 8/8 calls are accounted for; 8/8 form observed pairs with the original Qwen3-4B V3 coordinates.

Direct: 0/4 source-correct. Oracle: 0/4 source-correct. Against matching 4B V3 calls: {'wins': 0, 'losses': 0, 'ties': 8, 'unknown': 0}.

Physical cost: 31938 prompt and 1028 completion tokens.

This is a model-alternative calibration. Architecture, parameter count, post-training, renderer, LoRA/prefix-cache settings, and model identity differ, so paired differences are not a pure capacity effect. The oracle condition supplies exact child reports but never the root answer.
