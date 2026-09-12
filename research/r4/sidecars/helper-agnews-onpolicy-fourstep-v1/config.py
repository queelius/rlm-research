from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
REFERENCE = SIDE / "helper-hf-onpolicy-fourstep-v1"
V1 = SIDE / "helper-hf-onpolicy-v1"
V2 = SIDE / "helper-hf-onpolicy-v2"
BASE = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
CHILD = SIDE / "trec-leaf-sft-v1/outputs/attempt-001/checkpoint-0128"
CHILD_SHA = "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
SOURCE_BINDING = SIDE / "root-qs6-feedback-diagnostic-v1/outputs/attempt-001/service/BINDING.json"
TRAIN_PYTHON = Path(
    "/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/"
    "gpu/training/.venv/bin/python"
)
GRAMMAR_PYTHON = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
AG_VALUES = ("World", "Sports", "Business", "Sci/Tech")
GLOBAL_SEED = 202609120700
SAMPLER_SEED = 202609120701
PERMUTATION_SEED_BASE = 202609120800
UPDATES = 4
GROUPS = 32
BATCH = 4
DENOMINATOR = 128
LR = 1e-5
CLIP = 1.0
CAP = 4200
OUTER_CAP = 4400
