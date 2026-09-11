"""Pinned complete-window exporter with warm namespace inputs."""
import warm_collect as collect
import warm_metrics as metrics
import warm_native as native
import warm_study as study

SOURCE = study.QSR / "qsr_export.py"
SOURCE_SHA = "3b0e58ef886720cf2efd578ace0629d04b54463532c0531a443dd7fac3447796"
with study.aliases({"qsr_study": study, "qsr_native": native,
                    "qsr_metrics": metrics, "qsr_collect": collect}):
    qualified = study.load("warm_qualified_qsr_export", SOURCE, SOURCE_SHA)

rebuild = qualified.rebuild
export_attempt = qualified.export_attempt
authenticate_export = qualified.authenticate_export

