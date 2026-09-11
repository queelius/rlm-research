import pilot
import run


def test_exact_solver_requires_cross_record_join():
    rows = [["r1", "c01", "A"], ["r2", "c01", "B"], ["r3", "c02", "A"]]
    assert pilot.solve(rows) == ["c01"]
    assert pilot.solve(rows[:1]) == []


def test_worlds_preserve_records_and_engineer_lossy_information_loss():
    worlds = pilot.worlds()
    assert len(worlds) == 4
    answers = []
    for world in worlds:
        answers.append(tuple(pilot.solve(world["records"])))
        for name, chunks in world["partitions"].items():
            assert list(map(len, chunks)) == [16, 16, 16]
            assert sorted(sum(chunks, [])) == sorted(world["records"])
            if name == "cross":
                assert all(pilot.solve(chunk) == [] for chunk in chunks)
            else:
                assert sorted(sum([pilot.solve(chunk) for chunk in chunks], [])) == list(
                    answers[-1]
                )
    assert list(map(len, answers)) == [3, 5, 7, 9]
    assert len(set(answers)) == 4


def test_bad_extraction_is_null_not_empty_and_wrong_facts_are_not_repaired():
    chunk = [["r1", "c01", "A"], ["r2", "c01", "B"]]
    assert pilot.extract("not json", chunk)["rows"] is None
    assert pilot.extract("[]", chunk)["rows"] == []
    result = pilot.extract('[["r1","c01","B"]]', chunk)
    assert result["rows"] == [["r1", "c01", "B"]]
    assert result["correct_triples"] == 0
    assert result["recall"] == 0


def test_answer_scoring_keeps_empty_answer_separate_from_invalid():
    assert pilot.score("[]", ["c01"], ["c01"])["correct"] is False
    assert pilot.score("broken", [], ["c01"])["answer"] is None
    assert pilot.score('["c01", "c01"]', ["c01"], ["c01"])["valid"] is False
    assert pilot.score('["c01"]', ["c01"], ["c01"])["correct"] is True


def test_projections_share_extraction_and_charge_acquisition():
    calls = [
        {
            "id": "extract0",
            "prompt_tokens": 10,
            "output_tokens": 20,
            "seconds": 3,
            "content": '[["r1","c01","A"],["r2","c01","B"]]',
        }
    ]
    chunk = [["r1", "c01", "A"], ["r2", "c01", "B"]]
    full, lossy = pilot.projections(calls, [chunk])
    assert full["acquisition_call_ids"] == lossy["acquisition_call_ids"] == ["extract0"]
    assert full["reports"][0]["evidence"] == chunk
    assert lossy["reports"][0]["local_winners"] == ["c01"]
    assert pilot.cost(calls) == {"calls": 1, "prompt_tokens": 10, "output_tokens": 20, "seconds": 3}


def test_freeze_has_eight_coordinates_eleven_actual_calls_each_and_original_input():
    plan = pilot.plan()
    assert len(plan) == 8
    for coordinate in plan:
        requests = pilot.static_requests(coordinate)
        assert len(requests) == 8
        reports = {"reports": [], "acquisition_call_ids": []}
        root = pilot.parent_request(coordinate, "full", reports)
        for row in coordinate["records"]:
            assert pilot.render_record(row) in root["messages"][1]["content"]
    assert len({(p["world_id"], p["partition"]) for p in plan}) == 8


def test_collector_reuses_actual_extraction_and_retains_eighty_eight_calls(tmp_path, monkeypatch):
    def sample(model, tokenizer, request, output, deadline):
        content = "[]"
        record = {
            "id": request["id"],
            "content": content,
            "request": request,
            "prompt_tokens": 10,
            "output_tokens": 2,
            "seconds": 1,
        }
        run.save(output / "calls" / (request["id"] + ".json"), record)
        return record

    monkeypatch.setattr(run, "sample", sample)
    coordinates = pilot.plan()
    for coordinate in coordinates:
        coordinate["static_requests"] = pilot.static_requests(coordinate)
    run.collect(None, None, coordinates, tmp_path, 99999)
    assert len(list((tmp_path / "calls").glob("*.json"))) == 88
    episodes = [run.read(p) for p in (tmp_path / "episodes").glob("*.json")]
    assert len(episodes) == 8
    for episode in episodes:
        full, lossy = episode["endpoints"]["full"], episode["endpoints"]["lossy"]
        assert full["acquisition_call_ids"] == lossy["acquisition_call_ids"]
        assert full["cost"]["calls"] == lossy["cost"]["calls"] == 4
        assert full["cost"]["output_tokens"] == 8
        assert full["report_implied_answer"] == []


def test_failed_call_remains_unavailable_and_unknown_cost():
    coordinate = pilot.plan()[0]
    final = {
        "id": coordinate["id"] + "-parent-full",
        "content": None,
        "prompt_tokens": 10,
        "output_tokens": None,
        "seconds": 2,
    }
    episode = pilot.episode(coordinate, [final])
    assert episode["endpoints"]["full"]["score"] is None
    assert episode["endpoints"]["full"]["cost"]["output_tokens"] is None


def test_native_tokenizer_returns_serializable_token_sequence():
    from transformers import AutoTokenizer

    path = "/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
    request = pilot.static_requests(pilot.plan()[0])[0]
    ids = run.prompt_ids(tokenizer, request["messages"])
    assert isinstance(ids, list) and all(isinstance(token, int) for token in ids)
    assert tokenizer.decode(ids).endswith("<|im_start|>assistant\n")
