import json
from collections import Counter
from pathlib import Path

import id_study as s


EXPECTED_IDS = [
    "3ac2fa58dfc06f89e7462a306e2d0649aa5f3f9985ce7960511b141011709bc5",
    "3b301ffc5ba732b0489c5e0dcc078f24c0d7239e6211483fc6b5b86037859e3b",
    "97e665b69395db0e218ee37e1277aa44240f48edc603bd0f21e48461a06fa9a3",
    "fd9979513d01b0efd0af4dd96b813617f08cdc6e0bc2f5c97a518c185a0f6d44",
    "9e78771ad2f31a2a3ddfb7ca74dc36eaedf6c37b9991dc4ebe255ec5493d992e",
    "45770bdfbcc3a51ad692005cb42955db406db57c935494d1c0f4a9c9fb9d858a",
    "e65c03953d685eeb06409584a6c5356fbcdfff6a9b0abea5cd0405043dbe0331",
    "69c9e873fbff9591a10c329346e1349e1ab1f8120b4f4e5ea50a9ad2bacbdc6e",
    "425fd09f388d348e0d9cd638319daca38abb5210810dac23433393beb3df54f0",
    "6cb427de8586b2ef2d266b5c923b72848538a073cee523536521cde021023367",
    "b7d096caa7afc2e34d02dc2680dddcc77212eaede308b6882d3d1601eb7a8ebd",
    "ccf48c319a54f65fe53428aea31d53036855958f7a63e9dfde30fe0643e5ba09",
    "6125545e204cdce7063eeb5143deb9aa00010d81d53a75a6595fa92db5647a48",
    "37facfaaad6993c3f111f0e9a414efc97f0d38a4d73b3170ad724227d7a58da5",
    "83ab56338cdf864d4caa4e5a5f7afbc50d228bdddf7c8f06b00ff175e3e9f77f",
    "a7e862252950b2dcd237b31bf362e5a813907bd6af4f5e24721837ed82422dc8",
]


def test_selection_reproduces_literal_inventory_without_model_results():
    plan = json.loads((s.SOURCE / "inputs/FREE_PLAN.json").read_text())
    gold = json.loads((s.SOURCE / "inputs/HOST_GOLD.json").read_text())
    selected, receipt = s.select_panel(plan, gold)
    assert [row["id"] for row in selected] == EXPECTED_IDS
    assert receipt["fields_used"] == ["context_id", "id", "operator", "scope", "stratum", "gold_is_zero"]
    assert receipt["model_outcome_fields_used"] == []
    assert receipt["ordered_ids_sha256"] == "76e27abc804ee0ebaeffe8582b662a2cd930c55f544fe4759006756aad222282"
    assert Counter(row["stratum"] for row in selected) == {"root_new": 8, "exposed_repeatability": 8}
    assert sorted(Counter(row["operator"] for row in selected).values()) == [5, 5, 6]
    assert sorted(Counter(row["scope"] for row in selected).values()) == [5, 5, 6]
    assert sum(gold[row["context_id"]]["answers"][row["family"]] == 0 for row in selected) == 3
    assert len({row["context_id"] for row in selected}) == 12
