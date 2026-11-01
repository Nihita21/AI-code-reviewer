import pytest

from app.services import pipeline


@pytest.fixture(autouse=True)
def never_call_openai(monkeypatch):
    """No test may reach the real AI provider, even if a developer has a .env file."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)


@pytest.fixture
def no_tools(monkeypatch):
    """Replace Ruff/Bandit/Radon so API tests are fast and fully deterministic."""
    monkeypatch.setattr(pipeline, "analyze_with_ruff", lambda code: [])
    monkeypatch.setattr(pipeline, "analyze_with_bandit", lambda code: [])
    monkeypatch.setattr(pipeline, "analyze_with_radon", lambda code: ([], None))
