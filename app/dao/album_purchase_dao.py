# app/dao/album_purchase_dao.py
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.purchase import CompraAlbum
from app.models.album import Album

class AlbumPurchaseDAO:
    def __init__(self, db: Session):
        self.db = db

    def purchase_album(
        self,
        *,
        album_id: int,
        user_ref: str,
        price_paid: Optional[float] = None,
    ) -> CompraAlbum:
        # Idempotencia: si ya existe, devuélvela
        existing = (
            self.db.query(CompraAlbum)
            .filter(
                CompraAlbum.album_id == album_id,
                CompraAlbum.user_ref == user_ref,
            )
            .one_or_none()
        )
        if existing:
            return existing

        album = self.db.query(Album).filter(Album.id == album_id).one_or_none()
        if not album:
            raise ValueError("album_not_found")

        min_price = float(album.precio or 0.0)

        if price_paid is None:
            price_paid = min_price
        elif price_paid < min_price:
            raise ValueError("price_below_min")

        compra = CompraAlbum(
            album_id=album_id,
            user_ref=user_ref,
            price_paid=price_paid,
        )
        self.db.add(compra)
        self.db.flush()
        self.db.refresh(compra)
        return compra

    # Identifica los IDs de los álbumes comprados por un usuario
    def list_user_album_ids(self, *, user_ref: str) -> List[int]:
        rows = (
            self.db.query(CompraAlbum.album_id)
            .filter(CompraAlbum.user_ref == user_ref)
            .all()
        )
        return [album_id for (album_id,) in rows]

