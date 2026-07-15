from pydantic import BaseModel


class ReviewRequest(BaseModel):
    language: str
    code: str


class Issue(BaseModel):
    severity: str
    title: str
    line: int
    suggestion: str


class ReviewResponse(BaseModel):
    score: int
    summary: str
    issues: list[Issue]