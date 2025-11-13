from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.album import AlbumOut, AlbumIn, AlbumUpdate, AlbumPriceUpdate
from app.dao.album_dao import AlbumDAO
from app.factories import get_album_dao
from app.services.album_service import AlbumService
from app.db import get_db

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

@router.put(
    "/albumes/{album_id}",
    response_model=AlbumOut,
    summary="Actualizar un álbum por ID",
)
def update_album(
    album_id: int,
    album_update: AlbumUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualiza los campos de un álbum.
    Los campos no proporcionados no se modificarán.
    """
    album_service = AlbumService(db)
    update_data = album_update.model_dump(exclude_unset=True)
    
    if "genre" in update_data:
        update_data["genre_names"] = update_data.pop("genre")

    updated_album = album_service.update_album(album_id, update_data=update_data)

    if updated_album is None:
        raise HTTPException(status_code=404, detail=f"Álbum con id={album_id} no encontrado")
    
    return updated_album

@router.patch(
    "/albumes/{album_id}/precio",
    response_model=AlbumOut,
    summary="Actualizar el precio de un álbum",
)
def update_album_price(
    album_id: int,
    price_update: AlbumPriceUpdate,
    db: Session = Depends(get_db),
):
    album_service = AlbumService(db)
    updated_album = album_service.update_album_price(album_id, precio=price_update.precio)
    if updated_album is None:
        raise HTTPException(status_code=404, detail=f"Álbum con id={album_id} no encontrado")
    return updated_album

@router.delete("/albumes/{album_id}", status_code=204)
def borrar_album(album_id: int, album_dao: AlbumDAO = Depends(get_album_dao)):
    ok = album_dao.delete(album_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Album not found")
    return None
