import asyncio

import qualify_transport


def test_one_real_prepared_free_row_reaches_native_scalar_and_bounded_bundle(tmp_path):
    result = asyncio.run(qualify_transport.qualify(tmp_path / "qualification"))
    assert result["status"] == "PASS"
    assert result["actual_model_calls"] == 0
    assert result["gpu_calls"] == 0
    assert result["mode"] == "free"
    assert result["prepared_size"] == 256
    assert result["root_calls"] == 2
    assert result["child_calls"] == 1
    assert result["root_reply"].startswith("Answer: ")
    assert result["strict_scalar_correct"] is True
    assert result["setup_files"] == [
        ".observation_view.json",
        "batch_contract.py",
        "context.txt",
        "query.txt",
        "records.json",
    ]
    assert result["view_cap_bytes"] == 4096
    assert result["bounded_view_clipped"] is True
    assert result["bounded_view_raw_bytes"] > 4096

