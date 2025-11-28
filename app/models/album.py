# app/models/album.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Date
from app.db import Base

from .associations import album_genero
from .artist_links import CancionArtistaLink, AlbumArtistaLink


class Album(Base):
    __tablename__ = "album"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)

    imgPortada: Mapped[str | None] = mapped_column(String, nullable=True)
    date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    precio: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    # relaciones con géneros
    genres = relationship("Genre", secondary=album_genero, back_populates="albums")

    # relaciones con canciones
    canciones = relationship(
        "Cancion",
        back_populates="album",
        cascade="all",  # al quitarla del álbum NO se borra
    )

    # relación N–N con artistas usando tabla intermedia
    artistas_refs = relationship(
        "AlbumArtistaLink",
        back_populates="album",
        cascade="all, delete-orphan",
    )

    album_purchases = relationship(
        "CompraAlbum",
        back_populates="album",
        cascade="all, delete-orphan",
    )

    comments = relationship(
        "Comment",
        back_populates="album",
        cascade="all, delete-orphan",
        order_by="desc(Comment.created_at)"
    )

    @property
    def generos(self) -> list[str]:
        # nombres desde la relación N–N
        return [g.name for g in self.genres]

    # helper 
    @property
    def artistas_emails(self) -> list[str]:
        return [r.artista_email for r in self.artistas_refs]

    def set_artistas_emails(self, emails: list[str]):
        self.artistas_refs = [AlbumArtistaLink(artista_email=e) for e in emails]

    @property
    def genre(self) -> list[str]:
        # Para compatibilidad con el frontend que espera "genre"
        return self.generos

    @property
    def canciones_ids(self) -> list[int]:
        return [c.id for c in self.canciones]

