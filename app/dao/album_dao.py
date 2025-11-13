from typing import Optional, Dict, Any, List, Set
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.album import Album
from app.models.song import Cancion
from app.models.genre import Genre
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.models.artist_links import AlbumArtistaLink

class AlbumDAO:
    def __init__(self, db: Session):
        self.db = db

    def list_albums(self, *, titulo: Optional[str] = None):
        # Cargar las relaciones de géneros y canciones
        q = self.db.query(Album).options(
            joinedload(Album.genres),
            joinedload(Album.canciones)
        )
        if titulo:
            q = q.filter(Album.titulo.ilike(f"%{titulo}%"))
        return q.limit(200).all()

    def get(self, album_id: int) -> Optional[Album]:
        return self.db.query(Album).options(
            joinedload(Album.genres),
            joinedload(Album.canciones)
        ).filter(Album.id == album_id).first()

    def create(
        self,
        *,
        titulo: str,
        imgPortada: Optional[str] = None,
        genre_names: Optional[List[str]] = None,
        date=None,
        precio: float = 0,
        canciones_ids: Optional[List[int]] = None,
        artista_emails: Optional[List[str]] = None,
    ) -> Album:
        album = Album(titulo=titulo)
        album.imgPortada = imgPortada
        album.date = date
        album.precio = precio
        album.genres = []

        # relaciones: canciones
        if canciones_ids:
            canciones = self.db.query(Cancion).filter(Cancion.id.in_(canciones_ids)).all()
            found_ids: Set[int] = {c.id for c in canciones}
            missing = set(canciones_ids) - found_ids
            if missing:
                raise HTTPException(status_code=400, detail=f"Canciones no encontradas: {sorted(missing)}")
            album.canciones = canciones


        if genre_names:  # lista validada desde el endpoint
            norm = [g.strip().lower() for g in genre_names if g.strip()]
            if norm:
             found = (
                self.db.query(Genre)
                .filter(func.lower(Genre.name).in_(norm))
                .all()
             )
            if len(found) != len(norm):
             missing = set(norm) - {g.name.lower() for g in found}
             raise HTTPException(status_code=400, detail=f"Géneros no válidos: {sorted(missing)}")
        album.genres = found


            # # si no pasa 'genre' simple, usa el primero como principal
              # if not genre and found:
            #     song.genre = found[0].name
        # relaciones: artistas (usando el helper)
        if artista_emails:
            # método helper en el modelo Cancion
            album.set_artistas_emails(artista_emails)
       
       
       
        self.db.add(album)
        self.db.commit()
        self.db.refresh(album)
        return album

    def update(self, album_id: int, *, update_data: Dict[str, Any]) -> Optional[Album]:
        """
        Actualiza un álbum con un diccionario de datos.
        Este método es genérico y solo actualiza los campos proporcionados.
        """
        album = self.get(album_id)
        if not album:
            return None
        
        for field, value in update_data.items():
            if hasattr(album, field):
                setattr(album, field, value)
        
        self.db.commit()
        self.db.refresh(album)
        return album

    def delete(self, album_id: int) -> bool:
        album = self.get(album_id)
        if not album:
            return False
        self.db.delete(album)
        self.db.commit()
        return True
    

    def get_by_artist(self, email_artista: str) -> List[Album]:
        """
        Obtiene todos los álbumes asociados a un email de artista.
        """
        # Hacemos un JOIN con la tabla intermedia AlbumArtistaLink
        # y filtramos por el email del artista.
        # También cargamos las canciones y géneros para que 
        # la respuesta JSON sea completa.
        q = self.db.query(Album)\
            .options(
                joinedload(Album.genres),
                joinedload(Album.canciones)
            )\
            .join(AlbumArtistaLink, Album.id == AlbumArtistaLink.album_id)\
            .filter(AlbumArtistaLink.artista_email == email_artista)
        
        return q.all()