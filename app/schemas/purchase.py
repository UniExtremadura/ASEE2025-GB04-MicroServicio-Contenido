# app/schemas/purchase.py
from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Dict, Set
from pydantic import BaseModel, ConfigDict

class CompraCreate(BaseModel):
    song_id: int
    user_ref: str
    price_paid: Optional[float] = None

class CompraOut(BaseModel):
    song_id: int
    user_ref: str
    purchased_at: datetime
    price_paid: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class CompraCheckOut(BaseModel):
    purchased: bool


class CompraAlbumCreate(BaseModel):
    user_ref: str
    price_paid: Optional[float] = None

class CompraAlbumOut(BaseModel):
    album_id: int
    user_ref: str
    purchased_at: datetime
    price_paid: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


# Comprueba compra múltiple
class CompraCheckMultipleIn(BaseModel):
    user_ref: str
    song_ids: List[int]


# Resultado de comprobar varias canciones.
class CompraCheckMultipleOut(BaseModel):
    owned: List[int]
    missing: List[int]
