from collections import Counter

from fastapi import APIRouter, HTTPException

from app import config
from app.schemas.review import (
    Capabilities,
    Issue,
    LanguageInfo,
    Metrics,
    ReviewRequest,
    ReviewResponse,
)
from app.services.ai_reviewer import ai_configured, review_with_ai
from app.services.errors import AnalyzerUnavailable
from app.services.pipeline import compute_score, merge_findings, run_static_analysis

router = APIRouter()

# id, label, has static analysis. Every language can be reviewed by the AI.
LANGUAGES = [
    ("python", "Python", True),
    ("javascript", "JavaScript", False),
    ("java", "Java", False),
    ("cpp", "C++", False),
]
LANGUAGE_IDS = {language_id for language_id, _, _ in LANGUAGES}
ALIASES = {"py": "python", "js": "javascript", "c++": "cpp"}


def build_summary(issues: list[Issue]) -> str:
    if not issues:
        return "No issues detected by the current analyzers."
    counts = Counter(issue.severity for issue in issues)
    parts = [f"{counts[level]} {level}" for level in ("high", "medium", "low") if counts[level]]
    return f"Found {len(issues)} issue(s): {', '.join(parts)}."


def to_issue(finding: dict) -> Issue:
    # `kind` is internal bookkeeping for de-duplication and is not part of the API.
    return Issue(**{key: value for key, value in finding.items() if key != "kind"})


@router.get("/capabilities", response_model=Capabilities)
def capabilities():
    """Tell the frontend what this backend can do, so the UI never offers dead options."""
    ai_enabled = ai_configured()
    return Capabilities(
        ai_enabled=ai_enabled,
        ai_model=config.openai_model() if ai_enabled else None,
        languages=[
            LanguageInfo(
                id=language_id,
                label=label,
                static_analysis=static,
                ai_review=ai_enabled,
            )
            for language_id, label, static in LANGUAGES
        ],
    )


@router.post("/review", response_model=ReviewResponse)
def review(request: ReviewRequest):
    code = request.code

    if not code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    limit = config.max_code_chars()
    if len(code) > limit:
        raise HTTPException(
            status_code=413,
            detail=f"Code is too large (limit: {limit:,} characters).",
        )

    requested = request.language.strip().lower()
    language = ALIASES.get(requested, requested)

    if language not in LANGUAGE_IDS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {request.language}.",
        )

    use_ai = request.use_ai and ai_configured()

    if language != "python" and not use_ai:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only Python has built-in static analysis. Enable AI review "
                f"(and configure OPENAI_API_KEY) to review {language} code."
            ),
        )

    findings: list[dict] = []
    warnings: list[str] = []
    metrics = None
    ai_summary = None

    if language == "python":
        findings, warnings, metrics = run_static_analysis(code)

    if use_ai:
        try:
            ai_result = review_with_ai(code, language, findings)
        except AnalyzerUnavailable as error:
            if language != "python":
                # Nothing else to show for these languages, so surface the failure.
                raise HTTPException(status_code=502, detail=str(error)) from error
            warnings.append(str(error))
        else:
            ai_summary = ai_result["summary"] or None
            findings = merge_findings(findings, ai_result["issues"])
            findings.sort(key=lambda finding: finding["line"])

    issues = [to_issue(finding) for finding in findings]

    return ReviewResponse(
        score=compute_score(findings),
        summary=build_summary(issues),
        issues=issues,
        metrics=Metrics(**metrics) if metrics else None,
        ai_summary=ai_summary,
        warnings=warnings,
    )
