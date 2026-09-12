"""Construct generic, public-input-only procedural demonstrations for short MRCR."""

from __future__ import annotations

import builtins
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
DATA = SIDE / "openai-mrcr-short-root-data-v1"
SHORT = SIDE / "openai-mrcr-short32-base-calibration-v1"
V7 = SIDE / "mrcr-v3-root-procedure-calibration-v1"
MODEL = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
QUERY = re.compile(
    r"^Prepend (\S+) to the (\d+)(?:st|nd|rd|th) \(1 indexed\) "
    r"(.+?) about (.+?)\. Do not include any other text in your response\.?$"
)
EOS = 151645


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_query(question: str) -> dict:
    match = QUERY.fullmatch(question.strip())
    if match is None:
        raise ValueError("public question is outside the frozen generic grammar")
    marker, ordinal, kind, topic = match.groups()
    request_text = f"write a {kind} about {topic}"
    return {
        "marker": marker,
        "ordinal": int(ordinal),
        "kind": kind,
        "topic": topic,
        "request_text": request_text,
    }


def authored_code(criteria: dict) -> str:
    """Emit one generic program parameterized only by constants visible in the question."""
    return "\n".join(
        [
            "import json",
            'messages = json.load(open("/context.json", encoding="utf-8"))',
            f"request_text = {criteria['request_text']!r}",
            f"ordinal = {criteria['ordinal']!r}",
            f"marker = {criteria['marker']!r}",
            "matches = []",
            "for index, message in enumerate(messages[:-1]):",
            '    if message.get("role") != "user":',
            "        continue",
            '    if message.get("content", "").strip().casefold() != request_text.casefold():',
            "        continue",
            "    following = messages[index + 1]",
            '    if following.get("role") != "assistant":',
            '        raise ValueError("matching user record is not followed by assistant")',
            '    matches.append(following["content"])',
            "if len(matches) < ordinal:",
            '    raise ValueError("requested ordinal is unavailable")',
            "print(marker + matches[ordinal - 1])",
        ]
    )


def construct(question: str, messages: list[dict]) -> dict:
    criteria = parse_query(question)
    matching = []
    for index, message in enumerate(messages[:-1]):
        if (
            message.get("role") == "user"
            and message.get("content", "").strip().casefold()
            == criteria["request_text"].casefold()
        ):
            if messages[index + 1].get("role") != "assistant":
                raise ValueError("matching user record is not followed by assistant")
            matching.append(index)
    ordinal = criteria["ordinal"]
    if len(matching) < ordinal:
        raise ValueError("requested ordinal is unavailable")
    selected = matching[ordinal - 1] + 1
    answer = criteria["marker"] + messages[selected]["content"]
    return {
        "criteria": criteria,
        "matching_user_indices": matching,
        "all_matching_user_indices": list(matching),
        "selected_message_index": selected,
        "answer": answer,
        "authored_code": authored_code(criteria),
    }


def execute_authored_code(code: str, context_bytes: bytes) -> str:
    """CPU audit helper: execute the exact authored program against supplied context bytes."""
    original_open = builtins.open

    def scoped_open(path, mode="r", *args, **kwargs):
        if str(path) == "/context.json" and mode == "r":
            return io.StringIO(context_bytes.decode(kwargs.get("encoding") or "utf-8"))
        return original_open(path, mode, *args, **kwargs)

    namespace = dict(builtins.__dict__)
    namespace["open"] = scoped_open
    output = io.StringIO()
    with redirect_stdout(output):
        exec(code, {"__builtins__": namespace})
    return output.getvalue()


def _load_short_study():
    spec = importlib.util.spec_from_file_location("procedural_sft_short_source", SHORT / "study.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _system_and_ordered_tools() -> tuple[dict, list[dict]]:
    # The V7 checkpoint is an authentic request from the same harness. Its JSON was key-sorted on
    # disk, so reconstruct the provider's semantic insertion order before rendering.
    raw = json.loads(
        (V7 / "outputs/attempt-007/science/native-calls/0000-start.json").read_text()
    )["body"]
    ordered = []
    for saved in raw["tools"]:
        function = saved["function"]
        parameters = function["parameters"]
        properties = {
            key: {"type": value["type"], "description": value["description"]}
            for key, value in parameters["properties"].items()
        }
        ordered.append(
            {
                "type": "function",
                "function": {
                    "name": function["name"],
                    "description": function["description"],
                    "parameters": {
                        "type": parameters["type"],
                        "properties": properties,
                        "required": parameters["required"],
                    },
                },
            }
        )
    return raw["messages"][0], ordered


def tool_action(code: str) -> str:
    return "<tool_call>\n" + json.dumps(
        {"name": "ipython", "arguments": {"code": code}}
    ) + "\n</tool_call>"


def render_training_rows() -> dict:
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer

    short = _load_short_study()
    system, tools = _system_and_ordered_tools()
    renderer = create_renderer(
        load_tokenizer(str(MODEL)), Qwen3RendererConfig(enable_thinking=True)
    )
    tokenizer = renderer._tokenizer
    sources = json.loads((DATA / "MODEL_INPUTS_V2.json").read_text())["train"]
    episodes = []
    for source in sources:
        question = Path(source["final_question_path"]).read_text()
        payload = Path(source["prompt_json_path"]).read_bytes()
        result = construct(question, json.loads(payload))
        if execute_authored_code(result["authored_code"], payload) != result["answer"] + "\n":
            raise ValueError("authored program does not reproduce constructed answer")
        user = {
            "role": "user",
            "content": short.root_prompt(question, source["prompt_json_bytes"]),
        }
        initial = renderer.render(
            [system, user], tools=tools, add_generation_prompt=True
        ).token_ids
        action_target = tokenizer.encode(
            tool_action(result["authored_code"]), add_special_tokens=False
        ) + [EOS]
        assistant = {
            "role": "assistant",
            "tool_calls": [
                {
                    "arguments": json.dumps({"code": result["authored_code"]}),
                    "id": "call_0",
                    "name": "ipython",
                    "type": "function",
                }
            ],
        }
        observation = {
            "content": result["answer"] + "\n",
            "name": "ipython",
            "role": "tool",
            "tool_call_id": "call_0",
        }
        terminal_prefix = renderer.render(
            [system, user, assistant, observation], tools=tools, add_generation_prompt=True
        ).token_ids
        terminal_target = tokenizer.encode(result["answer"], add_special_tokens=False) + [EOS]

        def turn(kind: str, prefix: list[int], target: list[int]) -> dict:
            if len(prefix) + len(target) > 8192:
                raise ValueError("teacher turn exceeds the current native context contract")
            return {
                "id": source["id"] + ":" + kind,
                "kind": kind,
                "input_ids": prefix + target,
                "prompt_length": len(prefix),
                "labels": [-100] * len(prefix) + target,
                "loss_mask": [0] * len(prefix) + [1] * len(target),
                "target_tokens": len(target),
            }

        episodes.append(
            {
                "episode_id": source["id"],
                "source": {
                    "record_id": source["id"],
                    "source_row_sha256": source["source_row_sha256"],
                    "prompt_json_sha256": source["prompt_json_sha256"],
                    "question_sha256": sha(Path(source["final_question_path"])),
                },
                "teacher": {
                    "criteria": result["criteria"],
                    "matching_user_indices": result["matching_user_indices"],
                    "selected_message_index": result["selected_message_index"],
                    "authored_code": result["authored_code"],
                    "answer_sha256": hashlib.sha256(result["answer"].encode()).hexdigest(),
                    "answer_chars": len(result["answer"]),
                },
                "turns": [
                    turn("root_action", initial, action_target),
                    turn("terminal", terminal_prefix, terminal_target),
                ],
            }
        )
    return {
        "schema": "openai-mrcr-procedural-sft-teacher-corpus-v1",
        "episodes": episodes,
        "train_records": len(episodes),
        "teacher_failures": [],
        "heldout_query_files_read": 0,
        "heldout_context_files_read": 0,
        "heldout_gold_records_used": 0,
        "system_source": str(
            V7 / "outputs/attempt-007/science/native-calls/0000-start.json"
        ),
        "renderer": {"name": "qwen3", "enable_thinking": True, "model": str(MODEL)},
    }
