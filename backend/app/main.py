from fastapi import FastAPI
from app.api.review import router

app = FastAPI(title="AI Code Reviewer")

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Backend is running!"}