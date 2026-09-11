"""Unchanged qualified QSR TIS/PPO trainer under fresh SFT24 RL cursor."""
import warm_common as common
import warm_study as study

SOURCE = study.QSR / "qsr_train.py"
SOURCE_SHA = "a5064c270f80e157945775accde4e57cd9c5f9e82d1bb17862a118786cb13878"
with study.aliases({"qsr_study": study, "qsr_common": common}):
    qualified = study.load("warm_qualified_qsr_train", SOURCE, SOURCE_SHA)

check_members = qualified.check_members
authenticate_group = qualified.authenticate_group
parse_args = qualified.parse_args
impl = qualified.impl


if __name__ == "__main__":
    import json
    import traceback
    import uuid
    args = parse_args()
    try:
        print(json.dumps(impl.train(args), sort_keys=True, allow_nan=False))
    except BaseException as error:
        if args.output is not None:
            study.write(args.output.parent / ("TRAIN_FAILURE-" + uuid.uuid4().hex + ".json"),
                        {"type": type(error).__name__, "error": str(error),
                         "traceback": traceback.format_exc(), "checkpoint_preserved": True})
        raise
