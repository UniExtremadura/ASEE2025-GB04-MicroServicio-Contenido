# app/models/associations.py
from sqlalchemy import Table, Column, ForeignKey, UniqueConstraint
from app.db import Base


playlist_cancion = Table(
    "playlist_cancion",
    Base.metadata,
    Column("playlist_id", ForeignKey("playlist.id"), primary_key=True),
    Column("cancion_id", ForeignKey("cancion.id"), primary_key=True),
)


cancion_genero = Table(
    "cancion_genero",
    Base.metadata,
    Column("cancion_id", ForeignKey("cancion.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", ForeignKey("genre.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("cancion_id", "genre_id", name="uq_cancion_genero"),
)
