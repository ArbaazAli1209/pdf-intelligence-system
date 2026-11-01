from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, documents
from app.core.config import settings
from app.database.db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI PDF Question Answering System", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "embedding_backend": settings.embedding_backend,
        "llm_provider": settings.llm_provider,
        "llm_configured": settings.llm_configured,
        "answer_mode": "llm" if settings.llm_configured else "extractive",
        "max_upload_mb": settings.max_upload_mb,
    }
