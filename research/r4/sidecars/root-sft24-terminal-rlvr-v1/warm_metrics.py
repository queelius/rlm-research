"""Pinned QSR endpoint and paired metrics in the warm namespace."""
import warm_study as study

SOURCE = study.QSR / "qsr_metrics.py"
SOURCE_SHA = "4e57eebac3404f1404221bbaea4d66a7406e82b777e19d28198d1cf841fb5bbd"
with study.aliases({"qsr_study": study}):
    qualified = study.load("warm_qualified_qsr_metrics", SOURCE, SOURCE_SHA)

endpoint = qualified.endpoint
paired_summary = qualified.paired_summary

