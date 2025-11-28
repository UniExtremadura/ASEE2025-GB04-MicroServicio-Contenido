# app/factories/comment.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.dao.comment_dao import CommentDAO

def get_comment_dao(db: Session = Depends(get_db)) -> CommentDAO:
    return CommentDAO(db)
