"""Style and correctness checks powered by Ruff."""

import json
import subprocess
import sys

from app.services.errors import AnalyzerUnavailable

# E4/E7/E9: import, statement and syntax errors   F: pyflakes   B: bugbear
# (security rules are left to Bandit to avoid reporting the same thing twice)
RULES = "E4,E7,E9,F,B"

# Ruff rule -> the shared "kind" used to de-duplicate against other analyzers.
KIND_BY_CODE = {
    "F401": "unused-import",
    "B006": "mutable-default",
}

HIGH_CODES = {"F821", "F822", "F823"}  # undefined names are real bugs
LOW_CODES = {"F401", "F841", "E401", "E402", "E731", "E741", "B007", "B904"}


def severity_for(code_id: str) -> str:
    if code_id in HIGH_CODES or code_id.startswith("E9"):
        return "high"
    if code_id in LOW_CODES:
        return "low"
    return "medium"


def analyze_with_ruff(code: str) -> list[dict]:
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--isolated",  # ignore any ruff config in the working directory
                "--no-cache",  # do not litter the working directory with .ruff_cache
                "--select",
                RULES,
                "--output-format",
                "json",
                "--stdin-filename",
                "submitted_code.py",
                "-",
            ],
            input=code,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise AnalyzerUnavailable(
            "Ruff timed out; style checks were skipped. Try a smaller submission."
        ) from error

    if "No module named" in (result.stderr or ""):
        raise AnalyzerUnavailable("Ruff is not installed; style checks were skipped.")

    # Ruff exits 0 (clean) or 1 (violations found); anything else is a failure.
    if result.returncode not in (0, 1):
        raise AnalyzerUnavailable("Ruff failed to run; style checks were skipped.")

    try:
        findings = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise AnalyzerUnavailable(
            "Ruff returned unreadable output; style checks were skipped."
        ) from error

    issues = []

    for finding in findings:
        code_id = finding.get("code") or ""
        message = finding.get("message", "Code issue detected")
        line = (finding.get("location") or {}).get("row", 1)
        fix = finding.get("fix")

        suggestion = (
            fix.get("message")
            if fix and fix.get("message")
            else "Review this finding and apply the appropriate correction."
        )

        issues.append(
            {
                "severity": severity_for(code_id),
                "title": f"{code_id}: {message}" if code_id else message,
                "line": max(1, line),
                "suggestion": suggestion,
                "source": "ruff",
                "kind": KIND_BY_CODE.get(code_id, code_id or None),
            }
        )

    return issues
