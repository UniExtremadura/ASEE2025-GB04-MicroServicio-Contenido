from __future__ import annotations

from datetime import date as Date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_serializer, field_validator


class AlbumOut(BaseModel):
    id: int
    titulo: str
    imgPortada: Optional[str] = None
    genre: List[str] = []
    date: Optional[Date] = None
    precio: float
    canciones_ids: List[int] = []
    artistas_emails: List[str] = []

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("imgPortada")
    def _ser_img(self, v: Optional[str]):
        if not v or v.startswith("http") or v.startswith("/files/"):
            return v
        return f"/files/{v.lstrip('/')}"


class AlbumIn(BaseModel):
    titulo: str
    imgPortada: Optional[str] = None
    genre: Optional[str] = None
    date: Optional[Date] = None
    precio: float = 0
    canciones_ids: Optional[List[int]] = None
    artista_emails: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("canciones_ids")
    def _validate_canciones_in(cls, v: Optional[List[int]]):
        """Valida que `canciones_ids` sea una lista de enteros y no vacía cuando se proporciona.

        La existencia real de las canciones se valida en la capa de persistencia (DAO).
        """
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("canciones_ids debe ser una lista de enteros")
        if len(v) == 0:
            raise ValueError("Debe incluir al menos una canción en 'canciones_ids'")
        for x in v:
            if not isinstance(x, int) or x <= 0:
                raise ValueError("Cada id en 'canciones_ids' debe ser un entero positivo")
        return v


class AlbumUpdate(BaseModel):
    titulo: Optional[str] = None
    imgPortada: Optional[str] = None
    genre: Optional[List[str]] = None
    date: Optional[Date] = None
    precio: Optional[float] = None
    canciones_ids: Optional[List[int]] = None
    artista_emails: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("canciones_ids")
    def _validate_canciones_update(cls, v: Optional[List[int]]):
        """Valida formato de `canciones_ids` en actualizaciones si se proporciona."""
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("canciones_ids debe ser una lista de enteros")
        for x in v:
            if not isinstance(x, int) or x <= 0:
                raise ValueError("Cada id en 'canciones_ids' debe ser un entero positivo")
        return v
    
    @field_serializer("imgPortada")
    def _ser_img(self, v: Optional[str]):
        if not v or v.startswith("http") or v.startswith("/files/"):
            return v
        return f"/files/{v.lstrip('/')}"

class AlbumPriceUpdate(BaseModel):
    """Schema específico para actualizar solo el precio de un álbum."""
    precio: float