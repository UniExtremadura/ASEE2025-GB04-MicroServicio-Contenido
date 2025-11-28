"""sync models

Revision ID: 07ed021c069e
Revises: aa10122d386e
Create Date: 2025-11-04 23:44:49.143850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# intenta copiar desde "nombreArtistico" si existe (columna CamelCase => hay que citar)
from sqlalchemy import exc as sa_exc


# revision identifiers, used by Alembic.
revision: str = '07ed021c069e'
down_revision: Union[str, None] = 'aa10122d386e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0) ARTISTA: asegurar columna id y rellenar
    #    (si ya existe, el try/except la deja tal cual)
    try:
        op.add_column("artista", sa.Column("id", sa.Integer(), nullable=True))
    except Exception:
        pass

    # secuencia tipo SERIAL y backfill
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'artista_id_seq') THEN
            CREATE SEQUENCE artista_id_seq OWNED BY artista.id;
        END IF;
    END$$;
    """)
    op.execute("ALTER TABLE artista ALTER COLUMN id SET DEFAULT nextval('artista_id_seq');")
    op.execute("UPDATE artista SET id = nextval('artista_id_seq') WHERE id IS NULL;")
    op.execute("ALTER TABLE artista ALTER COLUMN id SET NOT NULL;")
    # soltar FKs antiguas que apuntan a artista(email), si existen
    for t, fk in [
        ("album_artista", "album_artista_email_artista_fkey"),
        ("cancion_artista", "cancion_artista_email_artista_fkey"),
    ]:
        try:
            op.drop_constraint(fk, t, type_="foreignkey")
        except Exception:
            pass

    # hacer 'id' la clave primaria de 'artista'
    op.execute("""
    DO $$
    DECLARE
        pk_name text;
    BEGIN
        SELECT conname INTO pk_name
        FROM pg_constraint
        WHERE conrelid = 'artista'::regclass AND contype = 'p';
        IF pk_name IS NOT NULL THEN
            -- 👇 CASCADE para soltar dependencias (si quedara alguna)
            EXECUTE format('ALTER TABLE artista DROP CONSTRAINT %I CASCADE', pk_name);
        END IF;
        EXECUTE 'ALTER TABLE artista ADD CONSTRAINT artista_pkey PRIMARY KEY (id)';
    END$$;
    """)


    # nombre: añadir como NULL, copiar y luego NOT NULL
    try:
        op.add_column("artista", sa.Column("nombre", sa.String(length=255), nullable=True))
    except Exception:
        pass
    # si existía nombreArtistico, úsalo; si no, usa email
    try:
        op.execute('UPDATE artista SET nombre = COALESCE(nombre, "nombreArtistico");')
    except sa_exc.ProgrammingError:
        # la columna no existe en este entorno, seguimos
        pass

    # backup: rellena con email si sigue a NULL
    op.execute("UPDATE artista SET nombre = email WHERE nombre IS NULL;")
    op.execute("ALTER TABLE artista ALTER COLUMN nombre SET NOT NULL;")

    # unique en email (si ya existe, ignora)
    try:
        op.create_unique_constraint("uq_artista_email", "artista", ["email"])
    except Exception:
        pass

    # elimina columnas antiguas si existen
    for col in ("bio", "nombreArtistico", "redesSociales", "imagenPerfil"):
        try:
            op.execute(f'ALTER TABLE artista DROP COLUMN IF EXISTS "{col}" CASCADE')
        except Exception:
            pass

    # 1) ALBUM_ARTISTA: nueva FK por id (nullable -> copiar -> not null -> FK -> drop vieja)
    op.add_column("album_artista", sa.Column("artista_id", sa.Integer(), nullable=True))
    op.execute("""
        UPDATE album_artista aa
        SET artista_id = a.id
        FROM artista a
        WHERE aa.email_artista = a.email
    """)
    op.execute("ALTER TABLE album_artista ALTER COLUMN artista_id SET NOT NULL;")
    # borra la antigua FK si existe y crea la nueva
    try:
        op.drop_constraint("album_artista_email_artista_fkey", "album_artista", type_="foreignkey")
    except Exception:
        pass
    op.create_foreign_key(
        "fk_album_artista_artista_id",
        "album_artista", "artista",
        ["artista_id"], ["id"]
    )
    op.execute('ALTER TABLE album_artista DROP COLUMN IF EXISTS "email_artista" CASCADE')

    # 2) CANCION_ARTISTA: igual
    op.add_column("cancion_artista", sa.Column("artista_id", sa.Integer(), nullable=True))
    op.execute("""
        UPDATE cancion_artista ca
        SET artista_id = a.id
        FROM artista a
        WHERE ca.email_artista = a.email
    """)
    op.execute("ALTER TABLE cancion_artista ALTER COLUMN artista_id SET NOT NULL;")
    try:
        op.drop_constraint("cancion_artista_email_artista_fkey", "cancion_artista", type_="foreignkey")
    except Exception:
        pass
    op.create_foreign_key(
        "fk_cancion_artista_artista_id",
        "cancion_artista", "artista",
        ["artista_id"], ["id"]
    )
    op.execute('ALTER TABLE cancion_artista DROP COLUMN IF EXISTS "email_artista" CASCADE')

    # 3) CANCION: poner a 0 nulos antes de NOT NULL
    op.execute("UPDATE cancion SET precio = 0 WHERE precio IS NULL;")
    op.execute('UPDATE cancion SET "numVisualizaciones" = 0 WHERE "numVisualizaciones" IS NULL;')
    op.execute('UPDATE cancion SET "numIngresos" = 0 WHERE "numIngresos" IS NULL;')
    op.execute('UPDATE cancion SET "numLikes" = 0 WHERE "numLikes" IS NULL;')
    # ahora sí, NOT NULL
    op.execute("ALTER TABLE cancion ALTER COLUMN precio SET NOT NULL;")
    op.execute('ALTER TABLE cancion ALTER COLUMN "numVisualizaciones" SET NOT NULL;')
    op.execute('ALTER TABLE cancion ALTER COLUMN "numIngresos" SET NOT NULL;')
    op.execute('ALTER TABLE cancion ALTER COLUMN "numLikes" SET NOT NULL;')

    # 4) PLAYLIST: migrar nomPlaylist -> nombre
    try:
        op.add_column("playlist", sa.Column("nombre", sa.String(length=255), nullable=True))
    except Exception:
        pass
    try:
        op.add_column("playlist", sa.Column("descripcion", sa.Text(), nullable=True))
    except Exception:
        pass
    op.execute("UPDATE playlist SET nombre = COALESCE(nombre, nomPlaylist);")
    op.execute("UPDATE playlist SET nombre = COALESCE(nombre, 'Sin título');")
    op.execute("ALTER TABLE playlist ALTER COLUMN nombre SET NOT NULL;")
    # eliminar columnas antiguas si existen
    for col in ("numVisualizaciones", "emailUser", "nomPlaylist", "imgPortada"):
        try:
            op.execute(f'ALTER TABLE playlist DROP COLUMN IF EXISTS "{col}" CASCADE')
        except Exception:
            pass

    # 5) VALORACION: si quieres quitar fechaValoracion
    try:
        op.execute('ALTER TABLE valoracion DROP COLUMN IF EXISTS "fechaValoracion"')
    except Exception:
        pass

def downgrade() -> None:
    pass
