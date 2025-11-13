# app/models/artist_links.py
# ==========================================================
# Tabla de enlace local cancion - artista usando email del artista
# ==========================================================
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from app.db import Base

class CancionArtistaLink(Base):
    __tablename__ = "cancion_artista"

    cancion_id: Mapped[int] = mapped_column(
        ForeignKey("cancion.id", ondelete="CASCADE"), primary_key=True
    )
    artista_email: Mapped[str] = mapped_column(String(120), primary_key=True, index=True)

    # backref a Cancion
    song = relationship("Cancion", back_populates="artistas_refs")

    __table_args__ = (
        UniqueConstraint("cancion_id", "artista_email", name="uq_cancion_artista"),
    )

class AlbumArtistaLink(Base):
    __tablename__ = "album_artista"

    album_id: Mapped[int] = mapped_column(
        ForeignKey("album.id", ondelete="CASCADE"), primary_key=True
    )
    artista_email: Mapped[str] = mapped_column(String(120), primary_key=True, index=True)

    # backref a Album
    album = relationship("Album", back_populates="artistas_refs")

    __table_args__ = (
        UniqueConstraint("album_id", "artista_email", name="uq_album_artista"),
    )
