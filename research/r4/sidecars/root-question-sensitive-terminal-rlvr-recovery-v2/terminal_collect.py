"""Exact fixed8/readout72 adapter around the qualified QSR collector."""
import terminal_common as common
import terminal_native as native
import terminal_study as study

SOURCE = study.QSR / "qsr_collect.py"
PIN = "8f2901a03657dc6c417260e4350340202a9a3ee738ac8453ce48a3c628654dd7"
with study.aliases({"qsr_study": study, "qsr_common": common, "qsr_native": native}):
    qualified = study.load("terminal_qualified_qsr_collect", SOURCE, PIN)


def planned(phase):
    plans = study.read(study.ROOT / "inputs/PLANS.json")
    if phase in ("readout-start", "readout-rl_last"):
        return plans["readout"]
    if phase.startswith("window-") and phase[7:].isdigit() and 1 <= int(phase[7:]) <= 8:
        return plans["training"][str(int(phase[7:]))]
    raise ValueError("not fixed8 training or fixed protected readout")


qualified.planned = planned
qualified.impl.planned = planned
binding_for = qualified.binding_for
validate_descriptor = qualified.validate_descriptor
prepare_spec = qualified.prepare_spec
dispatch = qualified.dispatch
collect = qualified.collect
verify_spec = qualified.verify_spec
parse_args = qualified.parse_args


if __name__ == "__main__":
    import asyncio
    args = parse_args()
    raise SystemExit(asyncio.run(collect(args.spec, args.output, args.deadline)))
