# app/models/purchase.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class CompraCancion(Base):
    __tablename__ = "compra_cancion"

    # PK compuesta (idempotencia: 1 fila por (cancion, usuario))
    cancion_id: Mapped[int] = mapped_column(
        ForeignKey("cancion.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_ref: Mapped[str] = mapped_column(String(120), primary_key=True, index=True)

    purchased_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    price_paid: Mapped[float | None] = mapped_column(Float, nullable=True)


    # alias para mantener consistencia con otros modelos
    @property
    def song_id(self) -> int:
        return self.cancion_id

    # relación hacia canción (para joins/listados)
    song = relationship("Cancion", back_populates="purchases")

