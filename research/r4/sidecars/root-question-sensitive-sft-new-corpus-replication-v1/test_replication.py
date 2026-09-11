import importlib
from pathlib import Path
import time


def test_selection_is_new_fixed_128_and_builds_exact_72():
    prepare = importlib.import_module("rep_prepare")
    pool, proof, used_seeds, public_ids, native_ids = prepare.inventory()
    built = prepare.build(pool)
    assert proof["named_manifest_count"] >= 74
    assert len(built["selected"]) == 128
    assert not set(built["selected"]) & set(proof["current_excluded_group_ids"])
    assert len(built["values"]["PUBLIC.json"]) == 8
    assert {len(c["records"]) for c in built["values"]["PUBLIC.json"]} == {16}
    assert len(built["values"]["TRAIN_PLAN.json"]) == 72
    assert len({r["seed"] for r in built["values"]["TRAIN_PLAN.json"]}) == 72
    assert not ({r["seed"] for r in built["values"]["TRAIN_PLAN.json"]} | {prepare.s.SEED}) & used_seeds
    assert not {r["id"] for c in built["values"]["PUBLIC.json"] for r in c["records"]} & public_ids
    assert not {c["native_context_id"] for c in built["values"]["PUBLIC.json"]} & native_ids


def test_budget_and_readout_are_exact():
    owner = importlib.import_module("rep_owner")
    assert owner.BUDGET == {
        "outer": 4500,
        "owned": 4470,
        "work": 4320,
        "capture": 1500,
        "training": 1200,
        "readout": 1500,
        "finalize": 120,
        "cleanup": 150,
        "margin": 30,
    }
    plan = owner.s.read(owner.s.METADATA / "inputs/FREE_PLAN.json")
    rows = owner.inventory(owner.s.ATTEMPT)
    assert len(plan) == len(rows) == 72
    assert {r["coordinate"]["id"] for r in rows} == {r["id"] for r in plan}
    assert {r["policy"] for r in rows} == {"new_corpus_sft6"}


def test_corpus_rejects_missing_or_nonactual_teacher(tmp_path, monkeypatch):
    study = importlib.import_module("rep_study")
    monkeypatch.setattr(study, "ATTEMPT", tmp_path)
    try:
        study.corpus()
    except (FileNotFoundError, ValueError):
        pass
    else:
        raise AssertionError("incomplete corpus admitted")


def test_readout_facade_renders_exact_frozen_metadata_prefix():
    facade = importlib.import_module("rep_readout_study")
    row = facade.read(facade.ROOT / "inputs/FREE_PLAN.json")[0]
    context = next(c for c in facade.read(facade.ROOT / "inputs/PUBLIC.json") if c["id"] == row["context_id"])
    prompt = facade.read(facade.ROOT / "inputs/PROMPTS_ACCURATE.json")[row["id"]]["prompt"]
    task = facade.stack().native.task(context, prompt, 0, row["id"])
    assert facade.qnative().first_prefix(task) == facade.read(facade.ROOT / "inputs/PROMPTS_ACCURATE.json")[row["id"]]["token_ids"]


def test_collector_cli_is_exact_72(monkeypatch):
    collect = importlib.import_module("qs_collect")
    args = collect.parse_args(["--mode", "capture", "--plan", "TRAIN_PLAN.json", "--binding", "/b",
                               "--endpoint", "/e", "--output", "/o", "--stop", "72", "--deadline", "9"])
    assert (args.mode, args.start, args.stop) == ("capture", 0, 72)


def test_actual_owner_composes_capture_train_and_metadata72(tmp_path, monkeypatch):
    owner = importlib.import_module("rep_owner"); collect = importlib.import_module("qs_collect")
    output = tmp_path / "attempt"; calls = []
    class Suite:
        def start_service(self, stage, binding, deadline): calls.append(("start", stage.name, binding))
        def release_service(self, stage): calls.append(("release", stage.name))
        def command(self, stage, label, argv, cap, deadline):
            assert 0 < cap <= deadline - time.time() + 1
            calls.append(("command", label, argv))
            if label in ("capture72", "metadata72"):
                args = collect.parse_args(argv[2:])
                assert (args.start, args.stop) == (0, 72)
                assert Path(argv[1]).name == ("rep_collect.py" if label == "capture72" else "rep_readout.py")
            else:
                assert label == "six-full72-updates" and Path(argv[0]) == owner.s.TRAIN
                assert Path(argv[1]).name == "rep_train.py"
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "CPU_INTERCEPT_ONLY")
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "CPU_FIXTURE_NOT_SECRET")
    monkeypatch.setattr(owner.s, "ATTEMPT", output); monkeypatch.setattr(owner.s, "verify", lambda: {"identity": "CPU"})
    monkeypatch.setattr(owner.s, "runtime", lambda: None); monkeypatch.setattr(owner.s, "corpus", lambda: [])
    monkeypatch.setattr(owner, "qualified", type("Q", (), {"dependencies": staticmethod(lambda: Suite())}))
    monkeypatch.setattr(owner.b, "binding", lambda arm: {"arm": arm})
    monkeypatch.setattr(owner.b, "selected", lambda arm: {"step": 6})
    result = owner.execute(output)
    assert [c[1] for c in calls if c[0] == "command"] == ["capture72", "six-full72-updates", "metadata72"]
    assert result["released"] and not result["complete"]
