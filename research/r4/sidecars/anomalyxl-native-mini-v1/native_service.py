"""Owned loopback Prime native service; exact cached Qwen3.5 model, no adapters/API shim."""

import json
import os
import signal
import socket
import subprocess
import time
from urllib.request import urlopen

import mini as m

TEMPLATE = (
    m.STORE
    / "sidecars/root-qs6-fixed-helper-top20-batch-invariant-v1"
    / "outputs/attempt-003/service/service/inference.json"
)
ENV_SOURCE = m.STORE / "sidecars/strict-rlm-temperature-adherence-v1/scripts/launch.py"
DRIVER = "/export/software/system/nvidia/580.126.20/lib"
PORTS = (18681, 18691, 18701)


def configuration(directory):
    value = m.read(TEMPLATE)
    value["output_dir"] = str(directory / "launcher")
    value["server"].update(host="127.0.0.1", port=PORTS[0])
    value["backend_port"] = PORTS[2]
    engine = value["vllm"]
    for key in ("lora_dtype", "max_cpu_loras", "max_lora_rank", "max_loras", "api_key"):
        engine.pop(key, None)
    engine.update(
        model=str(m.MODEL),
        enable_lora=False,
        enforce_eager=True,
        max_num_seqs=1,
        data_parallel_rpc_port=PORTS[1],
        max_model_len=m.CONTEXT,
        reasoning_parser=None,
        tool_call_parser=None,
        dtype="bfloat16",
    )
    return value


def environment(directory):
    helper = m.load("anomalyxl_existing_native_environment", ENV_SOURCE)
    value = m.scrub(helper._environment())
    libs = [
        p
        for p in value.get("LD_LIBRARY_PATH", "").split(":")
        if p and "/nvidia-driver-" not in p and "/export/software/system/nvidia/" not in p
    ]
    value["LD_LIBRARY_PATH"] = ":".join([DRIVER, *libs])
    value["CUDA_VISIBLE_DEVICES"] = os.environ["CUDA_VISIBLE_DEVICES"]
    value["HF_HUB_OFFLINE"] = "1"
    value["HF_HOME"] = "/project/alex_phd/research-cache/huggingface-runtime"
    value["VLLM_BATCH_INVARIANT"] = "0"
    value["PYTHONPATH"] = ""
    for key, suffix in (
        ("VLLM_CACHE_ROOT", "vllm"),
        ("VLLM_CONFIG_ROOT", "vllm-config"),
        ("XDG_CACHE_HOME", "xdg-cache"),
        ("XDG_CONFIG_HOME", "xdg-config"),
        ("TORCHINDUCTOR_CACHE_DIR", "torch"),
        ("TRITON_CACHE_DIR", "triton"),
        ("HUMMING_CACHE_DIR", "humming"),
        ("HUMMING_TMP_DIR", "humming-tmp"),
    ):
        value[key] = str(directory / "cache" / suffix)
    return value


def release(process, directory):
    actions = []
    for sig, duration in ((signal.SIGTERM, 10), (signal.SIGKILL, 5)):
        try:
            os.killpg(process.pid, sig)
            actions.append(sig.name)
        except ProcessLookupError:
            break
        try:
            process.wait(timeout=duration)
        except subprocess.TimeoutExpired:
            continue
        # Parent exit does not prove engine descendants exited: KILL the same owned group.
    m.write(
        directory / "RELEASE.json",
        {
            "owned_process_group": process.pid,
            "signals": actions,
            "parent_exit_code": process.poll(),
            "completed_epoch": time.time(),
        },
    )


def start(directory, deadline):
    from prime_rl.configs.inference import InferenceConfig

    for port in PORTS:
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                raise ValueError("reserved native port occupied")
    directory.mkdir(parents=True, exist_ok=False)
    config = configuration(directory)
    InferenceConfig.model_validate(config)
    m.write(directory / "inference.json", config)
    command = [str(m.NATIVE.parent / "inference"), "@", str(directory / "inference.json")]
    env = environment(directory)
    with (directory / "inference.log").open("x") as log:
        process = subprocess.Popen(
            command, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True
        )
    m.write(
        directory / "SERVER_START.json",
        {
            "pid": process.pid,
            "command": command,
            "model": str(m.MODEL),
            "config_sha256": m.sha(directory / "inference.json"),
            "source_sha256": m.sha(__file__),
            "gpu": env["CUDA_VISIBLE_DEVICES"],
            "batch_invariant": env["VLLM_BATCH_INVARIANT"],
            "driver_library": DRIVER,
            "api_authentication": "loopback-only; no API key configured or persisted",
            "credential_environment_scrubbed": True,
            "started_epoch": time.time(),
        },
    )
    base = f"http://127.0.0.1:{PORTS[0]}"
    try:
        while time.time() < deadline:
            if process.poll() is not None:
                raise RuntimeError("native model server exited before qualification")
            try:
                with urlopen(base + "/v1/models", timeout=2) as response:
                    models = json.load(response)
                if str(m.MODEL) in {row["id"] for row in models["data"]}:
                    m.write(directory / "MODELS.json", models)
                    return process, base + "/inference/v1/generate"
            except (OSError, ValueError, KeyError):
                pass
            time.sleep(1)
        raise TimeoutError("native exact-model startup deadline")
    except BaseException:
        release(process, directory)
        raise
