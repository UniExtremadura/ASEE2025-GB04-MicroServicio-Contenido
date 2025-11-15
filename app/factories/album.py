# app/factories/album.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db

from app.dao.album_dao import AlbumDAO


def get_album_dao(db: Session = Depends(get_db)):
    return AlbumDAO(db)
