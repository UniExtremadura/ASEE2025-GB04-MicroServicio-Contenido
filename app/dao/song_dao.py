from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from app.models.song import Cancion as Song
from app.models.genre import Genre

class SongDAO:
    def __init__(self, db: Session):
        self.db = db

    # Renombrado: antes se llamaba 'list'
    def list_songs(self, *, genero: Optional[str] = None, popularidad: Optional[str] = None):
        q = self.db.query(Song)
        if genero:
            q = q.filter(Song.genre.ilike(f"%{genero}%"))
        if popularidad == "top":
            q = q.order_by(Song.numLikes.desc())
        elif popularidad == "tendencia":
            q = q.order_by(Song.numVisualizaciones.desc())
        elif popularidad == "reciente":
            q = q.order_by(Song.id.desc())
        return q.limit(200).all()

    def create(
        self,
        *,
        nomCancion: str,
        archivoMp3: str,
        imgPortada: Optional[str],
        # genre: Optional[str],
        genre_names: Optional[List[str]] = None,
        precio: float,
        date=None,
        artistas_emails: Optional[List[str]] = None,
        idAlbum: Optional[int] = None,
    ) -> Song:
        song = Song(
            nomCancion=nomCancion,
            archivoMp3=archivoMp3,
            imgPortada=imgPortada,
            # genre=genre,
            date=date,
            precio=precio,
            idAlbum=idAlbum,
        )

        if genre_names:
            norm = [g.strip().lower() for g in genre_names if g and g.strip()]
            if norm:
                found = (
                    self.db.query(Genre)
                    .filter(func.lower(Genre.name).in_(norm))
                    .all()
                )
                song.set_genres(found)

                # # si no pasa 'genre' simple, usa el primero como principal
                # if not genre and found:
                #     song.genre = found[0].name

        if artistas_emails:
            # método helper en el modelo Cancion
            song.set_artistas_emails(artistas_emails)

        self.db.add(song)
        self.db.flush()
        self.db.refresh(song)
        return song

    def get(self, song_id: int) -> Optional[Song]:
        """Obtiene una canción por su ID."""
        return self.db.query(Song).filter(Song.id == song_id).first()

    def update(self, song_id: int, *, update_data: Dict[str, Any]) -> Optional[Song]:
        """
        Actualiza una canción con un diccionario de datos.
        Este método es genérico y solo actualiza los campos proporcionados.
        """
        song = self.get(song_id)
        if not song:
            return None

        for field, value in update_data.items():
            if hasattr(song, field):
                setattr(song, field, value)

        self.db.commit()
        self.db.refresh(song)
        return song

    def delete(self, song_id: int) -> bool:
        """Elimina una canción por su ID."""
        song = self.get(song_id)
        if not song:
            return False
        self.db.delete(song)
        self.db.commit()
        return True
