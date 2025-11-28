# app/factories/purchase.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.dao.purchase_dao import PurchaseDAO
from app.dao.album_purchase_dao import AlbumPurchaseDAO

def get_purchase_dao(db: Session = Depends(get_db)) -> PurchaseDAO:
    return PurchaseDAO(db)

def get_album_purchase_dao(db: Session = Depends(get_db)) -> AlbumPurchaseDAO:
    return AlbumPurchaseDAO(db)
