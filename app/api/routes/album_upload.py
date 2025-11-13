# app/api/routes/album_upload.py
from __future__ import annotations

from datetime import date as Date
from typing import List, Optional

from fastapi import (
    APIRouter, Depends, File, Form, HTTPException, UploadFile, status
)

from app.schemas.album import AlbumOut
from app.factories import get_album_dao, get_song_dao
from app.dao.album_dao import AlbumDAO
from app.dao.song_dao import SongDAO
from app.services.storage import save_upload
from app.services import auth_proxy as auth  # usa get_current_identity()

router = APIRouter(tags=["albumes"])


def _parse_canciones_ids(canciones_ids: Optional[List[str]]) -> List[int]:
    """Acepta campos repetidos o un único CSV, devuelve lista de enteros."""
    if not canciones_ids:
        return []
    try:
        if len(canciones_ids) == 1 and "," in str(canciones_ids[0]):
            return [int(x.strip()) for x in str(canciones_ids[0]).split(",") if x.strip()]
        return [int(str(x).strip()) for x in canciones_ids if str(x).strip()]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid canciones_ids format. All IDs must be integers. Error: {str(e)}",
        )


@router.post(
    "/albumes",
    response_model=AlbumOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear álbum (requiere artista autenticado)",
)
async def upload_album(
    # form-data
    titulo: str = Form(..., description="Título del álbum"),
    precio: float = Form(..., description="Precio del álbum"),
    date: Optional[Date] = Form(None, description="Fecha del álbum (YYYY-MM-DD)"),
    canciones_ids: Optional[List[str]] = Form(None, description="IDs de canciones (repetidos o CSV)"),
    portada: Optional[UploadFile] = File(None, description="Imagen de portada"),
    # auth (tu proxy es ASYNC y devuelve {user_type, user_data:{email}})
    identity: dict = Depends(auth.get_current_identity),
    # daos
    album_dao: AlbumDAO = Depends(get_album_dao),
    song_dao: SongDAO = Depends(get_song_dao),
):
    # 1) Solo ARTISTAS
    if identity.get("user_type") != "artist":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo artistas pueden crear álbumes")
    artist_email = (identity.get("user_data") or {}).get("email")
    if not artist_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sin email de usuario")

    # 2) Parsear y validar existencia de canciones en una sola query
    ids = _parse_canciones_ids(canciones_ids)
    songs = song_dao.get_many(ids)  # precarga relaciones
    found_ids = {s.id for s in songs}
    missing = [i for i in ids if i not in found_ids]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Las siguientes canciones no existen: {missing}",
        )

    # 3) Validar PROPIEDAD: todas las canciones deben pertenecer al artista del token
    no_propias = []
    for s in songs:
        # tu relación real es 'artistas_refs' con campo 'artista_email'
        owner_emails = {ref.artista_email for ref in (s.artistas_refs or [])}
        if artist_email not in owner_emails:
            no_propias.append(s.id)
    if no_propias:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No puedes incluir canciones que no son tuyas: {no_propias}",
        )

    # 4) Guardar portada (si viene)
    portada_path: Optional[str] = None
    if portada:
        portada_path = save_upload("img", portada)  # devuelve "uploads/img/xxx.jpg"

    # 5) Crear álbum (tu DAO espera 'titulo' y 'artista_emails')
    album = album_dao.create(
        titulo=titulo,
        imgPortada=portada_path,
        precio=precio,
        date=date,
        canciones_ids=ids,
        artista_emails=[artist_email],  # <- solo el del token
    )
    return album

