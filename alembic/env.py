# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# --- Carga tu Base y settings del proyecto ---
# OJO: no llamamos a nada al importar; solo definimos funciones.

# importa dinámicamente TODOS los submódulos de app.models
import importlib, pkgutil
import app.models as models_pkg
try:
    from app.db import Base  # tu declarative_base()

    # # importa todos los modelos para poblar Base.metadata
    # # ajusta los nombres a los ficheros reales que tengas en app/models
    # from app.models import (
    #     song,              # crea tabla 'cancion'
    #     album,             # 'album'
    #     artista,           # 'artista'
    #     associations,
    #     rating,
    # )
except Exception as e:
    raise RuntimeError(f"No se pudo importar app.db.Base: {e}")


def load_all_models():
    for _, modname, ispkg in pkgutil.iter_modules(models_pkg.__path__):
        importlib.import_module(f"{models_pkg.__name__}.{modname}")


# settings puede no tener exactamente 'DATABASE_URL'; hacemos fallback
def _get_db_url() -> str:
    # 1) intenta leer de app.config.settings con varios nombres
    try:
        from app.config import settings  # tu Settings
        for key in ("DATABASE_URL", "database_url", "db_url"):
            v = getattr(settings, key, None)
            if v:
                return str(v)
    except Exception:
        pass
    # 2) fallback a variable de entorno
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    raise RuntimeError(
        "No se encontró la URL de BD. Define DATABASE_URL en .env "
            "o asegúrate de que app.config.settings exponga DATABASE_URL/database_url/db_url."
    )

# Config Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)



load_all_models()

# MUY IMPORTANTE: apuntar a tu metadata
target_metadata = Base.metadata

def run_migrations_offline():
    url = _get_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = _get_db_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

# 👇 NO LLAMES A NADA AQUÍ; Alembic decidirá el modo:
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

