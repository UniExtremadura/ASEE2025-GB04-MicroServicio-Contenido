# app/factories/playlist.py
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dao.playlist_dao import PlaylistDAO


def get_playlist_dao(db: Session = Depends(get_db)) -> PlaylistDAO:
    return PlaylistDAO(db)

