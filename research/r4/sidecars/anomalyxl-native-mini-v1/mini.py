"""Small native AnomalyXL experiment: immutable data, exact scorer and current executor."""

import contextlib
import functools
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STORE = ROOT.parents[1]
REPO = Path("/project/alex_phd/repos/rlm")
OFFICIAL = Path("/project/alex_phd/research-cache/repos/TimeRLM")
DATA_ROOT = Path("/project/alex_phd/research-cache/datasets/anomalyxl-31fcd847-release-seed42")
DATA = DATA_ROOT / "anomalyxl-precise/data.parquet"
MODEL = Path(
    "/project/alex_phd/research-cache/models/Qwen--Qwen3.5-4B--851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"
)
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
SCORER = OFFICIAL / "sft/tslm/src/datasets/anomaly_xl/scoring.py"
ATTEMPT = ROOT / "outputs/attempt-001"
CAP, EPISODE_CAP, CONTEXT, TOTAL_OUTPUT = 1100, 45, 8192, 2048
SEED = 202609121431


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")
    tmp.replace(path)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=1)
def tokenizer():
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(MODEL, local_files_only=True)


def select_metadata():
    import pyarrow.parquet as pq

    rows = [
        {"row_index": index, **r}
        for index, r in enumerate(
            pq.read_table(
                DATA, columns=["id", "category", "length", "n_channels", "seed"]
            ).to_pylist()
        )
    ]
    selected = []
    for category in sorted({r["category"] for r in rows}):
        candidates = [r for r in rows if r["category"] == category]
        shortest = min(r["length"] for r in candidates)
        eligible = [r for r in candidates if r["length"] == shortest]
        selected.extend(
            sorted(
                eligible,
                key=lambda r: hashlib.sha256(
                    f"anomalyxl-native-mini-v1|202609121430|{category}|{r['id']}".encode()
                ).hexdigest(),
            )[:2]
        )
    return selected


def episode_schedule(panel):
    return [
        {"episode_id": f"{index:02d}-{arm}", "row_id": r["id"], "arm": arm, "panel_index": index}
        for index, r in enumerate(panel)
        for arm in (("direct", "python") if index % 2 == 0 else ("python", "direct"))
    ]


def output_allowance(generated, final):
    remaining = TOTAL_OUTPUT - generated
    if remaining <= 0:
        raise ValueError("aggregate output budget exhausted")
    return remaining if final else min(512, remaining)


def body(messages, maximum):
    tok = tokenizer()
    if type(maximum) is not int or not 1 <= maximum <= TOTAL_OUTPUT:
        raise ValueError("invalid requested output budget")
    ids = tok.apply_chat_template(
        messages,
        tokenize=True,
        return_dict=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    if not isinstance(ids, list) or len(ids) + maximum > CONTEXT:
        raise ValueError("actual native prompt plus output exceeds context")
    model_eos = read(MODEL / "config.json")["text_config"]["eos_token_id"]
    stops = sorted({tok.eos_token_id, tok.convert_tokens_to_ids("<|im_end|>"), model_eos})
    if any(type(i) is not int or i < 0 for i in stops):
        raise ValueError("invalid tokenizer-derived stop IDs")
    return {
        "model": str(MODEL),
        "token_ids": ids,
        "sampling_params": {
            "temperature": 0.0,
            "top_p": 1.0,
            "seed": SEED,
            "max_tokens": maximum,
            "stop_token_ids": stops,
        },
    }


def decode(request, raw):
    if (
        raw.get("model") != str(MODEL)
        or not raw.get("request_id")
        or len(raw.get("choices", [])) != 1
    ):
        raise ValueError("native response model or identity differs")
    choice, usage = raw["choices"][0], raw["usage"]
    ids = choice["token_ids"]
    if not all(type(i) is int and i >= 0 for i in ids):
        raise ValueError("invalid native output tokens")
    if any(
        type(usage[k]) is not int or usage[k] < 0 for k in ("prompt_tokens", "completion_tokens")
    ):
        raise ValueError("invalid native physical tokens")
    if usage["prompt_tokens"] != len(request["token_ids"]) or usage["completion_tokens"] != len(
        ids
    ):
        raise ValueError("native physical tokens differ")
    if len(ids) > request["sampling_params"]["max_tokens"]:
        raise ValueError("native exceeded requested token cap")
    if choice["finish_reason"] not in ("stop", "length"):
        raise ValueError("unexpected native finish")
    return {
        "text": tokenizer().decode(ids, skip_special_tokens=True),
        "completion_ids": ids,
        "request_id": raw["request_id"],
        "finish_reason": choice["finish_reason"],
        "prompt_tokens": usage["prompt_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "cached_tokens": usage.get("prompt_tokens_details", {}).get("cached_tokens"),
    }


def scrub(environment):
    return {
        k: v
        for k, v in environment.items()
        if not any(
            term in k.upper()
            for term in (
                "KEY",
                "TOKEN",
                "SECRET",
                "CREDENTIAL",
                "PASSWORD",
                "AUTH",
                "COOKIE",
                "PROXY",
            )
        )
    }


def observation(result):
    """Bound the complete rendered model observation, retaining the full result on disk."""
    raw = json.dumps(result, separators=(",", ":"), ensure_ascii=False)
    marker = "\n[observation truncated by host]"
    text = raw if len(raw) <= 2048 else raw[: 2048 - len(marker)] + marker
    return text, {
        "original_characters": len(raw),
        "rendered_characters": len(text),
        "truncated": len(raw) > 2048,
    }


@contextlib.contextmanager
def executor(workspace):
    sys.path.insert(0, str(REPO / "src"))
    from rlm.executor import IPythonExecutor

    worker = IPythonExecutor(
        request={"input": "Public numerical analysis only"},
        allow_recursion=False,
        working_directory=workspace,
        startup_timeout=10,
        max_output_chars=2048,
    )
    before = dict(os.environ)
    try:
        os.environ.clear()
        os.environ.update(scrub(before))
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        worker.start()
    finally:
        os.environ.clear()
        os.environ.update(before)
    try:
        yield worker
    finally:
        worker.close()


def execute_cell(worker, text, timeout):
    from rlm.protocol import PythonCellControllerProtocol

    response = {
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": text}],
            }
        ]
    }
    code = PythonCellControllerProtocol().parse(response).code

    def disabled(*_args):
        raise RuntimeError("host calls and final submissions disabled in inspection phase")

    result = worker.execute(code, action_handler=disabled, timeout=timeout)
    if result.submission is not None:
        raise ValueError("inspection cannot submit final answer")
    return result.to_dict()


@functools.lru_cache(maxsize=1)
def official_scorer():
    return load("mini_fully_reviewed_official_scorer", SCORER)


def score(answer, gold):
    result = official_scorer().score_precise(answer, gold)
    try:
        parsed = json.loads(answer, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        strict = isinstance(parsed, dict)
    except (ValueError, TypeError):
        strict = False
    return {**result, "strict_whole_json": strict}


def direct_prompt(series, question):
    def render(stride):
        lines = [
            "Analyze the uniformly sampled time series below. Pairs are (original_index,value). "
            "Return one JSON object matching the question, without prose."
        ]
        for channel, values in series.items():
            indices = list(range(0, len(values), stride))
            if indices[-1] != len(values) - 1:
                indices.append(len(values) - 1)
            lines.append(channel + ": " + " ".join(f"({i},{values[i]})" for i in indices))
        return "\n".join(lines) + "\nQuestion: " + question

    length = len(next(iter(series.values())))
    lo, hi = 1, length
    tok = tokenizer()

    def fits(text):
        return (
            len(
                tok.apply_chat_template(
                    [{"role": "user", "content": text}],
                    tokenize=True,
                    return_dict=False,
                    add_generation_prompt=True,
                    enable_thinking=False,
                )
            )
            <= 6144
        )

    if not fits(render(hi)):
        raise ValueError("direct minimal representation exceeds context")
    while lo < hi:
        middle = (lo + hi) // 2
        if fits(render(middle)):
            hi = middle
        else:
            lo = middle + 1
    prompt = render(lo)
    kept = len(set(range(0, length, lo)) | {length - 1})
    return prompt, {
        "stride": lo,
        "retained_points_per_channel": kept,
        "original_points_per_channel": length,
        "retained_fraction": kept / length,
    }


def prepare():
    import pyarrow.parquet as pq

    panel = select_metadata()
    selected = pq.read_table(
        DATA,
        filters=[("id", "in", [r["id"] for r in panel])],
        columns=["id", "question", "answer", "channel_names", "channel_values"],
    ).to_pylist()
    by_id = {r["id"]: r for r in selected}
    gold = {}
    for meta in panel:
        if Path(meta["id"]).name != meta["id"] or meta["id"] in (".", ".."):
            raise ValueError("unsafe public case identifier")
        row = by_id[meta["id"]]
        series = {
            name: [round(float(x), 3) for x in values]
            for name, values in zip(row["channel_names"], row["channel_values"], strict=True)
        }
        public = {"series": series, "question": row["question"]}
        prompt, view = direct_prompt(series, row["question"])
        body([{"role": "user", "content": prompt}], 2048)
        write(ROOT / "inputs/public" / f"{meta['id']}.json", public)
        write(ROOT / "inputs/direct" / f"{meta['id']}.json", {"prompt": prompt, "view": view})
        gold[meta["id"]] = row["answer"]
    write(ROOT / "inputs/PANEL.json", panel)
    write(ROOT / "inputs/HOST_GOLD.json", gold)
    write(ROOT / "inputs/SCHEDULE.json", episode_schedule(panel))
    return panel


def verify():
    ready = read(ROOT / "READY.json")
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("sealed source changed: " + path)
    return ready
