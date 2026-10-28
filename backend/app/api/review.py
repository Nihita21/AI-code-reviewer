
from fastapi import APIRouter, HTTPException

from app.schemas.review import (
    ReviewRequest,
    ReviewResponse,
    Issue,
)
from app.services.analyzer import analyze_python
from app.services.ruff_analyzer import analyze_with_ruff

router = APIRouter()


@router.post("/review", response_model=ReviewResponse)
def review(request: ReviewRequest):
    if not request.code.strip():
        raise HTTPException(
            status_code=400,
            detail="Code cannot be empty.",
        )

    if request.language.lower() not in {"python", "py"}:
        raise HTTPException(
            status_code=400,
            detail="Currently, only Python code review is supported.",
        )

    ast_findings = analyze_python(request.code)

    # Syntax errors prevent meaningful Ruff analysis.
    if any(
        finding["title"].startswith("Syntax error:")
        for finding in ast_findings
    ):
        findings = ast_findings
    else:
        ruff_findings = analyze_with_ruff(request.code)

        # Merge duplicate findings using their line and title.
        findings = list(ast_findings)

        existing = {
            (item["line"], item["title"].split(":")[-1].strip().lower())
            for item in findings
        }

        for finding in ruff_findings:
            key = (
                finding["line"],
                finding["title"].split(":")[-1].strip().lower(),
            )

            if key not in existing:
                findings.append(finding)
                existing.add(key)

    issues = [Issue(**finding) for finding in findings]

    deductions = {"low": 5, "medium": 15, "high": 30}
    score = max(
        0,
        100 - sum(
            deductions.get(issue.severity, 0)
            for issue in issues
        ),
    )

    summary = (
        "No issues detected by the current analyzers."
        if not issues
        else f"Found {len(issues)} issue(s) in the submitted Python code."
    )

    return ReviewResponse(
        score=score,
        summary=summary,
        issues=issues,
    )
