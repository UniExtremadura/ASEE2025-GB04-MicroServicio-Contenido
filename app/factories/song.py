# app/factories/song.py  
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db

from app.dao.song_dao import SongDAO 

def get_song_dao(db: Session = Depends(get_db)):
    return SongDAO(db)

