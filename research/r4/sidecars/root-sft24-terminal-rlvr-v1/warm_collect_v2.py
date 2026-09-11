"""V2 collector authenticates the frozen first prefix when V1 task_hash is absent."""
import warm_collect as v1
import warm_verify_v2 as verification

verification.install()

source = v1.qualified.composed_collect_source()
before = "if task.hash != tasks[row['task_name']]['task_hash']:\n                raise ValueError('actual frozen task identity differs before call')"
after = "if n.first_prefix(task) != tasks[row['task_name']]['first_prompt_token_ids']:\n                raise ValueError('actual frozen first native prefix differs before call')"
if source.count(before) != 1:
    raise ValueError("qualified task-identity seam changed")
namespace = dict(v1.qualified.impl.__dict__)
exec(compile(source.replace(before, after), str(v1.SOURCE) + ":warm-collector-v2", "exec"), namespace)

planned = v1.planned
binding_for = v1.binding_for
validate_descriptor = v1.validate_descriptor
prepare_spec = v1.prepare_spec
dispatch = v1.dispatch
verify_spec = v1.verify_spec
parse_args = v1.parse_args
collect = namespace["collect"]


if __name__ == "__main__":
    import asyncio
    args = parse_args()
    raise SystemExit(asyncio.run(collect(args.spec, args.output, args.deadline)))
