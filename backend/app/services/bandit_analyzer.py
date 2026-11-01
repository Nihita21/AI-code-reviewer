"""Security checks powered by Bandit."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from app.services.errors import AnalyzerUnavailable

SEVERITIES = {"HIGH": "high", "MEDIUM": "medium", "LOW": "low"}

# Bandit test id -> shared "kind" used to de-duplicate against other analyzers.
KIND_BY_TEST_ID = {
    "B110": "empty-except",  # try / except / pass
}


def analyze_with_bandit(code: str) -> list[dict]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "submitted_code.py"
        path.write_text(code, encoding="utf-8")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "bandit",
                    "--format",
                    "json",
                    "--quiet",
                    "--exit-zero",  # findings are not an error; only crashes should be
                    "--skip",
                    "B101",  # `assert` is not worth flagging in a review tool
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise AnalyzerUnavailable(
                "Bandit timed out; the security scan was skipped."
            ) from error

    if "No module named" in (result.stderr or ""):
        raise AnalyzerUnavailable("Bandit is not installed; the security scan was skipped.")

    if result.returncode != 0:
        raise AnalyzerUnavailable("Bandit failed to run; the security scan was skipped.")

    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise AnalyzerUnavailable(
            "Bandit returned unreadable output; the security scan was skipped."
        ) from error

    issues = []

    for finding in report.get("results", []):
        test_id = finding.get("test_id") or ""
        text = finding.get("issue_text", "Potential security issue")
        cwe = (finding.get("issue_cwe") or {}).get("id")
        more_info = finding.get("more_info")

        suggestion = "Review this potential security issue"
        if cwe:
            suggestion += f" (CWE-{cwe})"
        suggestion += f". Details: {more_info}" if more_info else "."

        issues.append(
            {
                "severity": SEVERITIES.get(finding.get("issue_severity", ""), "low"),
                "title": f"{test_id}: {text}" if test_id else text,
                "line": max(1, finding.get("line_number", 1)),
                "suggestion": suggestion,
                "source": "bandit",
                "kind": KIND_BY_TEST_ID.get(test_id, test_id or None),
            }
        )

    return issues
