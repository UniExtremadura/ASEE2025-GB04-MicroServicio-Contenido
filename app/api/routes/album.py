from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.album import AlbumOut, AlbumIn, AlbumUpdate
from app.dao.album_dao import AlbumDAO
from app.factories import get_album_dao

router = APIRouter(tags=["albumes"])


@router.get("/albumes", response_model=list[AlbumOut])
def listar_albumes(
    titulo: str | None = Query(None),
    album_dao: AlbumDAO = Depends(get_album_dao),
):
    return album_dao.list_albums(titulo=titulo)


@router.get("/albumes/{album_id}", response_model=AlbumOut)
def obtener_album(album_id: int, album_dao: AlbumDAO = Depends(get_album_dao)):
    album = album_dao.get(album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album

@router.delete("/albumes/{album_id}", status_code=204)
def borrar_album(album_id: int, album_dao: AlbumDAO = Depends(get_album_dao)):
    ok = album_dao.delete(album_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Album not found")
    return None
