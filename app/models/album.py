# app/models/album.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from app.db import Base

class Album(Base):
    __tablename__ = "album"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)

    canciones = relationship("Cancion", back_populates="album")
    # Más adelante quizas hacer una tabla que relacione artista y album

