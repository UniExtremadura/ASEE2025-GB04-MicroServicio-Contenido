# app/api/routes/canciones.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
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


# RF 4.3 - Obtener detalle de canción
@router.get("/canciones/{song_id}", response_model=CancionOut, summary="Obtener detalle de canción (RF-4.3)")
def get_song(song_id: int, song_dao: SongDAO = Depends(get_song_dao)):
    song = song_dao.get(song_id)
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Canción no encontrada")
    return song
