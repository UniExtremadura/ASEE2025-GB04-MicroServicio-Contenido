# app/api/routes/comentarios.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.comment import CommentCreate, CommentOut
from app.dao.comment_dao import CommentDAO
from app.factories.comment import get_comment_dao
from app.services import auth_proxy as auth

router = APIRouter(tags=["comentarios"])

def _get_user_email(identity: dict) -> str:
    user_data = identity.get("user_data") or {}
    email = user_data.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Usuario no identificado o token inválido"
        )
    return email

# -----------------------------------------------------------------------------
# COMENTARIOS EN CANCIONES
# -----------------------------------------------------------------------------

@router.get(
    "/canciones/{song_id}/comentarios", 
    response_model=List[CommentOut],
    summary="Listar comentarios de una canción"
)
def listar_comentarios_cancion(
    song_id: int,
    comment_dao: CommentDAO = Depends(get_comment_dao)
):
    return comment_dao.get_by_song(song_id)


@router.post(
    "/canciones/{song_id}/comentarios", 
    response_model=CommentOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Añadir comentario a una canción"
)
def comentar_cancion(
    song_id: int,
    payload: CommentCreate,
    comment_dao: CommentDAO = Depends(get_comment_dao),
    identity: dict = Depends(auth.get_current_identity),
):
    email = _get_user_email(identity)

    try:
        return comment_dao.create(
            user_ref=email,
            content=payload.content,
            song_id=song_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo crear el comentario: {str(e)}")



@router.get(
    "/albumes/{album_id}/comentarios", 
    response_model=List[CommentOut],
    summary="Listar comentarios de un álbum"
)
def listar_comentarios_album(
    album_id: int,
    comment_dao: CommentDAO = Depends(get_comment_dao)
):
    return comment_dao.get_by_album(album_id)


@router.post(
    "/albumes/{album_id}/comentarios", 
    response_model=CommentOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Añadir comentario a un álbum"
)
def comentar_album(
    album_id: int,
    payload: CommentCreate,
    comment_dao: CommentDAO = Depends(get_comment_dao),
    identity: dict = Depends(auth.get_current_identity),
):
    email = _get_user_email(identity)

    try:
        return comment_dao.create(
            user_ref=email,
            content=payload.content,
            album_id=album_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo crear el comentario: {str(e)}")
