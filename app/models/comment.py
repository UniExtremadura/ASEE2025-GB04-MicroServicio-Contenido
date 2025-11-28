# app/models/comment.py
from __future__ import annotations
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class Comment(Base):
    __tablename__ = "comentario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Usuario que comenta (guardamos el email/ref)
    user_ref: Mapped[str] = mapped_column(String(120), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relación opcional con Canción
    cancion_id: Mapped[int | None] = mapped_column(
        ForeignKey("cancion.id", ondelete="CASCADE"),
        nullable=True
    )

    # Relación opcional con Álbum
    album_id: Mapped[int | None] = mapped_column(
        ForeignKey("album.id", ondelete="CASCADE"),
        nullable=True
    )

    # Relaciones ORM
    song = relationship("Cancion", back_populates="comments")
    album = relationship("Album", back_populates="comments")
