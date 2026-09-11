"""Exact protected72 collector for the authenticated recovered checkpoint2."""
import asyncio
import readout_study as study
import readout_common as common
import readout_native as native
with study.aliases({"terminal_study": study, "terminal_common": common, "terminal_native": native}):
    qualified = study.load("checkpoint2_terminal_collect", study.SOURCE / "terminal_collect.py")
def planned(phase):
    if phase != "readout-checkpoint2": raise ValueError("checkpoint2 readout phase only")
    return study.read(study.SOURCE / "inputs/PLANS.json")["readout"]
qualified.planned=planned; qualified.qualified.planned=planned
binding_for=qualified.binding_for; prepare_spec=qualified.prepare_spec
collect=qualified.collect; verify_spec=qualified.verify_spec; parse_args=qualified.parse_args
if __name__ == "__main__":
    args=parse_args(); raise SystemExit(asyncio.run(collect(args.spec,args.output,args.deadline)))
