from __future__ import annotations

import inspect
from datetime import date as Date
from pathlib import Path
from typing import List, Optional
from sqlalchemy import select

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from sqlalchemy import func
from app.db import get_db
from app.dao.album_dao import AlbumDAO
from app.factories.album import get_album_dao
from app.schemas.album import AlbumOut
from app.services import storage
from app import config

from app.models.genre import Genre

router = APIRouter(tags=["albumes"])


def _validate_upload(
    upload: UploadFile | None,
    allowed_exts: set[str],
    max_mb: int,
    kind: str,
    expected_mime_prefix: str,
) -> None:
    """Valida extensión, content-type y tamaño aprox. del archivo subido."""
    if upload is None:
        return
    ext = Path(upload.filename or "").suffix.lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{kind}: extensión no permitida ({ext}). Permitidas: {sorted(allowed_exts)}",
        )
    ctype = (upload.content_type or "").lower()
    if not ctype.startswith(expected_mime_prefix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{kind}: content-type inválido ({ctype}).",
        )
    # Estimar tamaño leyendo el spooled file
    f = upload.file
    try:
        pos = f.tell()
    except Exception:
        pos = 0
    try:
        f.seek(0, 2)  # EOF
        size_bytes = f.tell()
    finally:
        try:
            f.seek(pos, 0)
        except Exception:
            pass
    max_bytes = max_mb * 1024 * 1024
    if size_bytes and size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"{kind}: tamaño {size_bytes // (1024*1024)}MB supera {max_mb}MB.",
        )


async def _save_maybe_async(func, *args, **kwargs) -> str:
    """Compatibilidad: si storage.save_upload es async o sync."""
    res = func(*args, **kwargs)
    if inspect.isawaitable(res):
        return await res
    return res


@router.post(
    "/albumes/upload",
    response_model=AlbumOut,
    status_code=status.HTTP_201_CREATED,
    summary="Subida de álbum ",
)
async def upload_album(
    titulo: str = Form(...),
    precio: float = Form(...),
    date: Optional[Date] = Form(None),
    genres: Optional[List[str]] = Form(None),  # lista de géneros
    artistas_emails: Optional[List[str]] = Form(None),
    canciones_ids: Optional[List[str]] = Form(None),    
    
    portada: Optional[UploadFile] = File(None),

    db: Session = Depends(get_db),
    album_dao: AlbumDAO = Depends(get_album_dao),
):
    # Correcto funcionamiento de añadir canciones desde el formulario
    canciones_list: List[int] = []
    if canciones_ids:
        print(f"DEBUG RAW - canciones_ids type: {type(canciones_ids)}, value: {canciones_ids}, len: {len(canciones_ids)}")
        try:
            # If it's a list with one element containing commas, split it
            if len(canciones_ids) == 1 and ',' in str(canciones_ids[0]):
                print(f"DEBUG - Detected comma-separated format: {canciones_ids[0]}")
                canciones_list = [
                    int(id_str.strip()) 
                    for id_str in str(canciones_ids[0]).split(',') 
                    if id_str.strip()
                ]
            else:
                # Multiple form fields (already a proper list)
                print(f"DEBUG - Detected multiple field format: {canciones_ids}")
                canciones_list = [int(str(id_str).strip()) for id_str in canciones_ids if str(id_str).strip()]
            print(f"DEBUG - Parsed canciones_list: {canciones_list}")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid canciones_ids format. All IDs must be integers. Error: {str(e)}"
            )
        # —— validar nombres de géneros ——
        genre_names = []
    if genres:
        # Si viene una lista con un solo elemento y contiene comas, dividir
        if len(genres) == 1 and "," in genres[0]:
            genre_names = [g.strip() for g in genres[0].split(",")]
        else:
            genre_names = [g.strip() for g in genres]

    # elimina duplicados, normaliza
    genre_names = [g.strip() for g in genre_names if g and g.strip()]
    unique_lower = {g.lower() for g in genre_names}

    # 1) Validación del archivo de portada
    if portada is not None:
        _validate_upload(portada, config.ALLOWED_IMAGE_EXTS, config.MAX_IMAGE_MB, "portada", "image/")

    # 2) Guardado de portada en disco
    portada_path = None
    if portada:
        portada_path = await _save_maybe_async(storage.save_upload, portada, subdir="img")
    # 3) Procesar lista de artistas
    artistas_list = []
    if artistas_emails:
        # Manejar tanto lista como string separado por comas
        if len(artistas_emails) == 1 and ',' in artistas_emails[0]:
            artistas_list = [email.strip() for email in artistas_emails[0].split(',')]
        else:
            artistas_list = [email.strip() for email in artistas_emails]
        artistas_list = [email for email in artistas_list if email]  # Filtrar vacíos
    # 4) Persistencia (el DAO solo escribe en su BD)
    album = album_dao.create(
        titulo=titulo,
        imgPortada=portada_path,
        genre_names=genre_names,
        precio=precio,
        date=date,
        artista_emails=artistas_list,
        canciones_ids=canciones_list,
    )

    return album