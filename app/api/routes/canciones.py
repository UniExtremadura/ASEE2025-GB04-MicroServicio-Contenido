# app/api/routes/canciones.py
from fastapi import APIRouter, Depends, Query, HTTPException
from app.schemas.song import CancionOut
from app.schemas.album import AlbumOut

from app.factories import get_song_dao, get_album_dao
from app.dao.song_dao import SongDAO
from app.dao.album_dao import AlbumDAO

router = APIRouter(tags=["canciones"])

@router.get("/canciones", response_model=list[CancionOut])
def listar_canciones(
    genero: str | None = Query(None),
    popularidad: str | None = Query(None),
    song_dao: SongDAO = Depends(get_song_dao),
):
    return song_dao.list_songs(genero=genero, popularidad=popularidad)

@router.delete("/canciones/{cancion_id}", status_code=204)
def borrar_cancion(cancion_id: int, song_dao: SongDAO = Depends(get_song_dao)):
    """Elimina una canción por su ID."""
    ok = song_dao.delete(cancion_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    return None

@router.get("/artistas/{email_artista}/canciones", response_model=list[CancionOut])
def listar_canciones_por_artista(
    email_artista: str,
    song_dao: SongDAO = Depends(get_song_dao)
):
    """Lista las canciones de un artista dado su email."""
    return song_dao.get_by_artist(email_artista)

@router.get("/artistas/{email_artista}/albumes", response_model=list[AlbumOut])
def listar_albumes_por_artista(
    email_artista: str, album_dao: AlbumDAO = Depends(get_album_dao)
):
    """Lista los álbumes de un artista dado su email."""
    return album_dao.get_by_artist(email_artista)
