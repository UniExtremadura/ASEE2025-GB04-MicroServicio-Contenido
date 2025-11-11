# app/dao/purchase_dao.py
from __future__ import annotations

from typing import Iterable, List, Optional, Dict, Set
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.purchase import CompraCancion
from app.models.song import Cancion as Song

class PurchaseDAO:
    def __init__(self, db: Session):
        self.db = db

    def purchase(
        self,
        *,
        song_id: int,
        user_ref: str,
        price_paid: Optional[float] = None,
    ) -> CompraCancion:
        # idempotencia: si ya existe, devuélvela
        existing = self.db.query(CompraCancion).filter(
            CompraCancion.cancion_id == song_id,
            CompraCancion.user_ref == user_ref,
        ).one_or_none()
        if existing:
            return existing

        # valida canción
        song = self.db.query(Song).filter(Song.id == song_id).one_or_none()
        if not song:
            raise ValueError("song_not_found")

        # fija precio si no viene (precio de la canción en ese momento)
        if price_paid is None:
            price_paid = float(song.precio or 0.0)

        obj = CompraCancion(
            cancion_id=song_id,
            user_ref=user_ref,
            price_paid=price_paid,
        )
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def has_purchase(self, *, song_id: int, user_ref: str) -> bool:
        return self.db.query(CompraCancion).filter(
            CompraCancion.cancion_id == song_id,
            CompraCancion.user_ref == user_ref,
        ).first() is not None

    def list_user_song_ids(self, *, user_ref: str) -> List[int]:
        rows = self.db.query(CompraCancion.cancion_id).filter(
            CompraCancion.user_ref == user_ref
        ).all()
        return [cid for (cid,) in rows]

    def list_user_purchases(self, *, user_ref: str) -> List[CompraCancion]:
        return (
            self.db.query(CompraCancion)
            .filter(CompraCancion.user_ref == user_ref)
            .order_by(CompraCancion.purchased_at.desc())
            .all()
        )

    def count_song_purchases(self, *, song_id: int) -> int:
        return self.db.query(func.count(CompraCancion.user_ref)).filter(
            CompraCancion.cancion_id == song_id
        ).scalar() or 0


