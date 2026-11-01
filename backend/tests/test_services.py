"""Unit tests for the individual analyzers and the merge / scoring logic."""

import json
import subprocess

import httpx
import pytest

from app.services import (
    ai_reviewer,
    analyzer,
    bandit_analyzer,
    pipeline,
    radon_analyzer,
    ruff_analyzer,
)
from app.services.errors import AnalyzerUnavailable


class FakeProcess:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def titles(issues):
    return [issue["title"] for issue in issues]


# --- AST analyzer -----------------------------------------------------------


def test_future_import_is_not_reported_as_unused():
    code = "from __future__ import annotations\n\ndef f(x: int) -> int:\n    return x\n"

    assert analyzer.analyze_python(code) == []


def test_names_in_dunder_all_count_as_used():
    assert analyzer.analyze_python("from os import path\n__all__ = ['path']\n") == []


def test_two_unused_imports_on_one_line_are_both_reported():
    issues = analyzer.analyze_python("import os, sys\n")

    assert titles(issues) == ["Unused import: os", "Unused import: sys"]


def test_mutable_default_after_positional_only_parameters():
    code = "def f(a, b=1, /, c=[]):\n    return a, b, c\n"

    assert titles(analyzer.analyze_python(code)) == ["Mutable default argument: c"]


def test_keyword_only_mutable_default():
    code = "def f(*, items={}):\n    return items\n"

    assert titles(analyzer.analyze_python(code)) == ["Mutable default argument: items"]


def test_syntax_error_is_marked_with_its_kind():
    issue = analyzer.analyze_python("def greet(:")[0]

    assert issue["kind"] == "syntax-error"
    assert issue["severity"] == "high"


def test_null_bytes_do_not_crash_the_analyzer():
    issue = analyzer.analyze_python("x = 1\x00")[0]

    assert issue["kind"] == "syntax-error"


# --- merge and score --------------------------------------------------------


def finding(line, kind, source="x", severity="low"):
    return {
        "severity": severity,
        "title": f"{source}:{kind}",
        "line": line,
        "suggestion": "",
        "source": source,
        "kind": kind,
    }


def test_merge_drops_duplicates_from_later_groups_only():
    first = [finding(1, "unused-import", "ast")]
    second = [finding(1, "unused-import", "ruff"), finding(2, "unused-import", "ruff")]

    merged = pipeline.merge_findings(first, second)

    assert [(item["source"], item["line"]) for item in merged] == [("ast", 1), ("ruff", 2)]


def test_merge_keeps_repeats_within_one_group_and_untagged_findings():
    group = [finding(1, "unused-import"), finding(1, "unused-import"), finding(1, None)]

    assert len(pipeline.merge_findings(group, [finding(1, None)])) == 4


def test_score_weights_ai_findings_at_half():
    assert pipeline.compute_score([finding(1, None, "ai", "high")]) == 85
    assert pipeline.compute_score([finding(1, None, "ruff", "high")]) == 70
    assert pipeline.compute_score([finding(1, None, "ai", "low")] * 2) == 95


def test_score_never_goes_below_zero():
    assert pipeline.compute_score([finding(1, None, "ruff", "high")] * 10) == 0


def test_static_analysis_stops_at_syntax_errors(monkeypatch):
    def must_not_run(code):
        raise AssertionError("must not run")

    monkeypatch.setattr(pipeline, "analyze_with_ruff", must_not_run)
    monkeypatch.setattr(pipeline, "analyze_with_bandit", must_not_run)
    monkeypatch.setattr(pipeline, "analyze_with_radon", must_not_run)

    findings, warnings, metrics = pipeline.run_static_analysis("def broken(:")

    assert findings[0]["kind"] == "syntax-error"
    assert warnings == [] and metrics is None


def test_static_analysis_collects_warnings_and_keeps_going(monkeypatch):
    def broken(code):
        raise AnalyzerUnavailable("Bandit is not installed.")

    monkeypatch.setattr(pipeline, "analyze_with_ruff", lambda code: [finding(3, "F841", "ruff")])
    monkeypatch.setattr(pipeline, "analyze_with_bandit", broken)
    monkeypatch.setattr(pipeline, "analyze_with_radon", lambda code: ([], {"functions": 0}))

    findings, warnings, metrics = pipeline.run_static_analysis("x = 1\n")

    assert [item["source"] for item in findings] == ["ruff"]
    assert warnings == ["Bandit is not installed."]
    assert metrics == {"functions": 0}


# --- Ruff -------------------------------------------------------------------


def test_ruff_output_is_translated(monkeypatch):
    output = [
        {
            "code": "F401",
            "message": "`os` imported but unused",
            "location": {"row": 1, "column": 8},
            "fix": {"message": "Remove unused import: `os`"},
        },
        {"code": "F821", "message": "Undefined name `x`", "location": {"row": 3, "column": 1}, "fix": None},
        {"code": "B007", "message": "Loop variable not used", "location": {"row": 5, "column": 1}},
        {"code": "E711", "message": "Comparison to None", "location": {"row": 7, "column": 1}},
    ]
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeProcess(json.dumps(output), "", 1))

    issues = ruff_analyzer.analyze_with_ruff("irrelevant")

    assert [issue["severity"] for issue in issues] == ["low", "high", "low", "medium"]
    assert [issue["kind"] for issue in issues] == ["unused-import", "F821", "B007", "E711"]
    assert issues[0]["suggestion"] == "Remove unused import: `os`"
    assert issues[1]["suggestion"].startswith("Review this finding")
    assert all(issue["source"] == "ruff" for issue in issues)


def test_ruff_is_called_without_project_config_or_cache(monkeypatch):
    seen = {}

    def fake_run(command, **kwargs):
        seen["command"] = command
        seen["input"] = kwargs["input"]
        return FakeProcess("[]", "", 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert ruff_analyzer.analyze_with_ruff("print(1)") == []
    assert "--isolated" in seen["command"] and "--no-cache" in seen["command"]
    assert seen["input"] == "print(1)"


@pytest.mark.parametrize(
    "process",
    [
        FakeProcess("", "No module named ruff", 1),
        FakeProcess("", "boom", 2),
        FakeProcess("not json", "", 0),
    ],
)
def test_ruff_problems_raise_analyzer_unavailable(monkeypatch, process):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: process)

    with pytest.raises(AnalyzerUnavailable):
        ruff_analyzer.analyze_with_ruff("x = 1")


def test_ruff_timeout_raises_analyzer_unavailable(monkeypatch):
    def slow(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="ruff", timeout=10)

    monkeypatch.setattr(subprocess, "run", slow)

    with pytest.raises(AnalyzerUnavailable):
        ruff_analyzer.analyze_with_ruff("x = 1")


# --- Bandit -----------------------------------------------------------------


def test_bandit_output_is_translated(monkeypatch):
    report = {
        "results": [
            {
                "test_id": "B110",
                "issue_text": "Try, Except, Pass detected.",
                "issue_severity": "LOW",
                "line_number": 5,
                "more_info": "https://bandit.readthedocs.io/b110",
                "issue_cwe": {"id": 703},
            },
            {
                "test_id": "B602",
                "issue_text": "subprocess call with shell=True",
                "issue_severity": "HIGH",
                "line_number": 3,
            },
        ]
    }
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeProcess(json.dumps(report), "", 0))

    issues = bandit_analyzer.analyze_with_bandit("irrelevant")

    assert [issue["severity"] for issue in issues] == ["low", "high"]
    assert [issue["kind"] for issue in issues] == ["empty-except", "B602"]
    assert "CWE-703" in issues[0]["suggestion"]
    assert issues[0]["title"] == "B110: Try, Except, Pass detected."
    assert all(issue["source"] == "bandit" for issue in issues)


def test_bandit_with_no_findings(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeProcess('{"results": []}', "", 0))

    assert bandit_analyzer.analyze_with_bandit("x = 1") == []


@pytest.mark.parametrize(
    "process",
    [
        FakeProcess("", "No module named bandit", 1),
        FakeProcess("", "crash", 2),
        FakeProcess("garbage", "", 0),
    ],
)
def test_bandit_problems_raise_analyzer_unavailable(monkeypatch, process):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: process)

    with pytest.raises(AnalyzerUnavailable):
        bandit_analyzer.analyze_with_bandit("x = 1")


# --- Radon ------------------------------------------------------------------


def test_radon_flags_complex_functions_and_reports_metrics():
    pytest.importorskip("radon")
    branches = "\n".join(f"    if x == {i}:\n        return {i}" for i in range(12))
    code = f"def big(x):\n{branches}\n    return -1\n\ndef small(x):\n    return x\n"

    issues, metrics = radon_analyzer.analyze_with_radon(code)

    assert any("big" in title for title in titles(issues))
    assert not any("small" in title for title in titles(issues))
    assert metrics["functions"] == 2
    assert metrics["max_complexity"] >= 12
    assert 0 <= metrics["maintainability_index"] <= 100


# --- AI reviewer ------------------------------------------------------------


class FakeResponse:
    def __init__(self, content=None, status_code=200):
        self._content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("failed", request=None, response=self)

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


def use_fake_post(monkeypatch, response=None, error=None, captured=None):
    def fake_post(url, **kwargs):
        if captured is not None:
            captured.update(url=url, **kwargs)
        if error:
            raise error
        return response

    monkeypatch.setenv("OPENAI_API_KEY", "sk-secret-test-key")
    monkeypatch.setattr(ai_reviewer.httpx, "post", fake_post)


def test_ai_requires_an_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert ai_reviewer.ai_configured() is False
    with pytest.raises(AnalyzerUnavailable):
        ai_reviewer.review_with_ai("x = 1", "python", [])


def test_ai_reply_is_parsed_and_sanitised(monkeypatch):
    issues = [
        {"severity": "critical", "title": "Bad severity", "line": 1, "suggestion": "Fix"},
        {"severity": "HIGH", "title": "Line out of range", "line": 999, "suggestion": "Fix"},
        {"severity": "low", "title": "Line is text", "line": "abc"},
        {"severity": "low", "title": "   ", "line": 1},  # no title: dropped
        "not an object",  # dropped
    ]
    reply = "Sure! Here is the review:\n```json\n" + json.dumps({"summary": "  OK  ", "issues": issues}) + "\n```"
    captured = {}
    use_fake_post(monkeypatch, FakeResponse(reply), captured=captured)

    result = ai_reviewer.review_with_ai(
        "a = 1\nb = 2\n", "python", [{"line": 1, "title": "Unused import: os"}]
    )

    assert result["summary"] == "OK"
    assert [(i["severity"], i["line"]) for i in result["issues"]] == [
        ("low", 1),
        ("high", 2),  # clamped to the last line
        ("low", 1),
    ]
    assert result["issues"][2]["suggestion"] == "No specific suggestion was provided."
    assert all(i["source"] == "ai" and i["kind"] is None for i in result["issues"])

    prompt = captured["json"]["messages"][1]["content"]
    assert "   1| a = 1" in prompt  # code is sent with line numbers
    assert "Unused import: os" in prompt  # known findings are not repeated
    assert captured["headers"]["Authorization"] == "Bearer sk-secret-test-key"
    assert captured["url"].endswith("/chat/completions")


def test_ai_issue_count_is_capped(monkeypatch):
    many = [{"severity": "low", "title": f"Issue {n}", "line": 1, "suggestion": "x"} for n in range(30)]
    use_fake_post(monkeypatch, FakeResponse(json.dumps({"summary": "s", "issues": many})))

    assert len(ai_reviewer.review_with_ai("x", "python", [])["issues"]) == ai_reviewer.MAX_AI_ISSUES


def test_ai_http_errors_never_leak_the_api_key(monkeypatch):
    use_fake_post(monkeypatch, FakeResponse(status_code=401))

    with pytest.raises(AnalyzerUnavailable) as raised:
        ai_reviewer.review_with_ai("x = 1", "python", [])

    assert "401" in str(raised.value)
    assert "sk-secret-test-key" not in str(raised.value)


def test_ai_network_errors_are_reported(monkeypatch):
    use_fake_post(monkeypatch, error=httpx.ConnectError("down"))

    with pytest.raises(AnalyzerUnavailable) as raised:
        ai_reviewer.review_with_ai("x = 1", "python", [])

    assert "could not reach" in str(raised.value)


@pytest.mark.parametrize("reply", ["not json at all", '["a list"]', "{broken"])
def test_ai_malformed_replies_are_reported(monkeypatch, reply):
    use_fake_post(monkeypatch, FakeResponse(reply))

    with pytest.raises(AnalyzerUnavailable) as raised:
        ai_reviewer.review_with_ai("x = 1", "python", [])

    assert "unexpected response" in str(raised.value)
