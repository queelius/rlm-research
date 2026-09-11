"""Pinned qualified endpoint and exact start/rl_last paired metrics."""
import sys
import types

import terminal_study as study

SOURCE = study.QSR / "qsr_metrics.py"
PIN = "4e57eebac3404f1404221bbaea4d66a7406e82b777e19d28198d1cf841fb5bbd"
study.check(SOURCE, PIN)
text = SOURCE.read_text()
for before, after, count in (("'unchanged'", "'start'", 4),
                             ("'trained'", "'rl_last'", 3),
                             ("import qsr_native as n", "import terminal_native as n", 1)):
    if text.count(before) != count:
        raise ValueError("qualified metrics arm seam changed: " + before)
    text = text.replace(before, after)
qualified = types.ModuleType("terminal_qualified_qsr_metrics")
qualified.__file__ = str(SOURCE)
sys.modules[qualified.__name__] = qualified
with study.aliases({"qsr_study": study}):
    exec(compile(text, str(SOURCE) + ":terminal-arms", "exec"), qualified.__dict__)

_qualified_score_message = qualified.score_message


def score_message(reply, content, tools, finish, gold):
    """Treat a physically authenticated empty final as observed zero, never NULL."""
    if reply is None and content == "" and not tools and finish in ("stop", "length"):
        reply = ""
    return _qualified_score_message(reply, content, tools, finish, gold)


qualified.score_message = score_message

endpoint = qualified.endpoint
paired_summary = qualified.paired_summary
