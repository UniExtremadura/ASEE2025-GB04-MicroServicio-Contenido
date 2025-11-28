# app/services/album_service.py
from typing import Dict, Any, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dao.album_dao import AlbumDAO
from app.models.album import Album
from app.models.song import Cancion
from app.models.genre import Genre
from sqlalchemy import func

class AlbumService:
    def __init__(self, db: Session):
        self.db = db
        self.album_dao = AlbumDAO(db)

    def update_album(self, album_id: int, update_data: Dict[str, Any]) -> Optional[Album]:
        """
        Servicio para actualizar un álbum, manejando la lógica de negocio
        para relaciones como géneros y canciones.
        """
        album = self.album_dao.get(album_id)
        if not album:
            return None

        # Separar campos simples de relaciones
        simple_fields = {k: v for k, v in update_data.items() if k not in ["canciones_ids", "genre_names", "artista_emails"]}
        if simple_fields:
            self.album_dao.update(album_id, update_data=simple_fields)

        # Lógica de negocio para relaciones
        if "canciones_ids" in update_data:
            canciones = self.db.query(Cancion).filter(Cancion.id.in_(update_data["canciones_ids"])).all()
            album.canciones = canciones

        if "genre_names" in update_data:
            norm = [g.strip().lower() for g in update_data["genre_names"] if g.strip()]
            found = self.db.query(Genre).filter(func.lower(Genre.name).in_(norm)).all()
            album.genres = found

        if "artista_emails" in update_data:
            album.set_artistas_emails(update_data["artista_emails"])

        self.db.commit()
        self.db.refresh(album)
        return album

    def update_album_price(self, album_id: int, precio: float) -> Optional[Album]:
        """Servicio específico para actualizar el precio de un álbum."""
        return self.album_dao.update(album_id, update_data={"precio": precio})