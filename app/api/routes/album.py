from datetime import date as Date
from typing import List, Any, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    Form,
    File,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.schemas.album import AlbumOut, AlbumIn, AlbumUpdate, AlbumPriceUpdate
from app.schemas.song import CancionOut
from app.dao.album_dao import AlbumDAO
from app.factories import get_album_dao
from app.services.album_service import AlbumService
from app.db import get_db
from app.services.storage import save_upload  

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



@router.get(
    "/albumes/{album_id}/canciones",
    response_model=List[CancionOut],
    summary="Listar canciones de un álbum",
)
def listar_canciones_de_album(
    album_id: int,
    album_dao: AlbumDAO = Depends(get_album_dao),
):
    """
    Devuelve todas las canciones asociadas a un álbum.
    """
    album = album_dao.get(album_id)  # ya hace joinedload(Album.canciones)
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Álbum no encontrado",
        )

    # album.canciones es una lista de modelos Cancion
    return album.canciones


@router.put(
    "/albumes/{album_id}",
    response_model=AlbumOut,
    summary="Actualizar un álbum por ID (datos + portada opcional)",
)
async def update_album(
    album_id: int,
    titulo: Optional[str] = Form(None),
    precio: Optional[float] = Form(None),
    date: Optional[Date] = Form(None),
    # lista de géneros (nombres)
    genre: Optional[List[str]] = Form(None),
    # ids de canciones del álbum
    canciones_ids: Optional[List[int]] = Form(None),
    # ojo con el nombre: en el schema es 'artista_emails'
    artista_emails: Optional[List[str]] = Form(None),

    portada: UploadFile | None = File(None),

    db: Session = Depends(get_db),
):
    album_service = AlbumService(db)

    update_data: dict[str, Any] = {}

    if titulo is not None:
        update_data["titulo"] = titulo
    if precio is not None:
        update_data["precio"] = precio
    if date is not None:
        update_data["date"] = date

    # Igual que antes: el service/DAO esperan 'genre_names'
    if genre is not None:
        update_data["genre_names"] = genre

    if canciones_ids is not None:
        update_data["canciones_ids"] = canciones_ids

    if artista_emails is not None:
        update_data["artista_emails"] = artista_emails

    # Nueva portada opcional
    if portada is not None and portada.filename:
        # mismo comportamiento que en album_upload.py
        portada_path = save_upload(portada, "img")  # devuelve "uploads/img/xxx.jpg"
        update_data["imgPortada"] = portada_path

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionó ningún campo a actualizar",
        )

    updated_album = album_service.update_album(album_id, update_data=update_data)
    if updated_album is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Álbum con id={album_id} no encontrado",
        )
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
