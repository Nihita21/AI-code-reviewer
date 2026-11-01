"""Runs the static analyzers, merges their findings and computes the score.

Deliberately free of FastAPI / Pydantic so it is easy to test on its own.
"""

from app.services.analyzer import analyze_python
from app.services.bandit_analyzer import analyze_with_bandit
from app.services.errors import AnalyzerUnavailable
from app.services.radon_analyzer import analyze_with_radon
from app.services.ruff_analyzer import analyze_with_ruff

SEVERITY_DEDUCTIONS = {"low": 5, "medium": 15, "high": 30}
# AI findings can be wrong, so they weigh half as much as deterministic tools.
SOURCE_WEIGHTS = {"ai": 0.5}


def merge_findings(*groups: list[dict]) -> list[dict]:
    """Combine findings, dropping ones an *earlier* group already reported.

    Two findings are the same when they share a line and a ``kind``. Findings
    inside a single group are never merged with each other, so e.g. two unused
    imports on one line are both kept.
    """
    merged: list[dict] = []
    seen: set[tuple[int, str]] = set()

    for group in groups:
        group_keys: set[tuple[int, str]] = set()
        for finding in group:
            kind = finding.get("kind")
            key = (finding["line"], kind) if kind else None
            if key is not None and key in seen:
                continue
            merged.append(finding)
            if key is not None:
                group_keys.add(key)
        seen |= group_keys

    return merged


def run_static_analysis(code: str) -> tuple[list[dict], list[str], dict | None]:
    """Return ``(findings, warnings, metrics)`` for Python source."""
    ast_findings = analyze_python(code)

    # Syntax errors make every other tool's output meaningless.
    if any(finding.get("kind") == "syntax-error" for finding in ast_findings):
        return ast_findings, [], None

    groups = [ast_findings]
    warnings: list[str] = []
    metrics = None

    try:
        groups.append(analyze_with_ruff(code))
    except AnalyzerUnavailable as error:
        warnings.append(str(error))

    try:
        groups.append(analyze_with_bandit(code))
    except AnalyzerUnavailable as error:
        warnings.append(str(error))

    try:
        radon_issues, metrics = analyze_with_radon(code)
        groups.append(radon_issues)
    except AnalyzerUnavailable as error:
        warnings.append(str(error))

    findings = merge_findings(*groups)
    findings.sort(key=lambda finding: finding["line"])  # stable: keeps tool order per line
    return findings, warnings, metrics


def compute_score(findings: list[dict]) -> int:
    penalty = sum(
        SEVERITY_DEDUCTIONS.get(finding["severity"], 0)
        * SOURCE_WEIGHTS.get(finding.get("source", ""), 1.0)
        for finding in findings
    )
    return max(0, round(100 - penalty))
