# app/schemas/comment.py
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CommentCreate(BaseModel):
    content: str

class CommentOut(BaseModel):
    id: int
    content: str
    user_ref: str
    created_at: datetime

    # Opcionales para saber el contexto si listamos mezclados
    cancion_id: int | None = None
    album_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
