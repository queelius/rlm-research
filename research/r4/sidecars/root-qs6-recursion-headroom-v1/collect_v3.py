"""Final collector facade: cached frozen first-prefix lookup on every native module seam."""

import collect_v2 as v2


qualified = v2.qualified
terminal_study = v2.terminal_study
activate = v2.activate
task_tables = v2.task_tables
make_task = v2.make_task
first_prefix = v2.first_prefix
_read = v2._read
planned = v2.planned
prepare_spec = v2.prepare_spec
verify_spec = v2.verify_spec
binding = v2.binding
binding_for = v2.binding_for
phase = v2.phase
export_attempt = v2.export_attempt

for module in (qualified.native, qualified.qualified.n, qualified.qualified.impl.n):
    module.first_prefix = first_prefix

collect = qualified.collect


if __name__ == "__main__":
    import asyncio
    args = qualified.parse_args()
    raise SystemExit(asyncio.run(collect(args.spec, args.output, args.deadline)))
