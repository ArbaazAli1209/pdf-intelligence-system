from typing import Literal, Optional

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    title: Optional[str] = None
    document_ids: list[int] = Field(default_factory=list)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    mode: Literal["auto", "llm", "extractive"] = "auto"
