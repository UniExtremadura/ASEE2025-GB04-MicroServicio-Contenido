from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from app.db import Base
from .associations import cancion_genero

class Genre(Base):
    __tablename__ = "genre"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    songs = relationship("Cancion", secondary=cancion_genero, back_populates="genres")

