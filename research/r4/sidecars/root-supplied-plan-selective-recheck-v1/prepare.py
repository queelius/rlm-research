"""CPU-only preparation from the exact frozen supplied-plan ceiling."""
import copy
import hashlib
import importlib.util
import json
import math
import re
from pathlib import Path

from tokenizers import Tokenizer
import study as s

NAMESPACE = "root-supplied-plan-selective-recheck-v1"
TOKENIZER = Path("/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554/tokenizer.json")
OWNER_PIN = "0b6034ac31854444f1bb2101a13ca88f86ff5ef0faeaa3b342aeb5efbd6bffd7"
EXIT_PATH = s.SIDE.parent / "operations/2026-09-10-after-fresh-ordinal192-supplied-plan40/attempt-001/supplied_plan40/EXIT.json"
EXIT_PIN = "9160822abd3bf910025f8debe82b8fa4cb3e5fee470ecfcc7588486cfb34e8d3"
REPORT_PIN = "4ccb7a60082d0bc76e8de88f5500514efca7ba61cf4afd42931a6c7ec04f892e"
FINAL_PIN = "1a14d53b0542130a62bbf69ba4dbbae1eb1f69784239efc7fefc07e070c38104"
ADOPTION_PIN = "16c420e0bcbe5558a13ba3b76681d9af44ec8502e7daf65c8e21ff0cfb95f8f9"
LABELS = ("human being", "location", "abbreviation", "entity",
          "description and abstract concept", "numeric value")
MEMBER = re.compile(r'"(?P<id>r[0-9a-f]{15})"\s*:\s*"(?P<label>' +
                    "|".join(re.escape(x) for x in LABELS) + r')"')


def hash_rank(salt, episode_id, record_id):
    raw = json.dumps([salt, episode_id, record_id], separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def select_confidence(episode_id, confidences, budget):
    return [key for key, _ in sorted(confidences.items(),
            key=lambda item: (item[1], hash_rank(NAMESPACE + "/confidence-tie", episode_id, item[0])))[:budget]]


def select_uniform(episode_id, identifiers, budget):
    return sorted(identifiers, key=lambda key: hash_rank(NAMESPACE + "/uniform", episode_id, key))[:budget]


def load_ceiling_prepare():
    path = s.CEILING / "prepare.py"
    spec = importlib.util.spec_from_file_location("selective_recheck_ceiling_prepare", path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def admission():
    owner_path = s.CEILING / "outputs/attempt-001/OWNER_TERMINAL.json"
    report_path = s.CEILING_ANALYSIS / "REPORT.md"; final_path = s.CEILING_ANALYSIS / "FINAL_SEAL.json"
    adoption_path = s.CEILING_ANALYSIS / "MAIN_ADOPTION.json"
    pins = {owner_path: OWNER_PIN, EXIT_PATH: EXIT_PIN, report_path: REPORT_PIN,
            final_path: FINAL_PIN, adoption_path: ADOPTION_PIN}
    for path, pin in pins.items():
        if not path.exists() or s.sha(path) != pin: raise ValueError("ceiling pin mismatch: " + str(path))
    owner, outer = s.read(owner_path), s.read(EXIT_PATH)
    if not owner["complete"] or not owner["released"] or owner["active_unreleased_service"] is not None:
        raise ValueError("ceiling owner not cleanly released")
    if outer["exit_code"] != 0 or outer["timed_out"] or outer["gpu_pids_after_exit"]:
        raise ValueError("ceiling parent not clean")
    if outer["completion_markers"][str(owner_path)] != OWNER_PIN:
        raise ValueError("ceiling completion marker")
    return {str(path): pin for path, pin in pins.items()}


def baseline_and_confidence():
    admission(); tokenizer = Tokenizer.from_file(str(TOKENIZER)); plans = s.read(s.CEILING / "inputs/PLAN.json")
    baselines = {}; confidences = {}; call_pins = []
    for coordinate in plans:
        directory = s.CEILING / "outputs/attempt-001/rollout/calls" / coordinate["id"]
        response_path, result_path = directory / "RESPONSE.json", directory / "RESULT.json"
        response, result = s.read(response_path), s.read(result_path)
        if result["coordinate"] != coordinate or not result["score"]["available"] or not result["score"]["complete_map"]:
            raise ValueError("ceiling call unavailable/incomplete")
        choice = response["raw"]["choices"][0]; ids = choice["token_ids"]; logs = choice["logprobs"]["content"]
        if len(ids) != len(logs) or ids != [int(x["token"].split(":", 1)[1]) for x in logs]:
            raise ValueError("token/logprob mismatch")
        values = [x["logprob"] for x in logs]
        if not all(math.isfinite(x) for x in values): raise ValueError("nonfinite logprob")
        content = result["native"]["content"]; pieces = [tokenizer.decode([i], skip_special_tokens=True) for i in ids]
        if tokenizer.decode(ids, skip_special_tokens=True) != content or "".join(pieces) != content:
            raise ValueError("tokenizer reconstruction")
        spans=[]; position=0
        for index,piece in enumerate(pieces): spans.append((position,position+len(piece),index,piece));position+=len(piece)
        matches=list(MEMBER.finditer(content))
        if len(matches) != coordinate["n"]: raise ValueError("member inventory")
        episode=coordinate["context_id"]; baselines.setdefault(episode,{}).update(result["score"]["labels"]); confidences.setdefault(episode,{})
        for match in matches:
            start,stop=match.span("label"); overlap=[x for x in spans if x[0]<stop and x[1]>start]
            if not overlap or any(x[0]<start or x[1]>stop for x in overlap): raise ValueError("label boundary crossing")
            if "".join(x[3] for x in overlap) != match.group("label"): raise ValueError("label span decode")
            confidences[episode][match.group("id")]=sum(values[x[2]] for x in overlap)/len(overlap)
        call_pins.append({"coordinate_id":coordinate["id"],"response_sha256":s.sha(response_path),"result_sha256":s.sha(result_path)})
    if len(call_pins)!=40 or sum(len(x) for x in baselines.values())!=1280 or sum(len(x) for x in confidences.values())!=1280:
        raise ValueError("ceiling total inventory")
    return baselines,confidences,call_pins


def build(write=True):
    baselines,confidences,call_pins=baseline_and_confidence(); public=s.read(s.CEILING/"inputs/PUBLIC.json"); host=s.read(s.CEILING/"inputs/HOST_GOLD.json")
    episodes=sorted(public,key=lambda x:(x["cluster"],x["size"])); ceiling_prepare=load_ceiling_prepare()
    ceiling_requests=s.read(s.CEILING/"inputs/REQUESTS.json"); template=copy.deepcopy(next(iter(ceiling_requests.values())))
    tokenizer=Tokenizer.from_file(str(TOKENIZER)); decoded=tokenizer.decode(template["token_ids"],skip_special_tokens=False)
    marker="<|im_start|>user\n"; start=decoded.index(marker)+len(marker); end=decoded.index("<|im_end|>\n<|im_start|>assistant",start); prefix,suffix=decoded[:start],decoded[end:]
    plan=[];requests={};selections=[]
    for episode_index,episode in enumerate(episodes):
        episode_id=episode["id"]; records={r["id"]:r for r in episode["records"]}; budget=episode["size"]//4
        selected_by_arm={"confidence":select_confidence(episode_id,confidences[episode_id],budget),"uniform":select_uniform(episode_id,list(records),budget)}
        selections.append({"context_id":episode_id,"cluster":episode["cluster"],"size":episode["size"],"budget":budget,"confidence":selected_by_arm["confidence"],"uniform":selected_by_arm["uniform"],"overlap":sorted(set(selected_by_arm["confidence"])&set(selected_by_arm["uniform"]))})
        original_order={r["id"]:i for i,r in enumerate(episode["records"])}
        ceiling_coord=next(x for x in s.read(s.CEILING/"inputs/PLAN.json") if x["context_id"]==episode_id)
        for arm in ("confidence","uniform"):
            ordered=sorted(selected_by_arm[arm],key=original_order.get)
            for repack_index in range(0,len(ordered),32):
                ids=ordered[repack_index:repack_index+32]; repack=repack_index//32; seed=1002048101+2*episode_index+repack
                coordinate={k:ceiling_coord[k] for k in ("cluster","size","family","operator","target","target_b","scope","users","threshold")}
                coordinate.update(context_id=episode_id,selection_arm=arm,repack=repack,seed=seed,n=len(ids),ids=ids,model_policy="c32",root_model_calls=0,dispatch_order=len(plan))
                coordinate["id"]=s.digest([NAMESPACE,coordinate]); plan.append(coordinate)
                body=copy.deepcopy(template); body["token_ids"]=tokenizer.encode(prefix+ceiling_prepare.prompt([records[i] for i in ids])+suffix,add_special_tokens=False).ids;body["sampling_params"]["seed"]=seed
                body["sampling_params"]["structured_outputs"]["json"]={"type":"object","properties":{i:{"type":"string","enum":list(LABELS)} for i in sorted(ids)},"required":ids,"additionalProperties":False}
                if len(body["token_ids"])+2048>8192: raise ValueError("native context admission")
                requests[coordinate["id"]]=body
    value={"plan":plan,"requests":requests,"public":episodes,"host":host,"baselines":baselines,"confidences":confidences,"selections":selections,"call_pins":call_pins,"alignment":{"calls":40,"labels":1280,"excluded":0,"boundary_crossings":0}}
    if write:
        for name,data in (("PLAN.json",plan),("REQUESTS.json",requests),("PUBLIC.json",episodes),("HOST_GOLD.json",host),("BASELINE.json",baselines),("CONFIDENCE.json",confidences),("SELECTIONS.json",selections),("CEILING_CALL_PINS.json",call_pins)):
            s.write(s.ROOT/"inputs"/name,data)
        s.write(s.ROOT/"CPU_INPUT_NATIVE.json",value["alignment"]|{"planned_new_calls":24,"selected_labels_per_arm":320,"root_calls":0})
    return value


if __name__=="__main__": build(write=True)
