# app/dao/song_dao.py
from typing import List, Optional, Dict, Any, Iterable
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.song import Cancion as Song
from app.models.genre import Genre

class SongDAO:
    def __init__(self, db: Session):
        self.db = db

    # Normaliza la ruta de la imagen para almacenarla en la base de datos (que no se ponga el prefijo /files)
    def _normalize_img_path(self, path: str | None) -> str | None:
        if not path:
            return None
        path = path.strip()
        # La url externa no se toca
        if path.startswith("http://") or path.startswith("https://"):
            return path
        # Si viene con http://.../files/..., se queda con lo que va detras
        marker = "/files/"
        if marker in path:
            path = path.split(marker, 1)[1]
        # Se quitan las / iniciales si hay
        return path.lstrip("/")

    # Antes 'list' -> ahora 'list_songs'
    def list_songs(self, *, genero: Optional[str] = None, popularidad: Optional[str] = None):
        q = self.db.query(Song).options(joinedload(Song.genres))
        if genero:
            q = (
                q.join(Song.genres)
                .filter(func.lower(Genre.name).like(f"%{genero.lower()}%"))
            )
        if popularidad == "top":
            q = q.order_by(Song.numLikes.desc())
        elif popularidad == "tendencia":
            q = q.order_by(Song.numVisualizaciones.desc())
        elif popularidad == "reciente":
            q = q.order_by(Song.id.desc())
        return q.distinct().limit(200).all()

    def create(
        self,
        *,
        nomCancion: str,
        archivoMp3: str,
        imgPortada: Optional[str],
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

        if artistas_emails:
            song.set_artistas_emails(artistas_emails)

        self.db.add(song)
        self.db.flush()
        self.db.refresh(song)
        return song

    # RF 4.3
    def get(self, song_id: int) -> Optional[Song]:
        return (
            self.db.query(Song)
            .options(joinedload(Song.genres))
            .filter(Song.id == song_id)
            .one_or_none()
        )

    def update(self, song_id: int, *, update_data: Dict[str, Any]) -> Optional[Song]:
        """
        Actualiza una canción con los campos proporcionados.
        Si 'generos' viene en update_data, reasigna la relación M2M.
        """
        song = self.get(song_id)
        if not song:
            return None

        # normalizar imgPortada si viene del frontend con /files/...
        # (Tambien se hace en el album_dao)
        if "imgPortada" in update_data and update_data["imgPortada"]:
            update_data["imgPortada"] = self._normalize_img_path(update_data["imgPortada"])


        # actualizar géneros si vienen
        if "generos" in update_data and update_data["generos"] is not None:
            names = [g.strip().lower() for g in update_data["generos"] if g and g.strip()]
            found = []
            if names:
                found = (
                    self.db.query(Genre)
                    .filter(func.lower(Genre.name).in_(names))
                    .all()
                )
            song.set_genres(found)
            update_data.pop("generos", None)  # ya aplicado

        # actualizar el resto de campos “planos”
        for field, value in list(update_data.items()):
            if hasattr(song, field) and field not in {"id"}:
                setattr(song, field, value)

        self.db.commit()
        self.db.refresh(song)
        return song

    def delete(self, song_id: int) -> bool:
        song = self.get(song_id)
        if not song:
            return False
        self.db.delete(song)
        self.db.commit()
        return True

    def get_many(self, ids: Iterable[int]) -> List[Song]:
        ids = list({int(i) for i in ids})
        if not ids:
            return []
        return (
            self.db.query(Song)
            .options(
                joinedload(Song.genres),
                joinedload(Song.artistas_refs),  # precarga para propiedad
            )
            .filter(Song.id.in_(ids))
            .all()
        )

    def get_by_artist(self, email_artista: str) -> List[Song]:
        return (
            self.db.query(Song)
            .options(joinedload(Song.genres))
            .filter(Song.artistas_refs.any(artista_email=email_artista))
            .all()
        )

    # incrementa numVisualizaciones de una canción
    def increment_views(self, song_id: int, amount: int = 1):
        song = (
            self.db.query(Song)
            .filter(Song.id == song_id)
            .first()
        )
        if not song:
            return None

        # Si está a NULL se inicializa a 0
        current = getattr(song, "numVisualizaciones", 0) or 0
        song.numVisualizaciones = current + amount

        self.db.commit()
        self.db.refresh(song)
        return song

