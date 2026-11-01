import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # dotenv is optional
    pass


class Settings:
    """Reads configuration from environment variables at access time."""

    @property
    def data_dir(self) -> Path:
        p = Path(os.getenv("DATA_DIR", "./data")).resolve()
        (p / "vectors").mkdir(parents=True, exist_ok=True)
        (p / "uploads").mkdir(parents=True, exist_ok=True)
        return p

    @property
    def db_path(self) -> Path:
        return self.data_dir / "app.db"

    @property
    def max_upload_mb(self) -> int:
        return int(os.getenv("MAX_UPLOAD_MB", "20"))

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

    @property
    def embedding_backend(self) -> str:
        return os.getenv("EMBEDDING_BACKEND", "sentence-transformers").lower()

    @property
    def embedding_model(self) -> str:
        return os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    @property
    def llm_provider(self) -> str:
        return os.getenv("LLM_PROVIDER", "none").lower()

    @property
    def llm_api_key(self) -> str:
        return os.getenv("LLM_API_KEY", "")

    @property
    def llm_model(self) -> str:
        return os.getenv("LLM_MODEL", "gemini-2.5-flash")

    @property
    def llm_base_url(self) -> str:
        return os.getenv("LLM_BASE_URL", "").rstrip("/")

    @property
    def top_k(self) -> int:
        return int(os.getenv("TOP_K", "5"))

    @property
    def chunk_size(self) -> int:
        return int(os.getenv("CHUNK_SIZE", "900"))

    @property
    def chunk_overlap(self) -> int:
        return int(os.getenv("CHUNK_OVERLAP", "150"))

    @property
    def min_relevance(self) -> float:
        v = os.getenv("MIN_RELEVANCE", "").strip()
        if v:
            return float(v)
        return 0.10 if self.embedding_backend == "hash" else 0.25

    @property
    def llm_configured(self) -> bool:
        return self.llm_provider != "none" and bool(self.llm_api_key)


settings = Settings()
