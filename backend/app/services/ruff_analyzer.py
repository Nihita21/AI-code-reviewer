
import json
import subprocess
import sys


def analyze_with_ruff(code: str) -> list[dict]:
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--stdin-filename",
                "submitted_code.py",
                "--output-format",
                "json",
                "-",
            ],
            input=code,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return [
            {
                "severity": "medium",
                "title": "Ruff analysis timed out",
                "line": 1,
                "suggestion": "Try reviewing a smaller code submission.",
            }
        ]

    if result.returncode not in (0, 1):
        return [
            {
                "severity": "medium",
                "title": "Ruff analysis failed",
                "line": 1,
                "suggestion": "Check the Ruff installation and backend logs.",
            }
        ]

    try:
        findings = json.loads(result.stdout)
    except json.JSONDecodeError:
        return [
            {
                "severity": "medium",
                "title": "Invalid Ruff output",
                "line": 1,
                "suggestion": "Check the Ruff version and backend logs.",
            }
        ]

    issues = []

    for finding in findings:
        code_id = finding.get("code") or ""
        message = finding.get("message", "Code issue detected")
        line = finding.get("location", {}).get("row", 1)
        fix = finding.get("fix")

        if code_id.startswith("E") or code_id.startswith("F"):
            severity = "medium"
        elif code_id.startswith("S"):
            severity = "high"
        else:
            severity = "low"

        suggestion = (
            fix.get("message")
            if fix and fix.get("message")
            else "Review this finding and apply the appropriate correction."
        )

        issues.append(
            {
                "severity": severity,
                "title": f"{code_id}: {message}",
                "line": line,
                "suggestion": suggestion,
            }
        )

    return issues
