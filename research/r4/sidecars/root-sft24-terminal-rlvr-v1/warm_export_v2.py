"""V2 exporter: keep the qualified lazy collector import bound at call time."""
import warm_collect_v2 as collect
import warm_export as v1
import warm_native_v2 as native
import warm_study as study
import warm_verify_v2 as verification

verification.install()


def rebuild(attempt):
    with study.aliases({"qsr_collect": collect, "qsr_native": native}):
        return v1.rebuild(attempt)


def export_attempt(attempt, output):
    with study.aliases({"qsr_collect": collect, "qsr_native": native}):
        return v1.export_attempt(attempt, output)


def authenticate_export(output):
    with study.aliases({"qsr_collect": collect, "qsr_native": native}):
        return v1.authenticate_export(output)
