"""Experiment-local terminal-strip ablation; reasoning/tool semantics stay frozen."""

from contextlib import contextmanager
import hashlib
import inspect
from pathlib import Path

CONDITION = "terminal-strip-disabled"
SOURCE_SHA256 = {
    "/project/alex_phd/research-cache/repos/prime-rl/deps/renderers/renderers/parsing.py": "4b54e8c82d81e0f00eb3f1b107a79892e2eff45d7b8a8c9ae40ebe4112ba87f4",
    "/project/alex_phd/research-cache/repos/prime-rl/deps/renderers/renderers/qwen3.py": "75c4d4a96c7fe930b0fe80d83df894133e1319b364b033cf97fbea2d84e8e146",
    "/project/alex_phd/research-cache/repos/prime-rl/deps/verifiers/verifiers/v1/acp/__init__.py": "c143d95580458c9b8e9c822860e34116e034e00d4325ffdd3b2298dd0c0adfb4",
    "/project/alex_phd/research-cache/repos/prime-rl/deps/verifiers/verifiers/v1/harnesses/rlm/harness.py": "7256f1efe1d0b44c8488e62edc93c41fa2da1fae95620bc6de4dea2e7d517bfc"
}

def qualify():
    for raw, expected in SOURCE_SHA256.items():
        if hashlib.sha256(Path(raw).read_bytes()).hexdigest() != expected:
            raise ValueError("terminal-strip source changed: " + raw)
    return {"condition": CONDITION, "source_sha256": dict(SOURCE_SHA256),
            "hook_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "parser_change": "final content=text.strip() -> content=text",
            "root_storage_change": "successful ACPTurn.reply preserved exactly after original metadata callback",
            "reasoning_newline_rule_unchanged": True, "tool_parsing_unchanged": True,
            "general_lossless_parser": False, "gold_dependent_repair": False}


@contextmanager
def installed():
    from renderers import parsing, qwen3
    from verifiers.v1.harnesses.rlm.harness import RLMHarness

    contract = qualify()
    original_parse = qwen3.parse_qwen3
    original_turn = RLMHarness.acp_turn_result
    if original_parse is not parsing.parse_qwen3:
        raise ValueError("another Qwen3 parser intervention is already installed")
    source = inspect.getsource(original_parse)
    if source.count("content=text.strip(),") != 1:
        raise ValueError("frozen terminal parser boundary differs")
    # Compile only the hash-pinned trusted dependency function, never model output.
    namespace = dict(original_parse.__globals__)
    exec(compile(source.replace("content=text.strip(),", "content=text,"),
                 str(Path(__file__)) + ":terminal-strip-disabled", "exec"), namespace)
    replacement = namespace["parse_qwen3"]

    def turn_result(harness, trace, result):
        original_turn(harness, trace, result)
        trace.root_reply = result.reply

    qwen3.parse_qwen3 = replacement
    RLMHarness.acp_turn_result = turn_result
    try:
        yield contract
    finally:
        qwen3.parse_qwen3 = original_parse
        RLMHarness.acp_turn_result = original_turn

