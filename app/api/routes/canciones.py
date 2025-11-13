# app/api/routes/canciones.py
from fastapi import APIRouter, Depends, Query
from app.schemas.song import CancionOut

from app.factories import get_song_dao
from app.dao.song_dao import SongDAO

router = APIRouter(tags=["canciones"])

@router.get("/canciones", response_model=list[CancionOut])
def listar_canciones(
    genero: str | None = Query(None),
    popularidad: str | None = Query(None),
    song_dao: SongDAO = Depends(get_song_dao),
):
    return song_dao.list_songs(genero=genero, popularidad=popularidad)

