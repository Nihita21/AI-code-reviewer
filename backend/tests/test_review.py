"""End-to-end tests of the HTTP API."""

import importlib.util

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import pipeline
from app.services.errors import AnalyzerUnavailable

client = TestClient(app)

BUGGY_CODE = (
    "import os\n"
    "def greet(names=[]):\n"
    "    try:\n"
    "        print(names)\n"
    "    except Exception:\n"
    "        pass\n"
)
CLEAN_CODE = "def greet(name):\n    return f'Hello, {name}'\n"


def post_review(code, language="python", **extra):
    return client.post("/review", json={"language": language, "code": code, **extra})


def fake_ai(monkeypatch, result=None, error=None):
    """Pretend the AI is configured and make it return `result` (or raise `error`)."""
    monkeypatch.setattr("app.api.review.ai_configured", lambda: True)

    def fake_review(code, language, known_issues):
        if error:
            raise error
        return result

    monkeypatch.setattr("app.api.review.review_with_ai", fake_review)


AI_RESULT = {
    "summary": "Looks fine overall.",
    "issues": [
        {
            "severity": "high",
            "title": "SQL injection risk",
            "line": 2,
            "suggestion": "Use parameterised queries.",
            "source": "ai",
            "kind": None,
        }
    ],
}


# --- basic behaviour --------------------------------------------------------


def test_review_detects_real_issues(no_tools):
    response = post_review(BUGGY_CODE)

    assert response.status_code == 200

    result = response.json()
    titles = [issue["title"] for issue in result["issues"]]

    assert result["score"] == 65  # low 5 + medium 15 + medium 15
    assert "Unused import: os" in titles
    assert "Mutable default argument: names" in titles
    assert "Empty exception handler" in titles
    assert all(issue["source"] == "ast" for issue in result["issues"])
    assert result["summary"] == "Found 3 issue(s): 2 medium, 1 low."


def test_review_clean_code(no_tools):
    response = post_review(CLEAN_CODE)

    assert response.status_code == 200
    assert response.json()["score"] == 100
    assert response.json()["issues"] == []


def test_review_syntax_error_skips_other_tools(monkeypatch):
    def must_not_run(code):
        raise AssertionError("analyzers must not run on code that does not parse")

    monkeypatch.setattr(pipeline, "analyze_with_ruff", must_not_run)
    monkeypatch.setattr(pipeline, "analyze_with_bandit", must_not_run)
    monkeypatch.setattr(pipeline, "analyze_with_radon", must_not_run)

    response = post_review("def greet(:")

    assert response.status_code == 200
    assert response.json()["issues"][0]["severity"] == "high"


# --- input validation -------------------------------------------------------


def test_review_rejects_empty_code():
    assert post_review("   ").status_code == 400


def test_review_rejects_unknown_language():
    assert post_review("print(1)", language="cobol").status_code == 400


def test_review_rejects_non_python_without_ai():
    response = post_review("console.log('Hello')", language="javascript")

    assert response.status_code == 400
    assert "AI review" in response.json()["detail"]


def test_review_rejects_oversized_code(monkeypatch):
    monkeypatch.setenv("MAX_CODE_CHARS", "10")

    assert post_review("x" * 11).status_code == 413


# --- analyzers: dedupe and failure handling ---------------------------------


def test_duplicate_findings_from_other_tools_are_merged(monkeypatch):
    ruff_duplicate = {
        "severity": "medium",
        "title": "F401: `os` imported but unused",
        "line": 1,
        "suggestion": "Remove unused import",
        "source": "ruff",
        "kind": "unused-import",
    }
    monkeypatch.setattr(pipeline, "analyze_with_ruff", lambda code: [ruff_duplicate])
    monkeypatch.setattr(pipeline, "analyze_with_bandit", lambda code: [])
    monkeypatch.setattr(pipeline, "analyze_with_radon", lambda code: ([], None))

    issues = post_review("import os\n").json()["issues"]

    assert len(issues) == 1
    assert issues[0]["source"] == "ast"


def test_tool_failure_is_a_warning_not_a_penalty(monkeypatch, no_tools):
    def broken(code):
        raise AnalyzerUnavailable("Ruff is not installed; style checks were skipped.")

    monkeypatch.setattr(pipeline, "analyze_with_ruff", broken)

    result = post_review(CLEAN_CODE).json()

    assert result["score"] == 100
    assert result["issues"] == []
    assert result["warnings"] == ["Ruff is not installed; style checks were skipped."]


# --- AI review --------------------------------------------------------------


def test_ai_findings_are_merged_and_weighted(monkeypatch, no_tools):
    fake_ai(monkeypatch, AI_RESULT)

    result = post_review(CLEAN_CODE).json()

    assert result["ai_summary"] == "Looks fine overall."
    assert [issue["source"] for issue in result["issues"]] == ["ai"]
    assert result["score"] == 85  # a high AI finding costs 30 * 0.5


def test_ai_can_review_non_python_languages(monkeypatch):
    fake_ai(monkeypatch, AI_RESULT)

    response = post_review("function f() {}", language="javascript")

    assert response.status_code == 200
    assert response.json()["metrics"] is None
    assert response.json()["issues"][0]["source"] == "ai"


def test_ai_failure_on_python_is_only_a_warning(monkeypatch, no_tools):
    fake_ai(monkeypatch, error=AnalyzerUnavailable("AI review failed: HTTP 429."))

    result = post_review(CLEAN_CODE).json()

    assert result["score"] == 100
    assert result["ai_summary"] is None
    assert "AI review failed: HTTP 429." in result["warnings"]


def test_ai_failure_on_other_languages_is_an_error(monkeypatch):
    fake_ai(monkeypatch, error=AnalyzerUnavailable("AI review failed: HTTP 500."))

    assert post_review("int main() {}", language="cpp").status_code == 502


def test_use_ai_false_is_respected(monkeypatch, no_tools):
    fake_ai(monkeypatch, error=AssertionError("AI must not be called"))

    result = post_review(CLEAN_CODE, use_ai=False)

    assert result.status_code == 200
    assert post_review("x", language="javascript", use_ai=False).status_code == 400


# --- capabilities -----------------------------------------------------------


def test_capabilities_without_ai():
    body = client.get("/capabilities").json()

    assert body["ai_enabled"] is False
    assert body["ai_model"] is None
    python = next(item for item in body["languages"] if item["id"] == "python")
    assert python["static_analysis"] is True
    assert all(item["ai_review"] is False for item in body["languages"])


def test_capabilities_with_ai(monkeypatch):
    monkeypatch.setattr("app.api.review.ai_configured", lambda: True)

    body = client.get("/capabilities").json()

    assert body["ai_enabled"] is True
    assert body["ai_model"]
    assert all(item["ai_review"] is True for item in body["languages"])


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


# --- the real tools (skipped when they are not installed) --------------------


@pytest.mark.skipif(
    not all(importlib.util.find_spec(name) for name in ("ruff", "bandit", "radon")),
    reason="ruff, bandit and radon must all be installed",
)
def test_real_tools_report_each_problem_once():
    result = post_review(BUGGY_CODE).json()
    titles = [issue["title"].lower() for issue in result["issues"]]

    assert result["warnings"] == []
    assert result["metrics"] is not None
    assert sum("unused" in title for title in titles) == 1
    assert sum("mutable" in title for title in titles) == 1
