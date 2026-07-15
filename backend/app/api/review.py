from fastapi import APIRouter
from app.schemas.review import (
    ReviewRequest,
    ReviewResponse,
    Issue,
)

router = APIRouter()


@router.post("/review", response_model=ReviewResponse)
def review(request: ReviewRequest):

    return ReviewResponse(
        score=95,
        summary="Everything is working!",
        issues=[
            Issue(
                severity="low",
                title="Missing docstring",
                line=1,
                suggestion="Consider adding a docstring."
            )
        ]
    )