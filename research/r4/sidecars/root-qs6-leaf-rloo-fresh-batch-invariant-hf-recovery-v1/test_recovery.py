import json
from pathlib import Path

import score
import study


def test_precomputed_inputs_are_exact_v2_records_and_load_without_xgrammar():
    value=score.verify_only()
    assert value["status"]=="PRECOMPUTED_INPUTS_VERIFIED_WITHOUT_XGRAMMAR"
    assert value["records"]==48
    assert json.loads((study.ATTEMPT/"PREPARED.json").read_text())["optimizer_steps"]==0


def test_source_service_was_cleanly_released_before_recovery():
    terminal=json.loads((study.SOURCE_ATTEMPT/"OWNER_TERMINAL.json").read_text())
    stopped=json.loads((study.SOURCE_ATTEMPT/"service/SERVICE_STOPPED.json").read_text())
    assert terminal["released_before_hf"] is True and terminal["optimizer_steps"]==0
    assert stopped["all_owned_process_identities_exited"] is True and stopped["ports_free"] is True
