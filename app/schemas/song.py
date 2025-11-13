# app/schemas/song.py
from __future__ import annotations

from datetime import date as Date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_serializer

class CancionOut(BaseModel):
    id: int
    nomCancion: str
    archivoMp3: str
    imgPortada: Optional[str] = None
    genre: Optional[str] = None
    generos: List[str] = []
    date: Optional[Date] = None   # ← fecha o None
    precio: float
    numVisualizaciones: int
    numIngresos: float
    numLikes: int
    idAlbum: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("archivoMp3")
    def _ser_archivo(self, v: str):
        if not v or v.startswith("http") or v.startswith("/files/"):
            return v
        return f"/files/{v.lstrip('/')}"

    @field_serializer("imgPortada")
    def _ser_img(self, v: Optional[str]):
        if not v or v.startswith("http") or v.startswith("/files/"):
            return v
        return f"/files/{v.lstrip('/')}"

