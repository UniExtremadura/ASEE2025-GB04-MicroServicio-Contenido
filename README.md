# Microservicio de Contenidos (FastAPI + PostgreSQL)

API del microservicio **contenidos** hecha con **FastAPI**, **SQLAlchemy** y **PostgreSQL**.  
Sirve canciones y ficheros estáticos (mp3/imágenes).

---

## Requisitos

- **Python 3.11+** (recomendado venv)
- **PostgreSQL 14+**

## Para lanzar la API se recomienda el uso del Makefile

```bash
# Ubuntu
sudo apt update
sudo apt install -y python3 python3-venv python3-pip \
postgresql postgresql-contrib \
libpq-dev build-essential


# Instalar en venv

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


```
