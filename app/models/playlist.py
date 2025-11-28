# app/models/playlist.py
from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Playlist(Base):
    __tablename__ = "playlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # email del dueño (usuario u artista)
    owner_ref: Mapped[str] = mapped_column(String(120), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # relación con PlaylistSong; ordenada por position
    songs: Mapped[List["PlaylistSong"]] = relationship(
        "PlaylistSong",
        back_populates="playlist",
        cascade="all, delete-orphan",
        order_by="PlaylistSong.position",
    )

    # para que el schema pueda sacar song_ids directamente
    @property
    def song_ids(self) -> list[int]:
        return [ps.cancion_id for ps in self.songs]


class PlaylistSong(Base):
    __tablename__ = "playlist_cancion"

    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlist.id", ondelete="CASCADE"),
        primary_key=True,
    )
    cancion_id: Mapped[int] = mapped_column(
        ForeignKey("cancion.id", ondelete="CASCADE"),
        primary_key=True,
    )
    # posición dentro de la playlist (0,1,2,...)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    playlist: Mapped["Playlist"] = relationship(
        "Playlist",
        back_populates="songs",
    )
    # no necesitamos backref desde Cancion para este requisito

