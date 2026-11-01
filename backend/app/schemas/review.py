from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["low", "medium", "high"]


class ReviewRequest(BaseModel):
    language: str = Field(min_length=1, max_length=30)
    code: str
    use_ai: bool = True


class Issue(BaseModel):
    severity: Severity
    title: str
    line: int
    suggestion: str
    # Which analyzer produced the finding: ast, ruff, bandit, radon or ai.
    source: str = "static"


class Metrics(BaseModel):
    lines_of_code: int
    functions: int
    average_complexity: float
    max_complexity: int
    maintainability_index: float


class ReviewResponse(BaseModel):
    score: int
    summary: str
    issues: list[Issue]
    metrics: Metrics | None = None
    ai_summary: str | None = None
    warnings: list[str] = Field(default_factory=list)


class LanguageInfo(BaseModel):
    id: str
    label: str
    static_analysis: bool
    ai_review: bool


class Capabilities(BaseModel):
    ai_enabled: bool
    ai_model: str | None = None
    languages: list[LanguageInfo]
