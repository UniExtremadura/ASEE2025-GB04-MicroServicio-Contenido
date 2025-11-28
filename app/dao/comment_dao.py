# app/dao/comment_dao.py
from typing import List
from sqlalchemy.orm import Session
from app.models.comment import Comment

class CommentDAO:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, 
        *, 
        user_ref: str, 
        content: str, 
        song_id: int | None = None, 
        album_id: int | None = None
    ) -> Comment:
        comment = Comment(
            user_ref=user_ref,
            content=content,
            cancion_id=song_id, # Nota: en el modelo lo llamamos cancion_id
            album_id=album_id
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_by_song(self, song_id: int) -> List[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.cancion_id == song_id)
            .order_by(Comment.created_at.desc())
            .all()
        )

    def get_by_album(self, album_id: int) -> List[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.album_id == album_id)
            .order_by(Comment.created_at.desc())
            .all()
        )
