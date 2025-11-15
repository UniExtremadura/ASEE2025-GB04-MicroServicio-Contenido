# app/factories/purchase.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.dao.purchase_dao import PurchaseDAO

def get_purchase_dao(db: Session = Depends(get_db)) -> PurchaseDAO:
    return PurchaseDAO(db)

