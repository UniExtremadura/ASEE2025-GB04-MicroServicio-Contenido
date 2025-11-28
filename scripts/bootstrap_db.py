# scripts/bootstrap_db.py
from app.db import engine, Base
import app.models  # noqa

Base.metadata.create_all(bind=engine)
print("Tablas creadas si faltaban ✅")

