# app/schemas/playlist.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None


class PlaylistCreate(PlaylistBase):
    # IDs de canciones a añadir al crear la lista (opcional)
    song_ids: List[int] = []


class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PlaylistOut(PlaylistBase):
    id: int
    owner_ref: str
    created_at: datetime
    updated_at: datetime
    song_ids: List[int] = []

    model_config = ConfigDict(from_attributes=True)


class PlaylistAddSong(BaseModel):
    song_id: int

