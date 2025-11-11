# app/models/song.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Date, ForeignKey
from app.db import Base
from .associations import playlist_cancion, cancion_genero
from .artist_links import CancionArtistaLink


class Cancion(Base):
    __tablename__ = "cancion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nomCancion: Mapped[str] = mapped_column(String(255), nullable=False)
    archivoMp3: Mapped[str] = mapped_column(String, nullable=False)
    imgPortada: Mapped[str | None] = mapped_column(String, nullable=True)
    # genre: Mapped[str | None] = mapped_column(String(64), nullable=True)
    date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    precio: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    numVisualizaciones: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    numIngresos: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    numLikes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    idAlbum: Mapped[int | None] = mapped_column("idAlbum", ForeignKey("album.id"), nullable=True)

    genres = relationship("Genre", secondary=cancion_genero, back_populates="songs")


    # 🔧 relaciones coherentes
    artistas_refs = relationship(
        # enlaza cancion y artista por email (id)
        "CancionArtistaLink",
        back_populates="song",
        cascade="all, delete-orphan",
    )
    album = relationship("Album", back_populates="canciones")
    playlists = relationship("Playlist", secondary=playlist_cancion, back_populates="canciones")


    purchases = relationship(
        "CompraCancion",
        back_populates="song",
        cascade="all, delete-orphan",
    )


    @property
    def generos(self) -> list[str]:
        # nombres desde la relación N–N
        return [g.name for g in self.genres]

    # helpers opcionales
    @property
    def artistas_emails(self) -> list[str]:
        return [r.artista_email for r in self.artistas_refs]

    def set_artistas_emails(self, emails: list[str]):
        self.artistas_refs = [CancionArtistaLink(artista_email=e) for e in emails]

    def set_genres(self, genre_models: list):
        self.genres = genre_models

# Song = Cancion
