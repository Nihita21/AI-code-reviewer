from fastapi import APIRouter

router = APIRouter()

@router.post("/review")
def review():
    return {
        "score": 90,
        "summary": "Backend is working!",
        "issues": []
    }