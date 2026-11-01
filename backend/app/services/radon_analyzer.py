"""Complexity and maintainability metrics powered by Radon."""

from app.services.errors import AnalyzerUnavailable

# Radon ranks complexity A (1-5) .. F (41+); rank C starts above 10.
COMPLEXITY_WARN = 10
COMPLEXITY_HIGH = 20
# Maintainability index below 10 is rank C ("extremely low").
MAINTAINABILITY_WARN = 10


def analyze_with_radon(code: str) -> tuple[list[dict], dict]:
    """Return ``(issues, metrics)``."""
    try:
        from radon.complexity import cc_visit
        from radon.metrics import mi_visit
        from radon.raw import analyze as raw_analyze
        from radon.visitors import Function
    except ImportError as error:
        raise AnalyzerUnavailable(
            "Radon is not installed; complexity metrics were skipped."
        ) from error

    try:
        blocks = cc_visit(code)
        maintainability = float(mi_visit(code, multi=True))
        raw = raw_analyze(code)
    except Exception as error:  # radon can raise many things on odd input
        raise AnalyzerUnavailable(
            "Radon could not analyze this code; complexity metrics were skipped."
        ) from error

    functions = [block for block in blocks if isinstance(block, Function)]
    scores = [block.complexity for block in functions]

    issues = []

    for block in functions:
        if block.complexity <= COMPLEXITY_WARN:
            continue
        issues.append(
            {
                "severity": "high" if block.complexity > COMPLEXITY_HIGH else "medium",
                "title": (
                    f"High cyclomatic complexity: {block.name} ({block.complexity})"
                ),
                "line": max(1, block.lineno),
                "suggestion": (
                    "Split this function into smaller helpers and simplify "
                    "nested conditions to make it easier to test and read."
                ),
                "source": "radon",
                "kind": None,
            }
        )

    if maintainability < MAINTAINABILITY_WARN:
        issues.append(
            {
                "severity": "medium",
                "title": f"Low maintainability index ({maintainability:.1f})",
                "line": 1,
                "suggestion": (
                    "Break the code into smaller, well-named functions and add "
                    "comments where the intent is not obvious."
                ),
                "source": "radon",
                "kind": None,
            }
        )

    metrics = {
        "lines_of_code": raw.sloc,
        "functions": len(functions),
        "average_complexity": round(sum(scores) / len(scores), 2) if scores else 0.0,
        "max_complexity": max(scores) if scores else 0,
        "maintainability_index": round(maintainability, 1),
    }

    return issues, metrics
