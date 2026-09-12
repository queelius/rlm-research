"""Analyze exactly once if attempt003 is terminal; never poll partial output."""

import json

import analyze


if not (analyze.ATTEMPT / "OWNER_TERMINAL.json").exists():
    print(json.dumps({"status": "PENDING", "attempt": str(analyze.ATTEMPT), "polled": False}))
else:
    result = analyze.run()
    print(
        json.dumps(
            {
                "status": "ANALYZED",
                "report": str(analyze.OUTCOME / "REPORT.json"),
                "report_sha256": analyze.sha(analyze.OUTCOME / "REPORT.json"),
                "authenticated_calls": result["authenticated_calls"],
                "available_endpoints": result["available_endpoints"],
            },
            sort_keys=True,
        )
    )
