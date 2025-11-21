# app/dao/playlist_dao.py
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.playlist import Playlist, PlaylistSong
from app.models.song import Cancion as Song


class PlaylistDAO:
    def __init__(self, db: Session):
        self.db = db

    def _get_next_position(self, playlist_id: int) -> int:
        max_pos = (
            self.db.query(func.max(PlaylistSong.position))
            .filter(PlaylistSong.playlist_id == playlist_id)
            .scalar()
        )
        if max_pos is None:
            return 0
        return int(max_pos) + 1

    def create(
        self,
        *,
        owner_ref: str,
        name: str,
        description: Optional[str] = None,
        song_ids: Optional[List[int]] = None,
    ) -> Playlist:
        playlist = Playlist(
            owner_ref=owner_ref,
            name=name,
            description=description,
        )
        self.db.add(playlist)
        self.db.flush()  # para tener playlist.id

        if song_ids:
            # Validamos que las canciones existen
            valid_ids = [
                s_id
                for (s_id,) in self.db.query(Song.id)
                .filter(Song.id.in_(song_ids))
                .all()
            ]
            seen: set[int] = set()
            pos = 0
            for s_id in valid_ids:
                if s_id in seen:
                    continue
                seen.add(s_id)
                link = PlaylistSong(
                    playlist_id=playlist.id,
                    cancion_id=s_id,
                    position=pos,
                )
                self.db.add(link)
                pos += 1

        self.db.flush()
        self.db.refresh(playlist)
        return playlist

    def get(self, playlist_id: int) -> Optional[Playlist]:
        return (
            self.db.query(Playlist)
            .options(joinedload(Playlist.songs))
            .filter(Playlist.id == playlist_id)
            .first()
        )

    def list_by_owner(self, owner_ref: str) -> List[Playlist]:
        return (
            self.db.query(Playlist)
            .options(joinedload(Playlist.songs))
            .filter(Playlist.owner_ref == owner_ref)
            .order_by(Playlist.created_at.desc())
            .all()
        )

    def delete(self, playlist_id: int) -> bool:
        playlist = self.db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            return False
        self.db.delete(playlist)
        return True

    def update(
        self,
        playlist_id: int,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Playlist]:
        playlist = self.db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            return None

        if name is not None:
            playlist.name = name
        if description is not None:
            playlist.description = description

        self.db.flush()
        self.db.refresh(playlist)
        return playlist

    def add_song(self, playlist_id: int, song_id: int) -> Optional[Playlist]:
        # Comprobamos que la playlist existe
        playlist = self.db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            return None

        # Comprobamos que la canción existe
        song_exists = (
            self.db.query(Song.id).filter(Song.id == song_id).first() is not None
        )
        if not song_exists:
            raise ValueError("song_not_found")

        # ¿Ya estaba la canción?
        link = (
            self.db.query(PlaylistSong)
            .filter(
                PlaylistSong.playlist_id == playlist_id,
                PlaylistSong.cancion_id == song_id,
            )
            .first()
        )
        if link is None:
            pos = self._get_next_position(playlist_id)
            link = PlaylistSong(
                playlist_id=playlist_id,
                cancion_id=song_id,
                position=pos,
            )
            self.db.add(link)

        self.db.flush()
        self.db.refresh(playlist)
        return playlist

    def remove_song(self, playlist_id: int, song_id: int) -> Optional[Playlist]:
        playlist = self.db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            return None

        link = (
            self.db.query(PlaylistSong)
            .filter(
                PlaylistSong.playlist_id == playlist_id,
                PlaylistSong.cancion_id == song_id,
            )
            .first()
        )
        if link:
            self.db.delete(link)

        self.db.flush()
        self.db.refresh(playlist)
        return playlist

