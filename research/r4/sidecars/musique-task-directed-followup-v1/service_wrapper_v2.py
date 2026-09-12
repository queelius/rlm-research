"""Preserve V1 service/config; change only the actual CLI entrypoint registry seam."""
import argparse
import ast
from pathlib import Path

import study


def build(run_dir):
    previous = study.load('report_followup_service_v1_reuse', study.ROOT / 'service_wrapper.py')
    previous.__file__ = str(Path(__file__).resolve())
    module = previous.build(run_dir)
    base = study.load('report_followup_base_text_v2', study.BASE / 'service_base_batch_v2.py')
    assert study.sha(base.SOURCE) == base.SOURCE_SHA
    text = base.SOURCE.read_text()
    replacements = {
        '    environment = adapt_environment(helper._server_environment(helper._environment(), 0))':
        '    environment = adapt_environment(helper._server_environment(helper._environment(), 0))\n    environment["VLLM_BATCH_INVARIANT"] = "1"',
        'process = subprocess.Popen(':
        'process = attested_launch(args.run_dir / "ENGINE_ENV_ATTESTATION.json",',
        'command = [str(helper.PRIME_ENV / "bin/inference"), "@", str(args.run_dir / "inference.json")]':
        'command = [sys.executable, str(Path(__file__).with_name("engine_entry_v2.py")), "@", str(args.run_dir / "inference.json")]'}
    for before, after in replacements.items():
        assert text.count(before) == 1, 'exact original launcher seam changed'
        text = text.replace(before, after)
    main = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    exec(compile(ast.fix_missing_locations(ast.Module(body=[main], type_ignores=[])), str(base.SOURCE) + ':actual-registry-v2', 'exec'), module.__dict__)
    return module


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--binding', type=Path, required=True)
    args = parser.parse_args(); build(args.run_dir).main()
