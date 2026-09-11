"""Additive SDK response typing fix; model requests and frozen samples unchanged."""

from __future__ import annotations

import argparse
import asyncio
import time
from pathlib import Path
from typing import Any


def fix_models_typing(client):
    original_get = client.get

    async def get(path, **kwargs):
        if path == "/models" and kwargs.get("cast_to") is dict:
            kwargs["cast_to"] = dict[str, Any]
        return await original_get(path, **kwargs)

    client.get = get


def main():
    import driver_converted as converted

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    original_make = converted.v1.make_client

    def make(endpoint):
        client = original_make(endpoint)
        fix_models_typing(client.client)
        return client

    output = args.output.resolve()
    record = {
        "schema": "native-direct-model-list-response-typing-v1",
        "started": time.time(),
        "output": str(output),
        "endpoint": str(args.endpoint.resolve()),
        "original_converted_spec_sha256": converted.v1.file_hash(converted.SPEC),
        "launcher_sha256": converted.v1.file_hash(Path(__file__)),
        "regression_test_sha256": converted.v1.file_hash(
            Path(__file__).with_name("test_live_models.py")
        ),
        "change": "Only /models SDK response cast_to=dict becomes dict[str,Any]",
        "model_request_or_sampler_change": False,
        "prior_failure": "converted-attempt-001 failed in /models SDK parsing before inference",
    }
    converted.v1.write_once(output.with_name(output.name + ".launcher.json"), record)
    converted.v1.make_client = make
    try:
        asyncio.run(converted.run(args.endpoint.resolve(), output))
    finally:
        converted.v1.make_client = original_make


if __name__ == "__main__":
    main()
