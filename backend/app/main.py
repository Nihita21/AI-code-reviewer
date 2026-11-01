from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.api.review import router

app = FastAPI(
    title="AI Code Reviewer",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Backend is running!"}


@app.get("/health")
def health():
    return {"status": "ok"}
